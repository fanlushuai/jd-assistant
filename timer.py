# -*- coding:utf-8 -*-
import json
import time
from datetime import datetime

import requests

from log import logger


class Timer(object):

    def __init__(self, buy_time, sleep_interval=0.5, fast_sleep_interval=0.01, sync_time_before_seconds=5):
        self.buy_time_base_server = self.datetime_to_timestamp(datetime.strptime(buy_time, '%Y-%m-%d %H:%M:%S.%f'))
        self.buy_time_base_local = self.buy_time_base_server
        self.modify_buy_time()
        self.fast_buy_time = self.buy_time_base_local + 5 * 1000
        self.sleep_interval = sleep_interval
        self.fast_sleep_interval = fast_sleep_interval
        self.sync_time_before_seconds = sync_time_before_seconds

    def start(self):
        logger.info('正在等待到达设定时间：%s' % self.buy_time_base_local)
        not_sync_time_before_buy = True
        while True:
            local_time_stamp_13_float = self.get_local_time_stamp_13_float()
            if local_time_stamp_13_float > self.buy_time_base_local - self.sync_time_before_seconds * 1000:
                if not_sync_time_before_buy:
                    network_delay = self.test_network_delay()
                    self.buy_time_base_local -= network_delay
                    logger.info("临近时间节点测试网络延迟，校准购买时间")
                    not_sync_time_before_buy = False

            if local_time_stamp_13_float >= self.buy_time_base_local:
                logger.info('时间到达，开始执行……')
                break
            else:
                if local_time_stamp_13_float >= self.fast_buy_time:
                    time.sleep(self.fast_sleep_interval)
                else:
                    time.sleep(self.sleep_interval)

    def test_network_delay(self):
        request_start_timestamp_13_float = self.get_local_time_stamp_13_float()
        requests.get('https://a.jd.com//ajax/queryServerData.html')
        request_response_timestamp_13_float = self.get_local_time_stamp_13_float()
        return request_response_timestamp_13_float - request_start_timestamp_13_float

    def modify_buy_time(self):
        # 根据服务器和本地时间的差值，来修改本地时间设置的抢购时间

        # 注意，diff=本地-京东的
        diff_time = self.get_diff_time()
        local_sync_buy_time = self.buy_time_base_server - diff_time

        logger.info('time require:  %s  after sync: %s diff: %s', self.buy_time_base_local, local_sync_buy_time,
                    diff_time)
        self.buy_time_base_local = local_sync_buy_time

    def get_diff_time(self):
        # 获取    本地时间 （减去）  京东服务器时间  的差值

        min_diff = 1000000000000000  # 注意：abs比较，所以默认设置一个非常大的，不能设置为0
        sync_count = 6
        while sync_count > 0:
            # 多次获得差值，取最小值
            jd_server_timestamp_13 = self.get_jd_server_timestamp_13()
            local_time_stamp_13_float = self.get_local_time_stamp_13_float()
            # 注意：本地时间 （减去）  京东服务器时间
            diff_jd_server_time = local_time_stamp_13_float - jd_server_timestamp_13
            # print(diff_jd_server_time) # 有点疑惑，为什么第一次的总是最快的//todo ？？？？？
            if abs(diff_jd_server_time) < abs(min_diff):
                min_diff = diff_jd_server_time

            sync_count -= 1

        return min_diff

    def get_jd_server_timestamp_13(self):
        request_start_timestamp_13_float = self.get_local_time_stamp_13_float()
        response = requests.get('https://a.jd.com//ajax/queryServerData.html')
        request_response_timestamp_13_float = self.get_local_time_stamp_13_float()

        js = json.loads(response.text)
        # {"serverTime":160 745 692 0037}
        jd_server_timestamp_13 = float(js["serverTime"])

        jd_server_timestamp_13_float_without_network_delay = jd_server_timestamp_13 + (
                (request_response_timestamp_13_float - request_start_timestamp_13_float) / 2)

        response_parse_timestamp_13_float = self.get_local_time_stamp_13_float()

        return (response_parse_timestamp_13_float - request_response_timestamp_13_float) \
               + jd_server_timestamp_13_float_without_network_delay

    @staticmethod
    def datetime_to_timestamp(datetime_obj):
        return int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)

    @staticmethod
    def get_local_time_stamp_13_float():
        # 注意 time.time()的精度，我不是很确定。有的说是精确是时间错13位。有的说是机器不一样精度不一样
        return time.time() * 1000


if __name__ == '__main__':
    Timer('2020-12-09 21:59:59.950').start();
