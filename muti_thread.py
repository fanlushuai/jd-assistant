import functools
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

# 提前初始化好
thread_pool = ThreadPoolExecutor(max_workers=30)


def threads(concurrent_size, timeout=0):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            futures = []
            for i in range(concurrent_size):
                # 向线程池提交任务。
                futures.append(thread_pool.submit(func, *args, **kw))
            for _ in repeat(None):
                for i in futures:
                    if i.done():
                        result = i.result()
                        return result
            return None

        return wrapper

    return decorate
