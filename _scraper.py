# -*- coding: utf-8 -*-
#
# Copyright 2021 Lingyun Gao 高凌芸
#
from _commons import create_filepath, FIELD_NAMES
from constants import DEVICE_START_TIMES, DeviceType, SENSORS
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import csv
import json
import logging
import requests


class TCScraper:
    """
    用于爬取塔石数据的爬虫
    """
    _HEADERS = {
        "Accept": "*/*",
        "X-Requested-With": "YXMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    _LOGIN_ACCOUNT = ""  # TODO: add login account
    _LOGIN_PASSWORD = ""  # TODO: add password
    _COMPANY_USER_ID = ""  # TODO: add company user id

    # 存储每个电阻爬虫运行时最后一组数据的时间, 下次只需爬取新数据，老数据不用重复爬取
    _LAST_RUN_TIME_FILE = "last_run_time.json"

    def __init__(self, restart: bool = False) -> None:
        self._cookies = self._get_cookies()
        self._last_run_time = self._get_last_run_time(restart)
        self._restart = restart

    def _get_cookies(self) -> requests.cookies.RequestsCookieJar:
        # 登录塔石并获取cookies
        data = {
            "loginAccount": self._LOGIN_ACCOUNT,
            "loginPassword": self._LOGIN_PASSWORD,
            "companyUserId": self._COMPANY_USER_ID,
        }
        response = requests.post(
            "http://tc.tastek.cn/user/login.htm",
            headers=self._HEADERS,
            data=data,
        )
        if response.ok:
            logging.info("获取塔石cookies成功")
            return response.cookies
        else:
            raise ValueError("获取cookies失败!")

    def _get_last_run_time(self, restart: bool) -> Dict[str, datetime]:
        # 获取每个电阻上次爬虫运行时最后一组数据的时间
        if restart:
            logging.info("爬虫被重置，从头开始爬取数据")
            return DEVICE_START_TIMES

        with open(self._LAST_RUN_TIME_FILE, "r") as f:
            parsed = json.loads(f.read())
            last_run_time = {
                k: datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                for k, v in parsed.items()
            }
        logging.info("成功获取上一次读取数据的时间戳")
        return last_run_time

    def _write_last_run_time(self, new_run_time: Dict[str, datetime]) -> None:
        with open(self._LAST_RUN_TIME_FILE, "w") as f:
            f.write(
                json.dumps(
                    {k: v.strftime("%Y-%m-%d %H:%M:%S") for k, v in new_run_time.items()}
                )
            )
        logging.info(f"`{self._LAST_RUN_TIME_FILE}`更新完成")

    def _get_device_data(self, device_id: str) -> Dict[str, Any]:
        # 获取ID为`device_id`的电阻从之前最后一组数据时间点至今随时间变化的数据
        start_time = self._last_run_time[device_id] + timedelta(seconds=1)
        # 为了确保不论是哪个时区，当前时间为最新时间，在当前时间基础上加一天
        end_time = datetime.now() + timedelta(days=1)

        data = {
            "sensorId": device_id,
            "startDate": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "endDate": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        response = requests.post(
            "http://tc.tastek.cn/user/querySensorHisDataLine.htm",
            headers=self._HEADERS,
            cookies=self._cookies,
            data=data,
            verify=False,
        )
        if response.ok:
            parsed_data = json.loads(response.content)
            logging.info(f"获取`{device_id}`设备数据成功")
            return parsed_data
        else:
            raise ValueError(f"获取`{device_id}`设备数据失败！")

    @staticmethod
    def _create_csv_file(filepath: str) -> None:
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
            writer.writeheader()
        logging.info(f"创建`{filepath}`文件成功")

    @staticmethod
    def _write_sensor_data(filepath: str, data: Dict[str, Any]) -> Optional[datetime]:
        time_list = data.get("timeList")
        data_list = data.get("dataList")
        if not time_list and not data_list:
            logging.info("自上次读数据起无新数据生成，故不更新数据文件")
            return None

        assert len(time_list) == len(data_list)

        with open(filepath, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
            for dt, value in zip(time_list, data_list):
                writer.writerow({
                    FIELD_NAMES[0]: dt,
                    FIELD_NAMES[1]: value,
                })
        logging.info(f"更新`{filepath}`文件成功")
        return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")

    def run(self) -> None:
        # 对于每个数据采集点，采集应变电阻和热敏电阻的数据，并记录最后一组数据的时间
        new_run_times: Dict[str, datetime] = {}
        for location, points in SENSORS.items():
            for i, devices in enumerate(points):
                for device_type in DeviceType:

                    device_id = devices[device_type]
                    filepath = create_filepath(location, i + 1, device_type, device_id, is_original=True)

                    if self._restart:
                        # 如果重置，创建一个新csv文件用于存储数据
                        self._create_csv_file(filepath)

                    device_data = self._get_device_data(device_id)
                    new_run_time = (
                        self._write_sensor_data(filepath, device_data)
                        or self._last_run_time[device_id]
                    )
                    new_run_times[device_id] = new_run_time
        self._write_last_run_time(new_run_times)
