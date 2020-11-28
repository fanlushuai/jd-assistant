# -*- coding:utf-8 -*-
import time
import json
import win32api
import ctypes, sys
import requests
from datetime import datetime, timedelta

from log import logger


def is_admin():
    try:
        # 获取当前用户的是否为管理员
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class Timer(object):

    def __init__(self, buy_time, sleep_interval=0.5, fast_sleep_interval=0.01):

        if not is_admin():
            # 重新运行这个程序使用管理员权限
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        # 同步京东服务器时间
        self.setSystemTime()

        # '2018-09-28 22:45:50.000'
        self.buy_time = datetime.strptime(buy_time, "%Y-%m-%d %H:%M:%S.%f")
        self.fast_buy_time = self.buy_time + timedelta(seconds=-5)
        self.sleep_interval = sleep_interval
        self.fast_sleep_interval = fast_sleep_interval

    def start(self):
        logger.info('正在等待到达设定时间：%s' % self.buy_time)
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

    def setSystemTime(self):
        url = 'https://a.jd.com//ajax/queryServerData.html'

        session = requests.session()

        # get server time
        t0 = datetime.now()
        ret = session.get(url).text
        t1 = datetime.now()

        js = json.loads(ret)
        t = float(js["serverTime"]) / 1000
        dt = datetime.fromtimestamp(t) + ((t1 - t0) / 2)
        tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(
            time.mktime(dt.timetuple()))
        msec = dt.microsecond / 1000
        win32api.SetSystemTime(tm_year, tm_mon, tm_wday, tm_mday, tm_hour, tm_min, tm_sec, int(msec))
        logger.info('已同步京东服务器时间：%s' % dt)