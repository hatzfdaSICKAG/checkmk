#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Callable
from typing import Any, Type

from cmk.base.check_api import (
    discover,
    get_bytes_human_readable,
    get_parsed_item_data,
    LegacyCheckDefinition,
)
from cmk.base.check_legacy_includes.aws import AWSLimitsByRegion, check_aws_limits, parse_aws
from cmk.base.config import check_info, factory_settings

factory_settings["aws_rds_limits_default_levels"] = {
    "db_instances": (None, 80.0, 90.0),
    "reserved_db_instances": (None, 80.0, 90.0),
    "allocated_storage": (None, 80.0, 90.0),
    "db_security_groups": (None, 80.0, 90.0),
    "auths_per_db_security_groups": (None, 80.0, 90.0),
    "db_parameter_groups": (None, 80.0, 90.0),
    "manual_snapshots": (None, 80.0, 90.0),
    "event_subscriptions": (None, 80.0, 90.0),
    "db_subnet_groups": (None, 80.0, 90.0),
    "option_groups": (None, 80.0, 90.0),
    "subnet_per_db_subnet_groups": (None, 80.0, 90.0),
    "read_replica_per_master": (None, 80.0, 90.0),
    "db_clusters": (None, 80.0, 90.0),
    "db_cluster_parameter_groups": (None, 80.0, 90.0),
    "db_cluster_roles": (None, 80.0, 90.0),
}


def parse_aws_rds_limits(info):
    limits_by_region: AWSLimitsByRegion = {}
    for line in parse_aws(info):
        resource_key, resource_title, limit, amount, region = line

        if resource_key == "allocated_storage":
            # Allocated Storage has unit TiB
            factor = 1024**4 / 1000.0
            limit = limit * factor
            amount = amount * factor
            human_readable_f: Callable[[Any], str] | Type[int] = get_bytes_human_readable
        else:
            human_readable_f = int
        limits_by_region.setdefault(region, []).append(
            [resource_key, resource_title, limit, amount, human_readable_f]
        )
    return limits_by_region


@get_parsed_item_data
def check_aws_rds_limits(item, params, region_data):
    return check_aws_limits("rds", params, region_data)


check_info["aws_rds_limits"] = LegacyCheckDefinition(
    parse_function=parse_aws_rds_limits,
    discovery_function=discover(),
    check_function=check_aws_rds_limits,
    service_name="AWS/RDS Limits %s",
    check_ruleset_name="aws_rds_limits",
    default_levels_variable="aws_rds_limits_default_levels",
    check_default_parameters={
        "db_instances": (None, 80.0, 90.0),
        "reserved_db_instances": (None, 80.0, 90.0),
        "allocated_storage": (None, 80.0, 90.0),
        "db_security_groups": (None, 80.0, 90.0),
        "auths_per_db_security_groups": (None, 80.0, 90.0),
        "db_parameter_groups": (None, 80.0, 90.0),
        "manual_snapshots": (None, 80.0, 90.0),
        "event_subscriptions": (None, 80.0, 90.0),
        "db_subnet_groups": (None, 80.0, 90.0),
        "option_groups": (None, 80.0, 90.0),
        "subnet_per_db_subnet_groups": (None, 80.0, 90.0),
        "read_replica_per_master": (None, 80.0, 90.0),
        "db_clusters": (None, 80.0, 90.0),
        "db_cluster_parameter_groups": (None, 80.0, 90.0),
        "db_cluster_roles": (None, 80.0, 90.0),
    },
)
