#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import dataclasses
import enum
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    all_of,
    any_of,
    check_levels,
    contains,
    exists,
    get_value_store,
    OIDCached,
    OIDEnd,
    register,
    Result,
    Service,
    SNMPTree,
    State,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)
from cmk.base.plugins.agent_based.utils.cisco_sensor_item import cisco_sensor_item
from cmk.base.plugins.agent_based.utils.temperature import check_temperature, TempParamDict

Section = Mapping[str, Mapping[str, Mapping[str, Any]]]  # oh boy.


_Levels = tuple[float, float] | None


# NOTE: Devices of type 3850 with firmware versions 3.2.0SE, 3.2.1, 3.2.2
# have been observed to display a tenth of the actual temperature value.
# A firmware update on the device fixes this.

# NOTE: But, in 2020/2021:
# Wrong values for transceivers (DOM) in C9500-24Y4C and C9500-48Y4C CSCvt16172
# The bug link: https://bst.cloudapps.cisco.com/bugsearch/bug/CSCvt16172
#
# See: SUP-4746
#

# OID: ifAdminStatus
_CISCO_TEMPERATURE_ADMIN_STATE_MAP = {
    "1": "up",
    "2": "down",
    "3": "testing",
}


class EntSensorThresholdRelation(enum.IntEnum):
    LESS_THAN = 1
    LESS_OR_EQUAL = 2
    GREATER_THAN = 3
    GREATER_OR_EQUAL = 4
    EQUAL_TO = 5
    NOT_EQUAL_TO = 6


class EntSensorThresholdSeverity(enum.IntEnum):
    OTHER = 1
    MINOR = 10
    MAJOR = 20
    CRITICAL = 30


@dataclasses.dataclass
class EntSensorThreshold:
    severity: EntSensorThresholdSeverity
    relation: EntSensorThresholdRelation
    value: float


def _filter_thresholds_for_relation(
    thresholds: Sequence[EntSensorThreshold],
    filter_comp_op: EntSensorThresholdRelation,
) -> Mapping[EntSensorThresholdSeverity, EntSensorThreshold]:
    return {thresh.severity: thresh for thresh in thresholds if thresh.relation == filter_comp_op}


def _parse_specified_thresholds(
    thresholds: Sequence[EntSensorThreshold],
    specified_relation: Literal[
        EntSensorThresholdRelation.GREATER_OR_EQUAL, EntSensorThresholdRelation.LESS_THAN
    ],
    factor: float,
) -> _Levels:
    filtered_thresholds = _filter_thresholds_for_relation(thresholds, specified_relation)
    # thresholds can be (minor, major, critical), but not all have to be defined
    # WARN <- minor, CRIT <- min(major, critical)
    warn_threshold = filtered_thresholds.get(EntSensorThresholdSeverity.MINOR)
    crit_threshold = filtered_thresholds.get(
        EntSensorThresholdSeverity.MAJOR,
        filtered_thresholds.get(EntSensorThresholdSeverity.CRITICAL),
    )

    match (warn_threshold, crit_threshold):
        case (EntSensorThreshold(value=warn), EntSensorThreshold(value=crit)):
            return warn * factor, crit * factor
        case (None, EntSensorThreshold(value=crit)):
            return crit * factor, crit * factor
        case _:
            return None


def _parse_unspecified_thresholds(
    thresholds: Sequence[EntSensorThreshold], factor: int
) -> tuple[_Levels, _Levels]:
    # Re-introduced (for temp levels, while being active for dBm levels all the time)
    # in the scope of SUP-15518
    # This is essentially guessing. With provided threshold severity "other", we can't know safely
    # what to do with the provided threshold values.
    # However, we interpreted the levels (without even considering the severity at all) as
    # a 4-tuple before, so we should continue doing so to avoid breaking existing installations.
    match sorted([t.value * factor for t in thresholds]):
        # coerce into our levels representation if there are 4 or 2 thresholds.
        case [crit_lower, warn_lower, warn_upper, crit_upper]:
            return (warn_upper, crit_upper), (warn_lower, crit_lower)
        case [warn_upper, crit_upper]:
            return (warn_upper, crit_upper), None
        # No further guessing otherwise
        case _:
            return None, None


