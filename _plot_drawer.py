# -*- coding: utf-8 -*-
#
# Copyright 2021 Lingyun Gao
#
from plotly.subplots import make_subplots
from constants import DeviceType, SENSORS, PARAMS
from _commons import create_filepath

import pandas as pd
import plotly
import plotly.graph_objects as go


class Plotter:
    @staticmethod
    def run() -> None:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        for location, points in SENSORS.items():
            for i, devices in enumerate(points):
                for device_type in DeviceType:
                    device_id = devices[device_type]
                    filename = create_filepath(location, i + 1, device_type, device_id, is_original=False)
                    df = pd.read_csv(filename)
                    secondary_y = (device_type == DeviceType.THERMISTOR)
                    fig.add_trace(
                        go.Scatter(
                            x=df["datetime"],
                            y=df["value"],
                            name=f"{location.value}_{str(i + 1)}_{device_type.value}"
                        ),
                        secondary_y=secondary_y
                    )

        # Add figure title
        fig.update_layout(
            title_text="远程电阻采集结果"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="时间")

        # Set y-axes titles
        fig.update_yaxes(title_text="位置(mm)", secondary_y=False)
        fig.update_yaxes(title_text="温度(°C)", secondary_y=True)
        plotly.offline.plot(fig, filename="plot.html", auto_open=False)
