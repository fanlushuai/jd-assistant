import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from main import *

if __name__ == '__main__':
    datetime_obj = datetime.datetime.strptime(buy_time, '%Y-%m-%d %H:%M:%S.%f')
    # 设定时间的前两分钟再开启 ass。因为里面通过轮训的逻辑来执行定时操作。会消耗cpu。通过定时调度减缓一点消耗。
    # 先不修改简单用用。看看效果再说。之后考虑重写逻辑全调度器。主要还是考虑精度问题
    run_date = datetime_obj + datetime.timedelta(minutes=-2)
    scheduler = BlockingScheduler()
    scheduler.add_job(boot_ass(), 'date', run_date=run_date, args=['text'], id='xx')
    scheduler.start()
