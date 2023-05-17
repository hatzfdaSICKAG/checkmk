#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree
from cmk.base.plugins.agent_based.utils.huawei import DETECT_HUAWEI_OSN

# The typical OSN power unit delivers 750 W max


factory_settings["huawei_osn_power_default_levels"] = {
    "levels": (700, 730),
}


def inventory_huawei_osn_power(info):
    for line in info:
        yield (line[0], None)


def check_huawei_osn_power(item, params, info):
    for line in info:
        if item == line[0]:
            state = 0
            reading = int(line[1])
            warn, crit = params["levels"]

            yield 0, "Current reading: %s W" % reading, [("power", reading, warn, crit, 0)]

            if reading >= crit:
                state = 2
            elif reading >= warn:
                state = 1

            if state:
                yield state, "(warn/crit at %s/%s W)" % (warn, crit)


check_info["huawei_osn_power"] = LegacyCheckDefinition(
    detect=DETECT_HUAWEI_OSN,
    discovery_function=inventory_huawei_osn_power,
    check_function=check_huawei_osn_power,
    service_name="Unit %s (Power)",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2011.2.25.4.70.20.20.10.1",
        oids=["1", "2"],
    ),
    default_levels_variable="huawei_osn_power_default_levels",
    check_default_parameters={
        "levels": (700, 730),
    },
)
