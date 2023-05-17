#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition, startswith
from cmk.base.check_legacy_includes.temperature import check_temperature
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

#
# during inventory we are looking for all temperatures available,
# in this example there are two (index 1 & 2):
#
# EES-POWER-MIB::psTemperature1.0 .1.3.6.1.4.1.6302.2.1.2.7.1
# EES-POWER-MIB::psTemperature2.0 .1.3.6.1.4.1.6302.2.1.2.7.2
#
# the mib is the NetSure_ESNA.mib, which we have received from directly
# from a customer, its named "Emerson Energy Systems (EES) Power MIB"

factory_settings["emerson_temp_default"] = {"levels": (40.0, 50.0)}


def inventory_emerson_temp(info):
    # Device appears to mark missing sensors by temperature value -999999
    yield from ((str(nr), {}) for nr, line in enumerate(info) if int(line[0]) >= -273000)


def check_emerson_temp(item, params, info):
    item_index = int(item)
    if item_index >= len(info):
        return None

    if int(info[item_index][0]) < -273000:
        return 3, "Sensor offline"

    temp = float(info[item_index][0]) / 1000.0
    return check_temperature(temp, params, "emerson_temp_%s" % item)


check_info["emerson_temp"] = LegacyCheckDefinition(
    detect=startswith(".1.3.6.1.4.1.6302.2.1.1.1.0", "Emerson Network Power"),
    discovery_function=inventory_emerson_temp,
    check_function=check_emerson_temp,
    service_name="Temperature %s",
    check_ruleset_name="temperature",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.6302.2.1.2",
        oids=["7"],
    ),
    default_levels_variable="emerson_temp_default",
    check_default_parameters={"levels": (40.0, 50.0)},
)
