# -*- coding: utf-8 -*-
#
# Copyright 2021 Lingyun Gao
#
from datetime import datetime
from enum import Enum


class DeviceType(Enum):
    """电阻类型"""
    STRAINGAUGE = "应变电阻"
    THERMISTOR = "热敏电阻"


class Location(Enum):
    """采集点位置"""
    HIGHWAY = "高架桥"
    LAB = "实验室"


"""电阻ID（每次有新ID加入，将restart设置成True）"""
SENSORS = {
    Location.HIGHWAY: [
        {
            DeviceType.STRAINGAUGE: "1464336",
            DeviceType.THERMISTOR: "1487032",
        },
        {
            DeviceType.STRAINGAUGE: "1932949",
            DeviceType.THERMISTOR: "1932950",
        },
        {
            DeviceType.STRAINGAUGE: "1929469",
            DeviceType.THERMISTOR: "1929468",
        },
    ],
    Location.LAB: []
}


"""电阻自何时起开始采集数据"""
DEVICE_START_TIMES = {
    "1464336": datetime(2022, 1, 13, 22),
    "1487032": datetime(2022, 1, 13, 22),
    "1932949": datetime(2022, 1, 13, 22),
    "1932950": datetime(2022, 1, 13, 22),
    "1929469": datetime(2022, 1, 13, 22),
    "1929468": datetime(2022, 1, 13, 22),
}


"""
设置应变电阻和距离关系式的系数和截距：(a, b)
关系式：距离 = a * 电阻 + b
"""
PARAMS = {
    "1464336": (3.4, -338),
    "1932949": (3.4, -338),
    "1929469": (3.4, -338),
}