def parse_cisco_temperature(  # pylint: disable=too-many-branches
    string_table: list[StringTable],
) -> Section:
    # CISCO-ENTITY-SENSOR-MIB entSensorType
    cisco_sensor_types = {
        "1": "other",
        "2": "unknown",
        "3": "voltsAC",
        "4": "voltsDC",
        "5": "amperes",
        "6": "watts",
        "7": "hertz",
        "8": "celsius",
        "9": "parentRH",
        "10": "rpm",
        "11": "cmm",
        "12": "truthvalue",
        "13": "specialEnum",
        "14": "dBm",
    }

    # CISCO-ENTITY-SENSOR-MIB::entSensorScale
    cisco_entity_exponents = {
        "1": -24,  # yocto
        "2": -21,  # zepto
        "3": -18,  # atto
        "4": -15,  # femto
        "5": -12,  # pico
        "6": -9,  # nano
        "7": -6,  # micro
        "8": -3,  # milli
        "9": 0,  # units
        "10": 3,  # kilo
        "11": 6,  # mega
        "12": 9,  # giga
        "13": 12,  # tera
        "14": 18,  # exa
        "15": 15,  # peta
        "16": 21,  # zetta
        "17": 24,  # yotta
    }

    # CISCO-ENTITY-SENSOR-MIB::entSensorStatus
    map_states = {
        "1": (0, "OK"),
        "2": (3, "unavailable"),
        "3": (2, "non-operational"),
    }

    # CISCO-ENVMON-MIB
    map_envmon_states = {
        "1": (0, "normal"),
        "2": (1, "warning"),
        "3": (2, "critical"),
        "4": (2, "shutdown"),
        "5": (3, "not present"),
        "6": (2, "not functioning"),
    }

    # description_info = [...,
    #                     [u'25955', u'Ethernet1/9(Rx-dBm)'],
    #                     [u'25956', u'Ethernet1/9(Tx-dBm)'],
    #                     ...]
    # state_info = [...,
    #               [u'25955', u'14', u'8', u'0', u'-3487', u'1'],
    #               [u'25956', u'14', u'8', u'0', u'-2525', u'1'],
    #               ...]
    # admin_states = [['Ethernet1/9', '1'], ...]
    #

    # IMPORTANT HINT: Temperature sensors uniquely identified via the indices in
    # description_info and linked to data in state_info are different sensors than
    # the ones contained in the perfstuff data structure. Sensors contained in the
    # perfstuff data structure contain only one threshold value for temperature.
    #
    # description_info = [...,
    #                     [u'1008', u'Switch 1 - WS-C2960X-24PD-L - Sensor 0'],
    #                     ...,
    #                     [u'2008', u'Switch 2 - WS-C2960X-24PD-L - Sensor 0'],
    #                     ...]
    # perfstuff = [...,
    #              [u'1008', u'SW#1, Sensor#1, GREEN', u'36', u'68', u'1'],
    #              [u'2008', u'SW#2, Sensor#1, GREEN', u'37', u'68', u'1'],
    #              ...]

    description_info, state_info, levels_info, perfstuff, admin_states = string_table

    # Create dict of sensor descriptions
    descriptions = dict(description_info)

    # Map admin state of Ethernet ports to sensor_ids of corresponding ethernet port sensors.
    # E.g. Ethernet1/9 -> Ethernet1/9(Rx-dBm), Ethernet1/9(Tx-dBm)
    # In case the description has been modified in the switch device this
    # mapping will not be successful. The description contains an ID instead of
    # a human readable string to identify the sensors then. The sensors cannot
    # be looked up in the description_info then.
    admin_states_dict = {}
    for if_name, admin_state in admin_states:
        for sensor_id, descr in descriptions.items():
            if descr.startswith(if_name):
                admin_states_dict[sensor_id] = _CISCO_TEMPERATURE_ADMIN_STATE_MAP.get(admin_state)

    # Create dict with thresholds
    thresholds: dict[str, list[EntSensorThreshold]] = {}
    for sensor_id, sensortype_id, scalecode, magnitude, value, sensorstate in state_info:
        thresholds.setdefault(sensor_id, [])

    for endoid, severity, relation, thresh_value in levels_info:
        # endoid is e.g. 21549.9 or 21459.10
        sensor_id, _subid = endoid.split(".")
        thresholds.setdefault(sensor_id, []).append(
            EntSensorThreshold(
                severity=EntSensorThresholdSeverity(int(severity)),
                relation=EntSensorThresholdRelation(int(relation)),
                value=float(thresh_value),
            )
        )

    # Parse OIDs described by CISCO-ENTITY-SENSOR-MIB
    entity_parsed: dict[str, dict[str, dict[str, str]]] = {}
    for sensor_id, sensortype_id, scalecode, magnitude, value, sensorstate in state_info:
        sensortype = cisco_sensor_types.get(sensortype_id)
        if sensortype not in ("dBm", "celsius"):
            continue

        if sensor_id in descriptions:
            descr = descriptions[sensor_id]
        else:
            descr = sensor_id

        if not descr:
            continue

        entity_parsed.setdefault(sensortype_id, {})

        sensor_attrs: dict[str, Any] = {
            "descr": descr,
            "raw_dev_state": sensorstate,  # used in discovery function
            "dev_state": map_states.get(sensorstate, (3, f"unknown[{sensorstate}]")),
            "admin_state": admin_states_dict.get(sensor_id),
        }

        dev_levels_lower: _Levels = None
        dev_levels_upper: _Levels = None

        if sensorstate == "1":
            factor = 10.0 ** (float(cisco_entity_exponents[scalecode]) - float(magnitude))
            sensor_attrs["reading"] = float(value) * factor
            if sensortype == "dBm":
                # Don't rely on provided severities and relations at all for dBm.
                # We observed misleading information here.
                dev_levels_upper, dev_levels_lower = _parse_unspecified_thresholds(
                    thresholds[sensor_id], factor
                )

            elif sensortype == "celsius":
                unspecified_thresholds = [
                    thres
                    for thres in thresholds[sensor_id]
                    if thres.severity is EntSensorThresholdSeverity.OTHER
                ]
                specified_thresholds = [
                    thres
                    for thres in thresholds[sensor_id]
                    if thres.severity is not EntSensorThresholdSeverity.OTHER
                ]

                if specified_thresholds:
                    # sensor values can be compared to the thresholds using different operators
                    # (<, <=, >, >=, =, !=))
                    # use the threshold only if the comp operator is the same as check_levels uses
                    dev_levels_upper = _parse_specified_thresholds(
                        thresholds[sensor_id],
                        EntSensorThresholdRelation.GREATER_OR_EQUAL,
                        factor,
                    )
                    dev_levels_lower = _parse_specified_thresholds(
                        thresholds[sensor_id],
                        EntSensorThresholdRelation.LESS_THAN,
                        factor,
                    )

                elif unspecified_thresholds:
                    dev_levels_upper, dev_levels_lower = _parse_unspecified_thresholds(
                        unspecified_thresholds, factor
                    )

            sensor_attrs["dev_levels_lower"] = dev_levels_lower
            sensor_attrs["dev_levels_upper"] = dev_levels_upper
            entity_parsed[sensortype_id].setdefault(sensor_id, sensor_attrs)
        elif sensorstate in ["2", "3"]:
            entity_parsed[sensortype_id].setdefault(sensor_id, sensor_attrs)

    temp_sensor_type = "8"
    parsed: dict[str, dict[str, dict[str, Any]]] = {temp_sensor_type: {}}

    for sensor_id, statustext, temp, max_temp, state in perfstuff:
        if sensor_id in descriptions and sensor_id in entity_parsed.get(temp_sensor_type, {}):
            # if this sensor is already in the dictionary, ensure we use the same name
            item = descriptions[sensor_id]
            prev_description = cisco_sensor_item(statustext, sensor_id)
            # also register the name we would have used up to 1.2.8b4, so we can give
            # the user a proper info message.
            # It's the little things that show you care
            parsed[temp_sensor_type][prev_description] = {"obsolete": True}
        else:
            item = cisco_sensor_item(statustext, sensor_id)

        temp_sensor_attrs: dict[str, Any] = {
            "raw_env_mon_state": state,
            "dev_state": map_envmon_states.get(state, (3, f"unknown[{state}]")),
        }

        try:
            temp_sensor_attrs["reading"] = int(temp)

            attrs = entity_parsed.get(temp_sensor_type, {}).get(sensor_id, {})
            if levels_upper := attrs.get("dev_levels_upper"):
                temp_sensor_attrs["dev_levels_upper"] = levels_upper
            elif max_temp and int(max_temp):
                temp_sensor_attrs["dev_levels_upper"] = int(max_temp), int(max_temp)
            else:
                temp_sensor_attrs["dev_levels_upper"] = None
            temp_sensor_attrs["dev_levels_lower"] = attrs.get("dev_levels_lower", None)

        except Exception:
            temp_sensor_attrs["dev_state"] = (3, "sensor defect")

        parsed[temp_sensor_type].setdefault(item, temp_sensor_attrs)

    for sensor_type, sensors in entity_parsed.items():
        for sensor_attrs in sensors.values():
            # Do not overwrite found sensors from perfstuff loop
            parsed.setdefault(sensor_type, {}).setdefault(sensor_attrs["descr"], sensor_attrs)

    return parsed


