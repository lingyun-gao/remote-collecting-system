# -*- coding: utf-8 -*-
#
# Copyright 2021 Lingyun Gao
#
from _data_cleaner import DataCleaner
from _scraper import TCScraper
from _plot_drawer import Plotter
import logging

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


if __name__ == "__main__":
    TCScraper(restart=True).run()
    DataCleaner().run()
    Plotter().run()
