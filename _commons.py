# -*- coding: utf-8 -*-
#
# Copyright 2021 Lingyun Gao
#
from constants import Location, DeviceType
import pathlib


FIELD_NAMES = ["datetime", "value"]


def create_filepath(
    location: Location,
    k: int,
    device_type: DeviceType,
    device_id: str,
    is_original: bool,
) -> str:
    suffix = "原始" if is_original else "经处理"
    filename = f"{location.value}_{k}_{device_type.value}_{device_id}_{suffix}.csv"
    filepath = pathlib.Path(__file__).parent.parent.absolute() / "data" / filename
    return filepath.as_posix()
