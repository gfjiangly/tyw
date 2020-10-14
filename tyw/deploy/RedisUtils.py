import uuid
import time
import math
import redis


# redis lock

# 获取锁
def acquire_lock(conn, lock_name, acquire_timeout=10):
    identifier = str(uuid.uuid4())
    end = time.time() + acquire_timeout
    while time.time() < end:
        if conn.settnx('lock:' + lock_name, identifier):
            return identifier
        time.sleep(.001)
    return False


# 带有超时限制特性的锁
def acquire_lock_with_timeout(conn, lock_name, acquired_timeout=10, lock_timeout=10):
    identifier = str(uuid.uuid4())
    lock_name = 'lock:' + lock_name
    lock_timeout = int(math.ceil(lock_timeout))  # 确保传给 EXPIRE 的都是整数

    end = time.time() + acquired_timeout
    while time.time() < end:
        if conn.setnx(lock_name, identifier):
            conn.expire(lock_name, lock_timeout)
            return identifier
        elif not conn.ttl(lock_name):
            conn.expire(lock_name, lock_timeout)

        time.sleep(.001)

    return False


# 释放锁
def release_lock(conn, lock_name, identifier):
    pipe = conn.pipeline(True)
    lock_name = 'lock:' + lock_name
    while True:
        try:
            pipe.watch(lock_name)
            if pipe.get(lock_name) == identifier:
                pipe.multi()
                pipe.delete(lock_name)
                pipe.execute()
                return True

            pipe.unwatch()
            break

        # 有其他客户端修改锁，重试
        except redis.exceptions.WatchError:
            pass

    return False
