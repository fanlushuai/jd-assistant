#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from config import global_config, CMD_SECTION
from jd_assistant import Assistant

"""
重要提示：此处为示例代码之一，请移步下面的链接查看使用教程👇
https://github.com/tychxn/jd-assistant/wiki/1.-%E4%BA%AC%E4%B8%9C%E6%8A%A2%E8%B4%AD%E5%8A%A9%E6%89%8B%E7%94%A8%E6%B3%95
"""

# 抢购通用配置

sku_id = global_config.get('sku', 'sku_id')  # 商品id
buy_time = global_config.get('sku', 'buy_time')  # 开始抢购时间，格式：'2020-11-28 12:59:59.950'
retry = 5  # 抢购重复执行次数，可选参数，默认4次
interval = 0.01  # 抢购执行间隔，可选参数，默认4秒
num = 1  # 购买数量，可选参数，默认1个
sleep_interval = 0.5  # 抢购前倒计时轮询时间，默认0.5秒
fast_sleep_interval = 0.01  # 抢购5秒内倒计时轮询时间，默认0.01秒

# 配置【预约抢购，自动加入购物车】
# 注意：一定要在抢购开始前手动清空购物车中此类无法勾选的商品！（因为脚本在执行清空购物车操作时，无法清空不能勾选的商品）
is_pass_cart = False  # 是否跳过添加购物车，默认False

# 配置【预约抢购，不会自动加入购物车】
# area = '19_1607_3155_62117'  # 区域id
# sku_buy_time = '2020-12-04 15:00:00.000'  # 商品抢购时间
# buy_time = None  # 开始抢购时间，默认为None，自动提前0.050秒，网络通畅时不需要修改，如果网络慢可根据自己情况适当修改，格式：'2020-11-28 12:59:59.950'
fast_mode = True  # 快速模式：略过访问抢购订单结算页面这一步骤，默认为 True


def boot_ass():
    asst = Assistant()  # 初始化
    asst.login_by_QRcode()  # 扫码登陆

    # # 执行【预约抢购，自动加入购物车】 手动清空自动添加到购物车的
    # asst.exec_reserve_seckill_by_time(sku_id=sku_id, buy_time=buy_time, retry=retry, interval=interval, num=num,
    #                                   is_pass_cart=is_pass_cart, sleep_interval=sleep_interval,
    #                                   fast_sleep_interval=fast_sleep_interval)

    # 执行【预约抢购，不会自动加入购物车】
    asst.exec_seckill_by_time(sku_ids=sku_id, buy_time=buy_time, num=num, fast_mode=fast_mode)

    # 根据商品是否有货自动下单
    # 6个参数：
    # sku_ids: 商品id。可以设置多个商品，也可以带数量，如：'1234' 或 '1234,5678' 或 '1234:2' 或 '1234:2,5678:3'
    # area: 地区id
    # wait_all: 是否等所有商品都有货才一起下单，可选参数，默认False
    # stock_interval: 查询库存时间间隔，可选参数，默认3秒
    # submit_retry: 提交订单失败后重试次数，可选参数，默认3次
    # submit_interval: 提交订单失败后重试时间间隔，可选参数，默认5秒


def boot():
    if global_config.getboolean(CMD_SECTION, 'aps'):
        datetime_obj = datetime.datetime.strptime(buy_time, '%Y-%m-%d %H:%M:%S.%f')
        # 设定时间的前两分钟再开启 ass。因为里面通过轮训的逻辑来执行定时操作。会消耗cpu。通过定时调度减缓一点消耗。
        # 先不修改简单用用。看看效果再说。之后考虑重写逻辑全调度器。主要还是考虑精度问题
        run_date = datetime_obj + datetime.timedelta(minutes=-5)
        scheduler = BlockingScheduler()
        scheduler.add_job(boot_ass, 'date', run_date=run_date, id='boot_ass')
        scheduler.start()
    else:
        boot_ass()


if __name__ == '__main__':
    boot()