register.snmp_section(
    name="cisco_temperature",
    parse_function=parse_cisco_temperature,
    detect=all_of(
        contains(".1.3.6.1.2.1.1.1.0", "cisco"),
        any_of(
            exists(".1.3.6.1.4.1.9.9.91.1.1.1.1.*"),
            exists(".1.3.6.1.4.1.9.9.13.1.3.1.3.*"),
        ),
    ),
    fetch=[
        # cisco_temp_sensor data
        SNMPTree(
            base=".1.3.6.1.2.1.47.1.1.1.1",
            oids=[
                OIDEnd(),
                OIDCached("7"),  # Name of the sensor
            ],
        ),
        # Type and current state
        SNMPTree(
            base=".1.3.6.1.4.1.9.9.91.1.1.1.1",
            oids=[
                OIDEnd(),
                "1",  # CISCO-ENTITY-SENSOR-MIB::entSensorType
                "2",  # CISCO-ENTITY-SENSOR-MIB::entSensorScale
                "3",  # CISCO-ENTITY-SENSOR-MIB::entSensorPrecision
                "4",  # CISCO-ENTITY-SENSOR-MIB::entSensorValue
                "5",  # CISCO-ENTITY-SENSOR-MIB::entSensorStatus
            ],
        ),
        # Threshold
        SNMPTree(
            base=".1.3.6.1.4.1.9.9.91.1.2.1.1",
            oids=[
                OIDEnd(),
                "2",  # entSensorThresholdSeverity
                "3",  # entSensorThresholdRelation
                "4",  # entSensorThresholdValue
            ],
        ),
        # cisco_temp_perf data
        SNMPTree(
            base=".1.3.6.1.4.1.9.9.13.1.3.1",
            oids=[  # CISCO-SMI
                OIDEnd(),
                "2",  # ciscoEnvMonTemperatureStatusDescr
                "3",  # ciscoEnvMonTemperatureStatusValue
                "4",  # ciscoEnvMonTemperatureThreshold
                "6",  # ciscoEnvMonTemperatureState
            ],
        ),
        SNMPTree(
            base=".1.3.6.1.2.1.2.2.1",
            oids=[
                OIDCached("2"),  # Description of the sensor
                OIDCached("7"),  # ifAdminStatus
            ],
        ),
    ],
)


