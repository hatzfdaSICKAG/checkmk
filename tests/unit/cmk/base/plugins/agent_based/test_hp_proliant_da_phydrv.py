#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, Service, State, TableRow
from cmk.base.plugins.agent_based.hp_proliant_da_phydrv import (
    check_hp_proliant_da_phydrv,
    discover_hp_proliant_da_phydrv,
    inventory_hp_proliant_da_phydrv,
    parse_hp_proliant_da_phydrv,
)

from .utils_inventory import sort_inventory_result

_AGENT_OUTPUT = [
    [
        "3",
        "8",
        "1",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ4XPK70000C5010PM0",
        "4",
        "HPD5",
    ],
    ["3", "9", "2", "2", "9050", "5723166", "2", "0", "2", "MB6000FEDAU", "1EJHTY4H", "4", "HPD1"],
    [
        "3",
        "10",
        "3",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ515CR0000W501Z7GK",
        "4",
        "HPD5",
    ],
    [
        "3",
        "11",
        "4",
        "2",
        "20322",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "S1Z2WN390000E717BQ0Q",
        "4",
        "HPDB",
    ],
    [
        "3",
        "12",
        "5",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ519SM0000W501Z3MB",
        "4",
        "HPD5",
    ],
    [
        "3",
        "13",
        "6",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ519N90000W4527H6S",
        "4",
        "HPD5",
    ],
    [
        "3",
        "14",
        "7",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ514E20000W5018EVB",
        "4",
        "HPD5",
    ],
    [
        "3",
        "15",
        "8",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ518KM0000W501ZH5U",
        "4",
        "HPD5",
    ],
    [
        "3",
        "16",
        "9",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ4XQAL0000C4528BEH",
        "4",
        "HPD5",
    ],
    [
        "3",
        "17",
        "10",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ4XBA20000C4525KFN",
        "4",
        "HPD5",
    ],
    [
        "3",
        "18",
        "11",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ4XDMA0000C4528BCA",
        "4",
        "HPD5",
    ],
    [
        "3",
        "19",
        "12",
        "2",
        "31597",
        "3815447",
        "2",
        "0",
        "2",
        "MB4000FCWDK",
        "XXZ4WSA70000C4528B49",
        "4",
        "HPD5",
    ],
    [
        "3",
        "20",
        "13",
        "2",
        "31597",
        "286102",
        "2",
        "0",
        "2",
        "EG0300FBVFL",
        "KFH1B3LF",
        "4",
        "HPDC",
    ],
    [
        "3",
        "21",
        "14",
        "2",
        "31597",
        "286102",
        "2",
        "0",
        "2",
        "EG0300FBVFL",
        "KFH1GHRF",
        "4",
        "HPDC",
    ],
    [
        "3",
        "22",
        "1",
        "2",
        "31597",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ4215000009442SDHD",
        "4",
        "HPD5",
    ],
    [
        "3",
        "23",
        "2",
        "2",
        "31597",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXY1RMWM0000C4423JRV",
        "4",
        "HPD5",
    ],
    [
        "3",
        "24",
        "3",
        "3",
        "31088",
        "2861588",
        "4",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ42CMG00009442SFMR",
        "4",
        "HPD5",
    ],
    [
        "3",
        "25",
        "4",
        "2",
        "31597",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ453ZJ000094428M7T",
        "4",
        "HPD5",
    ],
    [
        "3",
        "26",
        "5",
        "2",
        "12884",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FBNWV",
        "Z2986V780000C350AJZK",
        "4",
        "HPD6",
    ],
    [
        "3",
        "27",
        "6",
        "2",
        "31597",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ4CKBP0000C445DXBP",
        "4",
        "HPD5",
    ],
    [
        "3",
        "28",
        "7",
        "2",
        "31597",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ4D0P700009439LTC3",
        "4",
        "HPD5",
    ],
    [
        "3",
        "29",
        "8",
        "2",
        "31597",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ4BS1H00009444BFU0",
        "4",
        "HPD5",
    ],
    [
        "3",
        "30",
        "9",
        "2",
        "31597",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ4BTDD00009444BFU1",
        "4",
        "HPD5",
    ],
    [
        "3",
        "31",
        "10",
        "2",
        "31597",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ44D4Z00009442SUCB",
        "4",
        "HPD5",
    ],
    [
        "3",
        "32",
        "11",
        "2",
        "31597",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ3Z7YW00009441P86R",
        "4",
        "HPD5",
    ],
    [
        "3",
        "33",
        "12",
        "2",
        "11467",
        "2861588",
        "2",
        "2",
        "2",
        "MB3000FCWDH",
        "XXZ5G8WA0000C5069W2K",
        "4",
        "HPD9",
    ],
    [
        "3",
        "34",
        "1",
        "2",
        "68592",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FAMYV",
        "9WM3C8GF000091262F5E",
        "4",
        "HPD7",
    ],
    [
        "3",
        "35",
        "2",
        "2",
        "60070",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FBZPN",
        "XXP1DAFS00009232MWQX",
        "4",
        "HPD3",
    ],
    [
        "3",
        "36",
        "3",
        "2",
        "54960",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FBZPN",
        "XXP1LSEQ00009233P0EN",
        "4",
        "HPD3",
    ],
    [
        "3",
        "37",
        "4",
        "2",
        "28027",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FCWDF",
        "XXX4FL460000R53322FM",
        "4",
        "HPD9",
    ],
    [
        "3",
        "38",
        "5",
        "2",
        "47413",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FBZPN",
        "XXP1LRVT00009233F1J5",
        "4",
        "HPD3",
    ],
    [
        "3",
        "39",
        "6",
        "2",
        "35954",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FCWDF",
        "XXX0CB2Z0000C348B1EP",
        "4",
        "HPD5",
    ],
    [
        "3",
        "40",
        "7",
        "2",
        "40846",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FBZPN",
        "XXP1EK9G00009232MKEE",
        "4",
        "HPD3",
    ],
    [
        "3",
        "41",
        "8",
        "2",
        "60070",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FBZPN",
        "XXP1DAN500009232MWHZ",
        "4",
        "HPD3",
    ],
    [
        "3",
        "42",
        "9",
        "2",
        "68592",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FAMYV",
        "9WM3CRTJ00009126ZXE4",
        "4",
        "HPD7",
    ],
    [
        "3",
        "43",
        "10",
        "2",
        "45208",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FCWDF",
        "XXX0C25L0000C34900WJ",
        "4",
        "HPD5",
    ],
    [
        "3",
        "44",
        "11",
        "2",
        "68592",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FAMYV",
        "9WM3CBSK00009125YV9F",
        "4",
        "HPD7",
    ],
    [
        "3",
        "45",
        "12",
        "2",
        "68592",
        "1907729",
        "2",
        "3",
        "2",
        "MB2000FAMYV",
        "9WM3CY2W00009125YVHJ",
        "4",
        "HPD7",
    ],
]


