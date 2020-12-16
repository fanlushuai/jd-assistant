import functools
import queue
import random
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

from log import logger

shut_down_pool_queue = queue.Queue()
sys_thread_pool = ThreadPoolExecutor(max_workers=2)


def shutdown_listener():
    for _ in repeat(None):
        t_pool = shut_down_pool_queue.get()
        t_pool.shutdown()
        logger.info("shutdown")


sys_thread_pool.submit(shutdown_listener)


def threads(concurrent_size=1, try_times=1, try_internal=0.05):
    """
    并发工具。
    :param concurrent_size: 每次重试的并发数
    :param try_times: 重试次数
    :param try_internal: 重试间隔
    :return: 多线程，多次重试。的所有任务中，哪个最快获得结果，就将哪个返回。如果都没有获得，就返回None
    """

    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return Job(concurrent_size, try_times, try_internal).run(func, *args, **kw)

        return wrapper

    return decorate


class Job(object):
    """
     并发处理工具。
     可以在一个周期并发相应的请求。并且，上个周期的任务不会影响下个周期的延迟。
     具体来讲：周期1执行时间t1，周期2执行时间为 t2= t1 + try_internal
     解决的问题：
     传统的for循环，周期1执行时间t1，周期2执行时间为 t2= t1+任务耗时+try_internal。
     （可见传统方式的毛病，并不能带来真正的并发。只是单线程重试，并且重试的间隔受到上个周期任务执行时间的影响，严格讲，这种重试的间隔参数毫无意义，尤其是在io操作的时候）
    """

    def __init__(self, concurrent_size=1, try_times=1, try_internal=0.05):
        self.concurrent_size = concurrent_size
        self.try_times = try_times
        self.try_internal = try_internal
        self.futures = []
        self.thread_pool = ThreadPoolExecutor(max_workers=15)
        self.loop = True

    def run(self, fn, *args, **kwargs):
        # 开启异步线程去做这个
        self.thread_pool.submit(self._loop, fn, *args, **kwargs)
        logger.info("同步等待结果……")
        # 同步获取返回结果
        try_return_count = 0
        for _ in repeat(None):
            futures = self.futures
            for future in futures:
                if future.done():
                    re = future.result()
                    if re:
                        self.loop = False
                        # !!!!!! 确的修饰的方法，必须有明返回值。None或者其他。不然会一直搞
                        shut_down_pool_queue.put(self.thread_pool)
                        return re
                    else:
                        try_return_count += 1
                        if try_return_count >= self.try_times * self.concurrent_size:
                            return None

    def _loop(self, fn, *args, **kwargs):
        for try_count in range(self.try_times):
            for i in range(self.concurrent_size):
                self.futures.append(self.thread_pool.submit(fn, *args, **kwargs))
                logger.info("启动线程")
                if not self.loop:
                    # loop会一直执行，直到结果获得,或者循环结束，即self.try_times*self.concurrent_size
                    logger.debug("获取到结果，结束")
                    return
            if not self.loop:
                logger.debug("获取到结果，结束")
                # loop会一直执行，直到结果获得,或者循环结束，即self.try_times*self.concurrent_size
                return
            time.sleep(self.try_internal)


@threads(concurrent_size=3, try_times=100, try_internal=0.1)
def test_g():
    t = random.choice([0.1, 0.2, 0.3, 0.4, 0.5, 1])
    logger.info("run%s", t)
    time.sleep(t)
    return "java{}".format(t)


if __name__ == '__main__':
    logger.info("拿到结果%s", test_g())
