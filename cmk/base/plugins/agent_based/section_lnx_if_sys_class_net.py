#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from enum import Enum
from typing import Mapping, Sequence

from cmk.base.plugins.agent_based.agent_based_api.v1 import register
from cmk.base.plugins.agent_based.utils.interfaces import (
    Attributes,
    Counters,
    InterfaceWithCounters,
    mac_address_from_hexstring,
)
from cmk.base.plugins.agent_based.utils.lnx_if import Section

# To understand why this section exists, please read the comments in the
# correpsonding agent plugin.

# Parsing logic derived from Linux kernel documentation at
# https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-class-net
# and from lnx_if


class InterfaceStatus(Enum):
    UP = "1"
    DOWN = "2"


def _parse_raw_stats(line: Sequence[str]) -> Mapping[str, str]:
    """
    >>> _parse_raw_stats(["ifindex\v4", "ifalias\v", "speed\v0"])
    {'ifindex': '4', 'ifalias': '', 'speed': '0'}
    """
    raw_stats = {}
    for stats in line:
        k, v = stats.split("\v")
        raw_stats[k] = v
    return raw_stats


def _parse_speed(speed_string: str) -> float:
    """
    >>> _parse_speed("")
    0.0
    >>> _parse_speed("-1")
    0.0
    >>> _parse_speed("0")
    0.0
    >>> _parse_speed("5")
    5000000.0
    """
    if speed_string in ("", "-1"):
        # This covers the following cases:
        # file does not exist: e.g. in the event that a wifi interface has been disabled
        # file contains "-1", which means that the speed is unknown
        # file is empty, which is also interpreded as unknown

        # It would be better to handle this case differently, but
        # this is how it's currently handled by all interfaces
        return 0.0

    # Speed is always in Mbits/sec, see Linux kernel documentation (link at top)
    return float(speed_string) * 1000000.0


def _parse_interface_status(carrier: str) -> InterfaceStatus:
    """
    >>> _parse_interface_status("1")
    <InterfaceStatus.UP: '1'>
    >>> _parse_interface_status("0")
    <InterfaceStatus.DOWN: '2'>
    """
    if carrier == "1":
        return InterfaceStatus.UP
    if carrier == "0":
        return InterfaceStatus.DOWN
    raise ValueError(f"Unknown value for carrier: '{carrier}'")


def _create_interface(raw_stats: Mapping[str, str]) -> InterfaceWithCounters:
    multicast = float(raw_stats["multicast"])
    return InterfaceWithCounters(
        attributes=Attributes(
            index=raw_stats["ifindex"],
            descr=raw_stats["name"],
            alias=raw_stats["ifalias"],
            type=raw_stats["type"],
            speed=_parse_speed(raw_stats["speed"]),
            oper_status=_parse_interface_status(raw_stats["carrier"]).value,
            phys_address=mac_address_from_hexstring(raw_stats["address"]),
            out_qlen=float(raw_stats["tx_fifo_errors"]),
        ),
        counters=Counters(
            in_octets=float(raw_stats["rx_bytes"]),
            in_ucast=float(raw_stats["rx_packets"]) + multicast,
            in_mcast=multicast,
            in_disc=float(raw_stats["rx_dropped"]),
            in_err=float(raw_stats["rx_errors"]),
            out_octets=float(raw_stats["tx_bytes"]),
            out_ucast=float(raw_stats["tx_packets"]),
            out_disc=float(raw_stats["tx_dropped"]),
            out_err=float(raw_stats["tx_errors"]),
        ),
    )


def parse_lnx_if_sys_class_net(string_table) -> Section:
    return [_create_interface(_parse_raw_stats(i)) for i in string_table], {}


register.agent_section(
    name="lnx_if_sys_class_net",
    parsed_section_name="lnx_if",
    parse_function=parse_lnx_if_sys_class_net,
    supersedes=["lnx_if"],
)