@pytest.mark.parametrize(
    "string_table, expected_result",
    [
        (
            _AGENT_OUTPUT,
            [
                Service(item="3/8"),
                Service(item="3/9"),
                Service(item="3/10"),
                Service(item="3/11"),
                Service(item="3/12"),
                Service(item="3/13"),
                Service(item="3/14"),
                Service(item="3/15"),
                Service(item="3/16"),
                Service(item="3/17"),
                Service(item="3/18"),
                Service(item="3/19"),
                Service(item="3/20"),
                Service(item="3/21"),
                Service(item="3/22"),
                Service(item="3/23"),
                Service(item="3/24"),
                Service(item="3/25"),
                Service(item="3/26"),
                Service(item="3/27"),
                Service(item="3/28"),
                Service(item="3/29"),
                Service(item="3/30"),
                Service(item="3/31"),
                Service(item="3/32"),
                Service(item="3/33"),
                Service(item="3/34"),
                Service(item="3/35"),
                Service(item="3/36"),
                Service(item="3/37"),
                Service(item="3/38"),
                Service(item="3/39"),
                Service(item="3/40"),
                Service(item="3/41"),
                Service(item="3/42"),
                Service(item="3/43"),
                Service(item="3/44"),
                Service(item="3/45"),
            ],
        ),
    ],
)
def test_discover_hp_proliant_da_phydrv(string_table, expected_result) -> None:
    assert (
        list(discover_hp_proliant_da_phydrv(parse_hp_proliant_da_phydrv(string_table)))
        == expected_result
    )


