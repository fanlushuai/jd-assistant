# -*- coding:utf-8 -*-
import json
import time
from datetime import datetime

import requests

from config import global_config
from log import logger
from util import DEFAULT_USER_AGENT, get_random_useragent, get_local_time_stamp_13_float, datetime_to_timestamp


class JDTimer(object):

    def __init__(self):
        use_random_ua = global_config.getboolean('config', 'random_useragent')
        self.user_agent = DEFAULT_USER_AGENT if not use_random_ua else get_random_useragent()

    def get_diff_time(self):
        # 获取    本地时间 （减去）  京东服务器时间  的差值

        min_diff = 1000000000000000  # 注意：abs比较，所以默认设置一个非常大的，不能设置为0
        sync_count = 2
        while sync_count > 0:
            # 多次获得差值，取最小值
            try:
                jd_server_timestamp_13 = self.get_jd_server_timestamp_13()
                local_time_stamp_13_float = get_local_time_stamp_13_float()
                # 注意：本地时间 （减去）  京东服务器时间
                diff_jd_server_time = local_time_stamp_13_float - jd_server_timestamp_13
                print(diff_jd_server_time)  # 有点疑惑，为什么第一次的总是最快的//todo ？？？？？
                if abs(diff_jd_server_time) < abs(min_diff):
                    min_diff = diff_jd_server_time
            except Exception as e:
                # 如果出现异常，很可能说明结果已经不可信了。再次请求还是不可信，直接返回个默认的
                min_diff = 0
                logger.warn("获取京东时间异常 %s,直接认为0差距", e)
                return min_diff

            sync_count -= 1
            time.sleep(0.5)

        return min_diff

    def get_jd_server_timestamp_13(self):
        headers = {
            'User-Agent': self.user_agent
        }
        session = requests.session()
        session.keep_alive = False
        request_start_timestamp_13_float = get_local_time_stamp_13_float()
        response = session.get('https://a.jd.com//ajax/queryServerData.html', headers=headers)
        request_response_timestamp_13_float = get_local_time_stamp_13_float()

        js = json.loads(response.text)
        # {"serverTime":160 745 692 0037}
        jd_server_timestamp_13 = float(js["serverTime"])

        jd_server_timestamp_13_float_without_network_delay = jd_server_timestamp_13 + (
                (request_response_timestamp_13_float - request_start_timestamp_13_float) / 2)

        response_parse_timestamp_13_float = get_local_time_stamp_13_float()

        return (response_parse_timestamp_13_float - request_response_timestamp_13_float) + \
               jd_server_timestamp_13_float_without_network_delay

    def get_network_delay(self):
        request_start_timestamp_13_float = get_local_time_stamp_13_float()
        headers = {
            'User-Agent': self.user_agent
        }
        try:
            requests.get('https://a.jd.com//ajax/queryServerData.html', headers=headers)
        except Exception as e:
            logger.warn("将使用默认延迟。测试网络延迟 异常 %s", e)
            return 50
        request_response_timestamp_13_float = get_local_time_stamp_13_float()
        return (request_response_timestamp_13_float - request_start_timestamp_13_float) / 2


class Timer(object):

    def __init__(self, buy_time, sleep_interval=0.5, fast_sleep_interval=0.01, sync_time_before_seconds=5):
        self.buy_time_base_server = datetime_to_timestamp(datetime.strptime(buy_time, '%Y-%m-%d %H:%M:%S.%f'))
        self.buy_time_base_local = self.buy_time_base_server
        self.sync_time_before_seconds = sync_time_before_seconds
        self.sleep_interval = sleep_interval
        self.fast_sleep_interval = fast_sleep_interval
        self.jd_timer = JDTimer()
        # 初始化的时候，不应该做运算。因为后期在调用函数的时候会改变变量值，变量之间是没有监听关系的
        # 方法如果涉及到修改内部参数，谨慎处理，因为内部参数之间可能存在依赖关系。导致依赖关系断裂。也就是说，暴露出来的方法，尽量不要修改内部参数。或者修改的话，需要将依赖关系一并封装为一个修改方法
        self.__modify_buy_time()

    def start(self):
        logger.info('正在等待到达设定时间：%s' % self.buy_time_base_local)
        not_sync_time_before_buy = True
        fast_buy_time = self.buy_time_base_local + 5 * 1000
        while True:
            local_time_stamp_13_float = get_local_time_stamp_13_float()
            if local_time_stamp_13_float > self.buy_time_base_local - self.sync_time_before_seconds * 1000:
                if not_sync_time_before_buy:
                    network_delay = self.jd_timer.get_network_delay()
                    self.buy_time_base_local -= network_delay
                    logger.info("临近时间节点测试网络延迟，校准购买时间")
                    not_sync_time_before_buy = False

            if local_time_stamp_13_float >= self.buy_time_base_local:
                logger.info('时间到达，开始执行……')
                break
            else:
                if local_time_stamp_13_float >= fast_buy_time:
                    time.sleep(self.fast_sleep_interval)
                else:
                    time.sleep(self.sleep_interval)

    def __modify_buy_time(self):
        # 根据服务器和本地时间的差值，来修改本地时间设置的抢购时间

        # 注意，diff=本地-京东的
        diff_time = self.jd_timer.get_diff_time()
        local_sync_buy_time = self.buy_time_base_server - diff_time

        logger.info('time require:  %s  after sync: %s diff: %s', self.buy_time_base_local, local_sync_buy_time,
                    diff_time)
        self.buy_time_base_local = local_sync_buy_time


if __name__ == '__main__':
    timer = Timer('2020-12-09 21:59:59.950')
    timer.start()
