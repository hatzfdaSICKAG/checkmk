#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import equals, LegacyCheckDefinition
from cmk.base.check_legacy_includes.temperature import check_temperature
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

factory_settings["arris_cmts_temp_default_levels"] = {"levels": (40.0, 46.0)}


def inventory_arris_cmts_temp(info):
    for line in info:
        # only devices with not default temperature
        if line[1] != "999":
            yield line[0], {}


def check_arris_cmts_temp(item, params, info):
    for name, temp in info:
        if name == item:
            return check_temperature(int(temp), params, "arris_cmts_temp_%s" % item)

    return 3, "Sensor not found in SNMP data"


check_info["arris_cmts_temp"] = LegacyCheckDefinition(
    detect=equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.4998.2.1"),
    check_function=check_arris_cmts_temp,
    discovery_function=inventory_arris_cmts_temp,
    service_name="Temperature Module %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.4998.1.1.10.1.4.2.1",
        oids=["3", "29"],
    ),
    check_ruleset_name="temperature",
    default_levels_variable="arris_cmts_temp_default_levels",
    check_default_parameters={"levels": (40.0, 46.0)},
)