@pytest.mark.parametrize(
    "string_table, item, expected_result",
    [
        (
            _AGENT_OUTPUT,
            "3/8",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 1, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/9",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 2, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 9050, Size: 6001174511616MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/10",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 3, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/11",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 4, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 20322, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/12",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 5, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/13",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 6, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/14",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 7, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/15",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 8, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/16",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 9, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/17",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 10, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/18",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 11, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/19",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 12, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 4000786153472MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/20",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 13, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 299999690752MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/21",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 14, Bus number: 0, Status: ok, Smart status: ok, Ref hours: 31597, Size: 299999690752MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/22",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 1, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 31597, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/23",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 2, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 31597, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/24",
            [
                Result(
                    state=State.CRIT,
                    summary="Bay: 3, Bus number: 2, Status: failed, Smart status: ok, Ref hours: 31088, Size: 3000592498688MB, Condition: failed",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/25",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 4, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 31597, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/26",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 5, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 12884, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/27",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 6, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 31597, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/28",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 7, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 31597, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/29",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 8, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 31597, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/30",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 9, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 31597, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/31",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 10, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 31597, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/32",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 11, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 31597, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/33",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 12, Bus number: 2, Status: ok, Smart status: ok, Ref hours: 11467, Size: 3000592498688MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/34",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 1, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 68592, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/35",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 2, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 60070, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/36",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 3, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 54960, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/37",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 4, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 28027, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/38",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 5, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 47413, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/39",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 6, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 35954, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/40",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 7, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 40846, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/41",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 8, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 60070, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/42",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 9, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 68592, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/43",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 10, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 45208, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/44",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 11, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 68592, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
        (
            _AGENT_OUTPUT,
            "3/45",
            [
                Result(
                    state=State.OK,
                    summary="Bay: 12, Bus number: 3, Status: ok, Smart status: ok, Ref hours: 68592, Size: 2000398843904MB, Condition: ok",
                )
            ],
        ),
    ],
)
def test_check_hp_proliant_da_phydrv(string_table, item, expected_result) -> None:
    assert (
        list(
            check_hp_proliant_da_phydrv(
                item=item, section=parse_hp_proliant_da_phydrv(string_table)
            )
        )
        == expected_result
    )


@pytest.mark.parametrize(
    "string_table, expected_result",
    [
        ([], []),
        (
            [
                [
                    "3",
                    "8",
                    "1",
                    "2",
                    "31597",
                    "3815447",
                    "2",
                    "0",
                    "2",
                    "MB4000FCWDK",
                    "XXZ4XPK70000C5010PM0",
                    "4",
                    "HPD5",
                ]
            ],
            [
                TableRow(
                    path=["hardware", "storage", "disks"],
                    key_columns={
                        "controller": "3",
                    },
                    inventory_columns={
                        "bay": "1",
                        "bus": "0",
                        "size": 4000786153472,
                        "model": "MB4000FCWDK",
                        "serial": "XXZ4XPK70000C5010PM0",
                        "type": "SAS",
                        "firmware": "HPD5",
                    },
                    status_columns={},
                ),
            ],
        ),
    ],
)
def test_inventory_hp_proliant_da_phydrv(string_table, expected_result) -> None:
    assert sort_inventory_result(
        inventory_hp_proliant_da_phydrv(parse_hp_proliant_da_phydrv(string_table))
    ) == sort_inventory_result(expected_result)
