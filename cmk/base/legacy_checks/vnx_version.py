#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info


def inventory_vnx_version(info):
    return [(None, None)]


def check_vnx_version(item, params, info):
    for line in info:
        yield 0, f"{line[0]}: {line[1]}"


check_info["vnx_version"] = LegacyCheckDefinition(
    service_name="VNX Version",
    discovery_function=inventory_vnx_version,
    check_function=check_vnx_version,
)