#   .--temperature---------------------------------------------------------.
#   |      _                                      _                        |
#   |     | |_ ___ _ __ ___  _ __   ___ _ __ __ _| |_ _   _ _ __ ___       |
#   |     | __/ _ \ '_ ` _ \| '_ \ / _ \ '__/ _` | __| | | | '__/ _ \      |
#   |     | ||  __/ | | | | | |_) |  __/ | | (_| | |_| |_| | | |  __/      |
#   |      \__\___|_| |_| |_| .__/ \___|_|  \__,_|\__|\__,_|_|  \___|      |
#   |                       |_|                                            |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'


def discover_cisco_temperature(section: Section) -> DiscoveryResult:
    discoverable_sensor_state = ["1", "2", "3", "4"]  # normal, warning, critical, shutdown
    for item, value in section.get("8", {}).items():
        if value.get("obsolete", False):
            continue
        if env_mon_state := value.get("raw_env_mon_state"):
            if env_mon_state not in discoverable_sensor_state:
                continue
        elif value.get("raw_dev_state") != "1":
            continue

        yield Service(item=item)


def check_cisco_temperature(item: str, params: TempParamDict, section: Section) -> CheckResult:
    temp_parsed = section.get("8", {})
    if item not in temp_parsed:
        return

    data = temp_parsed[item]
    if data.get("obsolete", False):
        yield Result(state=State.UNKNOWN, summary="This sensor is obsolete, please rediscover")
        return

    state, state_readable = data["dev_state"]
    reading = data.get("reading")
    if reading is None:
        yield Result(state=State(state), summary="Status: %s" % state_readable)
        return

    yield from check_temperature(
        reading,
        params,
        unique_name="cisco_temperature_%s" % item,
        value_store=get_value_store(),
        dev_levels=data.get("dev_levels_upper", None),
        dev_levels_lower=data.get("dev_levels_lower", None),
        dev_status=state,
        dev_status_name=state_readable,
    )


