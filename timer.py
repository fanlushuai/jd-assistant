# -*- coding:utf-8 -*-
import time
from datetime import datetime, timedelta

from log import logger


class Timer(object):

    def __init__(self, buy_time, sleep_interval=0.5, fast_sleep_interval=0.01):

        # '2018-09-28 22:45:50.000'
        self.buy_time = datetime.strptime(buy_time, "%Y-%m-%d %H:%M:%S.%f")
        self.fast_buy_time = self.buy_time + timedelta(seconds=-5)
        self.sleep_interval = sleep_interval
        self.fast_sleep_interval = fast_sleep_interval

    def start(self):
        logger.info('正在等待到达设定时间:%s' % self.buy_time)
        now_time = datetime.now
        while True:
            if now_time() >= self.buy_time:
                logger.info('时间到达，开始执行……')
                break
            else:
                if now_time() >= self.fast_buy_time:
                    time.sleep(self.fast_sleep_interval)
                else:
                    time.sleep(self.sleep_interval)
