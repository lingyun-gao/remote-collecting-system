# -*- coding: utf-8 -*-
#
# Copyright 2021 Lingyun Gao
#
from _commons import create_filepath, FIELD_NAMES
from constants import DeviceType, SENSORS, PARAMS
from typing import Callable

import csv


class DataCleaner:
    """
    用于处理数据，每15个数据点作为一组数据进行处理，按数据大小取中间5个(去除最大、最小的5个数据)数据的平均值
    """
    _BATCH_SIZE = 15
    _N_OUTLIERS = 5

    @staticmethod
    def _get_transform(device_id: str) -> Callable[[float], float]:
        def _identity(x: float) -> float:
            return x

        def _transform(x: float) -> float:
            return a * x + b

        if device_id not in PARAMS:
            return _identity
        a, b = PARAMS[device_id]
        return _transform

    @classmethod
    def _clean_and_write_data(
        cls,
        source_file: str,
        dest_file: str,
        transform: Callable[[float], float]
    ) -> None:
        with open(dest_file, "w", newline="") as csvwriter:
            writer = csv.DictWriter(csvwriter, fieldnames=FIELD_NAMES)
            writer.writeheader()

            with open(source_file, newline="") as csvreader:
                reader = csv.DictReader(csvreader)

                time_buffer = []
                value_buffer = []
                for i, row in enumerate(reader):
                    if i % cls._BATCH_SIZE == 0 and i > 0:
                        # 检查时间是否顺序排列
                        if sorted(time_buffer) != time_buffer:
                            raise ValueError(f"从{i + 2}行开始的{cls._BATCH_SIZE}个时间序列没有顺序排列，请检查！")
                        mid = cls._BATCH_SIZE // 2
                        avg_time = time_buffer[mid]
                        avg_value = (
                            sum(sorted(value_buffer)[cls._N_OUTLIERS: - cls._N_OUTLIERS])
                            / (cls._BATCH_SIZE - 2 * cls._N_OUTLIERS)
                        )
                        writer.writerow({
                            FIELD_NAMES[0]: avg_time,
                            FIELD_NAMES[1]: transform(avg_value),
                        })

                        # 清空buffer，重新开始塞15个数据进去
                        time_buffer = []
                        value_buffer = []
                    time_buffer.append(row["datetime"])
                    value_buffer.append(float(row["value"]))

    def run(self) -> None:
        for location, points in SENSORS.items():
            for i, devices in enumerate(points):
                for device_type in DeviceType:
                    device_id = devices[device_type]
                    source_file = create_filepath(location, i + 1, device_type, device_id, is_original=True)
                    dest_file = create_filepath(location, i + 1, device_type, device_id, is_original=False)
                    self._clean_and_write_data(source_file, dest_file, self._get_transform(device_id))
