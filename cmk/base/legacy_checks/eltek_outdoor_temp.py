#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="var-annotated"

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.temperature import check_temperature
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree
from cmk.base.plugins.agent_based.utils.eltek import DETECT_ELTEK

# .1.3.6.1.4.1.12148.9.1.17.3.1.1.0 1 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.0
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.1 2 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.1
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.2 3 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.2
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.3 4 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.3
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.4 5 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.4
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.5 6 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.5
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.6 7 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.6
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.7 8 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.7
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.8 9 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.8
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.9 10 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.9
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.10 11 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.10
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.11 12 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.11
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.12 13 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.12
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.13 14 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.13
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.0 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.0
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.1 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.1
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.2 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.2
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.3 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.3
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.4 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.4
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.5 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.5
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.6 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.6
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.7 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.7
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.8 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.8
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.9 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.9
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.10 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.10
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.11 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.11
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.12 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.12
# .1.3.6.1.4.1.12148.9.1.17.3.1.2.13 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp1.13
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.0 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.0
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.1 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.1
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.2 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.2
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.3 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.3
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.4 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.4
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.5 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.5
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.6 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.6
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.7 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.7
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.8 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.8
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.9 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.9
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.10 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.10
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.11 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.11
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.12 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.12
# .1.3.6.1.4.1.12148.9.1.17.3.1.3.13 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitOutDoorTemp2.13

# suggested by customer
factory_settings["eltek_outdoor_temp_default_variables"] = {
    "levels": (35, 40),
}


def inventory_eltek_outdoor_temp(info):
    inventory = []
    for index, temp1, temp2 in info:
        if int(temp1) > 0:
            inventory.append(("1/%s" % index, {}))
        if int(temp2) > 0:
            inventory.append(("2/%s" % index, {}))
    return inventory


def check_eltek_outdoor_temp(item, params, info):
    for index, temp1, temp2 in info:
        for temp_id, reading in [("1", float(temp1)), ("2", float(temp2))]:
            if "%s/%s" % (temp_id, index) == item:
                return check_temperature(reading, params, "eltek_outdoor_temp_%s" % item)
    return None


check_info["eltek_outdoor_temp"] = LegacyCheckDefinition(
    detect=DETECT_ELTEK,
    discovery_function=inventory_eltek_outdoor_temp,
    check_function=check_eltek_outdoor_temp,
    service_name="Temperature Outdoor %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.12148.9.1.17.3.1",
        oids=["1", "2", "3"],
    ),
    default_levels_variable="eltek_outdoor_temp_default_variables",
    check_default_parameters={
        "levels": (35, 40),
    },
)
