# -*- coding:utf-8 -*-
import json
import time
from datetime import datetime

import requests

from config import global_config
from log import logger
from util import DEFAULT_USER_AGENT, get_random_useragent, get_local_time_stamp_13_float, datetime_to_timestamp


class TimeWait(object):
    def __init__(self, sleep_interval=0.5, fast_sleep_interval=0.01, fast_change_seconds=2):
        self.sleep_interval = sleep_interval
        self.fast_sleep_interval = fast_sleep_interval
        self.fast_change_seconds = fast_change_seconds
        self.jd_time_sync = JDTimeSync()
        self.timer = Timer()

    def start_wait_until_time(self, until_time, auto_fix=False):
        """
        执行wait。使用传入时间
        :param until_time: 格式例子。'2018-09-28 22:45:50.000'
        :param auto_fix: 是否自动校正时间。默认false
        :return:
        """
        until_time_milli_sec = datetime_to_timestamp(datetime.strptime(until_time, '%Y-%m-%d %H:%M:%S.%f'))
        if auto_fix:
            # 自动将基于服务器的时间，切换到基于本地时钟的时间
            until_time_milli_sec = until_time_milli_sec - self.jd_time_sync.local_diff_server_time_microseconds()
        self.timer.start(until_time_milli_sec)


class Timer(object):

    def __init__(self, sleep_interval=0.5, fast_sleep_interval=0.01, fast_change_seconds=2):

        self.sleep_interval = sleep_interval
        self.fast_sleep_interval = fast_sleep_interval
        self.fast_change_seconds = fast_change_seconds

    def start(self, trigger_time):
        """
        trigger_time : millisecond 毫秒 时间戳
        """
        logger.info('Timer loop …… util：%s' % trigger_time)
        fast_change_time = trigger_time - self.fast_change_seconds * 1000
        while True:
            local_time_stamp_13_float = get_local_time_stamp_13_float()

            if local_time_stamp_13_float >= trigger_time:
                logger.info('Timer triggered %s', trigger_time)
                break
            else:
                if local_time_stamp_13_float >= fast_change_time:
                    time.sleep(self.fast_sleep_interval)
                else:
                    time.sleep(self.sleep_interval)


class JDTimeSync(object):

    def __init__(self):
        use_random_ua = global_config.getboolean('config', 'random_useragent')
        self.user_agent = DEFAULT_USER_AGENT if not use_random_ua else get_random_useragent()

    def local_diff_server_time_microseconds(self):
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
        url = 'https://a.jd.com//ajax/queryServerData.html'
        headers = {
            'User-Agent': self.user_agent
        }
        session = requests.session()
        session.keep_alive = False

        response = session.get(url, headers=headers)
        http_delay_millisecond = response.elapsed.microseconds / 1000

        response_parse_start = get_local_time_stamp_13_float()
        js = json.loads(response.text)
        # {"serverTime":160 745 692 0037}
        jd_server_timestamp_13 = float(js["serverTime"])
        response_parse_end = get_local_time_stamp_13_float()

        parse_time = (response_parse_end - response_parse_start)

        return jd_server_timestamp_13 + parse_time + http_delay_millisecond

    def get_http_delay_microseconds(self):
        url = 'https://a.jd.com//ajax/queryServerData.html'
        http_delay_microseconds = 50
        headers = {
            'User-Agent': self.user_agent
        }
        try:
            http_delay_microseconds = requests.get(url, headers=headers).elapsed.microseconds / 1000
        except Exception as e:
            logger.warn("测试网络延迟 异常，返回默认延迟 %s %s", http_delay_microseconds, e)
        return http_delay_microseconds

if __name__ == '__main__':
    TimeWait().start_wait_until_time('2020-12-11 10:00:00.000', auto_fix=True)