register.check_plugin(
    name="cisco_temperature",
    service_name="Temperature %s",
    discovery_function=discover_cisco_temperature,
    check_function=check_cisco_temperature,
    check_ruleset_name="temperature",
    check_default_parameters={},  # is this OK?
)

# .
#   .--dom-----------------------------------------------------------------.
#   |                            _                                         |
#   |                         __| | ___  _ __ ___                          |
#   |                        / _` |/ _ \| '_ ` _ \                         |
#   |                       | (_| | (_) | | | | | |                        |
#   |                        \__,_|\___/|_| |_| |_|                        |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   | digital optical monitoring                                           |
#   '----------------------------------------------------------------------'


def discover_cisco_temperature_dom(params: Mapping[str, Any], section: Section) -> DiscoveryResult:
    parsed_dom = section.get("14", {})
    admin_states_to_discover = {
        _CISCO_TEMPERATURE_ADMIN_STATE_MAP[admin_state]
        for admin_state in params.get("admin_states", ["1"])
    } | {None}
    for item, attrs in parsed_dom.items():
        dev_state = attrs.get("raw_dev_state")
        adm_state = attrs.get("admin_state")
        if dev_state == "1" and adm_state in admin_states_to_discover:
            yield Service(item=item)


def _determine_levels(
    user_levels: tuple[float, float] | bool,
    device_levels: tuple[float, float] | tuple[None, None],
) -> _Levels:
    if isinstance(user_levels, tuple):
        return user_levels
    if user_levels:
        if device_levels[0] is None or device_levels[1] is None:
            return None
        return device_levels
    return None


def check_cisco_temperature_dom(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    # TODO perf, precision, severity, etc.

    data = section.get("14", {}).get(item, {})

    state, state_readable = data.get("dev_state", (None, None))
    if state is None:
        return
    yield Result(state=State(state), summary="Status: %s" % state_readable)

    reading = data.get("reading")
    if reading is None:
        return

    # get won't save you, because 'dev_levels' may be present, but None.
    dev_levels_lower = data.get("dev_levels_lower") or (None, None)
    dev_levels_upper = data.get("dev_levels_upper") or (None, None)

    if "Transmit" in data["descr"]:
        dsname = "output_signal_power_dbm"
    elif "Receive" in data["descr"]:
        dsname = "input_signal_power_dbm"
    else:
        # in rare case of sensor id instead of sensor description no destinction
        # between transmit/receive possible
        dsname = "signal_power_dbm"
    yield from check_levels(
        reading,
        metric_name=dsname,
        # Map WATO configuration of levels to check_levels() compatible tuple.
        # Default value in case of missing WATO config is use device levels.
        levels_lower=_determine_levels(params.get("power_levels_lower", True), dev_levels_lower),
        levels_upper=_determine_levels(params.get("power_levels_upper", True), dev_levels_upper),
        render_func=lambda f: "%.2f dBm" % f,
        label="Signal power",
    )


register.check_plugin(
    name="cisco_temperature_dom",
    service_name="DOM %s",
    sections=["cisco_temperature"],
    discovery_function=discover_cisco_temperature_dom,
    discovery_default_parameters={"admin_states": ["1"]},
    discovery_ruleset_name="discovery_cisco_dom_rules",
    check_function=check_cisco_temperature_dom,
    check_ruleset_name="cisco_dom",
    check_default_parameters={},
)
