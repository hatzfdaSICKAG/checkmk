#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


import time

import cmk.base.plugins.agent_based.utils.pulse_secure as pulse_secure
from cmk.base.check_api import discover_single, LegacyCheckDefinition
from cmk.base.check_legacy_includes.cpu_util import check_cpu_util
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

factory_settings["pulse_secure_cpu_util_def_levels"] = {"util": (80.0, 90.0)}

KEY_PULSE_SECURE_CPU = "cpu_util"


def check_pulse_secure_cpu(item, params, parsed):
    if not parsed:
        return None

    return check_cpu_util(parsed[KEY_PULSE_SECURE_CPU], params, this_time=time.time())


check_info["pulse_secure_cpu_util"] = LegacyCheckDefinition(
    detect=pulse_secure.DETECT_PULSE_SECURE,
    parse_function=lambda info: pulse_secure.parse_pulse_secure(info, KEY_PULSE_SECURE_CPU),
    discovery_function=discover_single,
    check_function=check_pulse_secure_cpu,
    service_name="Pulse Secure IVE CPU utilization",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.12532",
        oids=["10"],
    ),
    check_ruleset_name="cpu_utilization",
    default_levels_variable="pulse_secure_cpu_util_def_levels",
    check_default_parameters={"util": (80.0, 90.0)},
)
