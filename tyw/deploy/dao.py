import redis
from tyw.deploy.setting import *
import uuid

RESULT_KEY_PREFIX = 'result:'
FILES_NAME_KEY = "files:name"
FILES_ENCODE_KEY = 'files:encode'

VALID_CHARS = "/0123456789abcdefg"

pool = redis.ConnectionPool(host=redis_host, port=redis_port, decode_responses=True)


def getConn():
    return redis.Redis(connection_pool=pool, db=redis_db)


def setResult(filename, attr, result):
    pipeline = getConn().pipeline(True)
    pipeline.sadd(FILES_NAME_KEY, filename)
    pipeline.zadd(FILES_ENCODE_KEY, {encoding(filename): 0})
    pipeline.hmset(RESULT_KEY_PREFIX + filename, attr)
    pipeline.hmset(RESULT_KEY_PREFIX + filename, result)
    pipeline.execute()


def getAllResult():
    conn = getConn()
    arr = conn.sort(FILES_NAME_KEY,
                    by=RESULT_KEY_PREFIX + '*->trial_time',
                    get=['#', RESULT_KEY_PREFIX + '*->trial_time', RESULT_KEY_PREFIX + '*->aa',
                         RESULT_KEY_PREFIX + '*->bb', RESULT_KEY_PREFIX + '*->cc'],
                    desc=True,
                    alpha=True)

    res = []
    key = ['filename', 'trial_time', 'aa', 'bb', 'cc']
    for i in range(0, len(arr) // result_count):
        j = i * result_count
        sub_arr = arr[j:j + result_count]
        res.append(dict(zip(key, sub_arr)))

    return res


def getSearchResult(prefix):
    conn = getConn()
    pipeline = conn.pipeline()
    items = auto_complete(prefix)
    # for i in range(0, len(items)):
    for i in range(0, len(items)):
        filename = decoding(items[i])
        items[i] = filename
        pipeline.hgetall(RESULT_KEY_PREFIX + filename)

    res = pipeline.execute()
    for i in range(0, len(items)):
        res[i]['filename'] = items[i]

    rev_res = []
    for i in range(len(res) - 1, -1, -1):
        rev_res.append(res[i])

    return rev_res


def auto_complete(prefix):
    find_range = findPrefixRange(prefix)
    identifier = str(uuid.uuid4()).replace('-', '')
    start = find_range[0] + identifier
    end = find_range[1] + identifier
    zset_name = FILES_ENCODE_KEY
    conn = getConn()
    conn.zadd(zset_name, {start: 0, end: 0})
    pipeline = conn.pipeline(True)
    while 1:
        try:
            pipeline.watch(zset_name)
            start_idx = pipeline.zrank(zset_name, start)
            end_idx = pipeline.zrank(zset_name, end)
            # 最多展示 10 个
            # erange = min(start_idx + 9, end_idx - 2)
            erange = end_idx - 2
            pipeline.multi()
            pipeline.zrem(zset_name, start, end)

            if erange < 0:
                pipeline.execute()
                return []

            pipeline.zrange(zset_name, start_idx, erange)
            items = pipeline.execute()[-1]
            break
        except redis.exceptions.WatchError:
            continue

    # 把带g的去掉，因为有可能此时有其他客户端在搜索，插入了首尾元素
    return [item for item in items if 'g' not in item]


def findPrefixRange(prefix):
    prefix = encoding(prefix)
    pos = VALID_CHARS.index(prefix[-1])
    suffix = VALID_CHARS[0] if pos <= 0 else VALID_CHARS[pos - 1]
    start = prefix[:-1] + suffix + 'g'
    end = prefix + 'g'
    return [start, end]


# 编码，对字符的ASCII进行16进制编码
def encoding(s):
    result = ''
    for c in s:
        result = result + hex(ord(c))[2:] + '-'
    result = result[:-1]
    return result


# 解码
def decoding(s):
    result = ''
    for subst in s.split('-'):
        if subst.strip() != '':
            result += chr(int(subst, 16))
    return result
