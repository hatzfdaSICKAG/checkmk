#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.cisco_ucs import DETECT
from cmk.base.check_legacy_includes.temperature import check_temperature
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

# comNET GmbH, Fabian Binder - 2018-05-30

# .1.3.6.1.4.1.9.9.719.1.9.44.1.4  cucsComputeRackUnitMbTempStatsAmbientTemp
# .1.3.6.1.4.1.9.9.719.1.9.44.1.8  cucsComputeRackUnitMbTempStatsFrontTemp
# .1.3.6.1.4.1.9.9.719.1.9.44.1.13 cucsComputeRackUnitMbTempStatsIoh1Temp
# .1.3.6.1.4.1.9.9.719.1.9.44.1.21 cucsComputeRackUnitMbTempStatsRearTemp

factory_settings["cisco_ucs_temp_env_default_levels"] = {"levels": (30.0, 35.0)}


def parse_cisco_ucs_temp_env(info):
    new_info = {
        "Ambient": info[0][0],
        "Front": info[0][1],
        "IO-Hub": info[0][2],
        "Rear": info[0][3],
    }
    return new_info


def inventory_cisco_ucs_temp_env(info):
    for name, _temp in info.items():
        yield name, {}


def check_cisco_ucs_temp_env(item, params, info):
    for name, temp in info.items():
        if item == name:
            yield check_temperature(int(temp), params, "cisco_ucs_temp_env_%s" % name)


check_info["cisco_ucs_temp_env"] = LegacyCheckDefinition(
    detect=DETECT,
    parse_function=parse_cisco_ucs_temp_env,
    discovery_function=inventory_cisco_ucs_temp_env,
    check_function=check_cisco_ucs_temp_env,
    default_levels_variable="cisco_ucs_temp_env_default_levels",
    service_name="Temperature %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.9.9.719.1.9.44.1",
        oids=["4", "8", "13", "21"],
    ),
    check_ruleset_name="temperature",
    check_default_parameters={"levels": (30.0, 35.0)},
)
