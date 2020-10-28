from tyw.deploy.setting import *
from tyw.deploy.RedisUtils import *
from tyw.deploy.ResultBean import *
from tyw.deploy.constant import *
from tyw.deploy.run import log_save_root, app
import uuid
import time
import os
import os.path as osp

RESULT_KEY_PREFIX = 'result:'
FILES_ENCODE_KEY = 'files:name.encode'
FILES_MD5_KEY = 'files:md5'
FILES_LIST_KEY = 'files:list'
FILES_COUNT_KEY = 'files:count'
GRAPH_KEY_PREFIX = 'graph:'
PERSON_INFO_KEY_PREFIX = 'person.info:'
PERSON_FILE_LIST_PREFIX = 'person.fid:'

MD5_LOCK = 'md5'
GLOBAL_LOCK_PREFIX = 'global:'

VALID_CHARS = "/0123456789abcdefg"

pool = redis.ConnectionPool(host=redis_host, port=redis_port, decode_responses=True)


# 获取连接
def getConn():
    return redis.Redis(connection_pool=pool, db=redis_db)


# 判断 md5 是否存在，不是则存储
def isMd5Existed(md5):
    conn = getConn()
    locked = acquire_lock_with_timeout(conn, MD5_LOCK)
    if not locked:
        return create_fail_bean("nolock")  # 获取不到锁

    try:
        existed = conn.sismember(FILES_MD5_KEY, md5)
        if existed:
            return True
            # return create_bean(2, FILE_EXISTED_MSG, getFidByMd5(md5))  # md5 存在返回 fid
            # return create_fail_bean("existed")

        conn.sadd(FILES_MD5_KEY, md5)
        # return create_success_bean("ok")
        return False

    finally:
        release_lock(conn, MD5_LOCK, locked)


# 获取 MD5
def getMd5ById(fid):
    conn = getConn()
    result_key = RESULT_KEY_PREFIX + str(fid)
    locked = acquire_lock_with_timeout(conn, MD5_LOCK)
    if not locked:
        return ""

    try:
        return conn.hget(result_key, 'md5')
    finally:
        release_lock(conn, MD5_LOCK, locked)


# 删除 MD5
def deleteMd5(md5):
    conn = getConn()
    locked = acquire_lock_with_timeout(conn, MD5_LOCK)
    if not locked:
        return False

    try:
        conn.srem(FILES_MD5_KEY, md5)
        return True

    finally:
        release_lock(conn, MD5_LOCK, locked)


# 通过 MD5 获取 fid
def getFidByMd5(md5):
    return getConn().get('md5:' + md5)


# 删除全部记录，包括文件
def deleteRecordAll(fid):
    result_key = RESULT_KEY_PREFIX + str(fid)
    lock_name = GLOBAL_LOCK_PREFIX + str(fid)

    conn = getConn()
    locked = acquire_lock_with_timeout(conn, lock_name)

    if not locked:
        return create_fail_bean(GET_LOCK_FAIL_MSG)

    try:
        # 根据 id 拿到 MD5、filename 属性
        pipeline = conn.pipeline(True)
        pipeline.hmget(result_key, ['md5', 'filename'])
        attr = pipeline.execute()[0]
        md5 = attr[0]
        filename = attr[1]

        if md5 is None:
            return create_fail_bean("该文件已被删除")

        # 删除 fid MD5 filename result
        pipeline.multi()
        pipeline.srem(FILES_MD5_KEY, md5)
        filename_id = filename + ':' + fid
        pipeline.zrem(FILES_ENCODE_KEY, encoding(filename_id))
        pipeline.zrem(FILES_LIST_KEY, fid)
        pipeline.delete(result_key)
        res_arr = pipeline.execute()

        deleteFile(md5)

        return create_success_bean("删除成功")

    finally:
        release_lock(conn, lock_name, locked)


# 获取自增 id
def autoIncrementId():
    return getConn().incr(FILES_COUNT_KEY)


# 持久化文件属性（MD5，文件名，上传时间）
def setFileAttr(filename, md5):
    upload_timestamp = time.time()
    file_id = autoIncrementId()
    filename_id = filename + ':' + str(file_id)

    pipeline = getConn().pipeline(True)

    pipeline.set('md5:' + md5, file_id)  # 设置 MD5 和文件id 的映射
    pipeline.zadd(FILES_LIST_KEY, {file_id: upload_timestamp})  # 将id加入 files:list
    pipeline.zadd(FILES_ENCODE_KEY, {encoding(filename_id): 0})  # 将文件名:id编码后加入 files:name.encode
    pipeline.hmset(RESULT_KEY_PREFIX + str(file_id), {'id': file_id,
                                                      'md5': md5,
                                                      "filename": filename,
                                                      "upload_time": time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                   time.localtime(upload_timestamp))})
    pipeline.execute()
    return file_id


# 设置测试结果
def setResult(fid, result):
    conn = getConn()
    lock_name = GLOBAL_LOCK_PREFIX + str(fid)
    result_key = RESULT_KEY_PREFIX + str(fid)

    locked = acquire_lock_with_timeout(conn, lock_name)
    if not locked:
        return create_fail_bean(GET_LOCK_FAIL_MSG)

    # 指标名称
    titles = TABLE_ITEM[3:]

    try:
        pipeline = conn.pipeline(True)
        pipeline.exists(result_key)
        existed = pipeline.execute()[0]
        if existed != 1:
            return create_fail_bean(FILE_NOT_EXISTED_MSG)

        keys_mapping = {'trial_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}

        for title in titles:
            code_field = title + '.' + 'code'
            keys_mapping[title] = result[title]['state']
            keys_mapping[code_field] = str(result[title]['code'])
            # 设置 data
            # data_key = GRAPH_KEY_PREFIX + title + ':' + str(fid)
            # 本来打算用 list 来存放 data；现在将 [1,2,3] => '[1,2,3]'，存在 result:ID 里

        # 设置 state
        pipeline.hmset(result_key, keys_mapping)
        pipeline.execute()

        return create_success_bean("ok")

    finally:
        release_lock(conn, lock_name, locked)


# 获取 graph 数据
def getGraphData(fid):
    result_key = RESULT_KEY_PREFIX + str(fid)

    # 指标名称
    titles = TABLE_ITEM[3:]
    data_field = ['filename', 'trial_time']
    for title in titles:
        data_field.append(title + '.' + 'data')

    conn = getConn()
    if conn.exists(result_key) != 1:
        return create_fail_bean(FILE_NOT_EXISTED_MSG)

    res = conn.hmget(result_key, data_field)
    return create_success_data_bean(res)


# 获取全部结果
def getAllResult():
    # 这是之前用 set 存储文件名时，使用 sort 来获取结果的方法。
    # conn = getConn()
    # arr = conn.sort(FILES_NAME_KEY,
    #                 by=RESULT_KEY_PREFIX + '*->trial_time',
    #                 get=['#', RESULT_KEY_PREFIX + '*->trial_time', RESULT_KEY_PREFIX + '*->aa',
    #                      RESULT_KEY_PREFIX + '*->bb', RESULT_KEY_PREFIX + '*->cc'],
    #                 desc=True,
    #                 alpha=True)

    # 这是之前处理结果的关键代码
    # res = []
    # key = ['filename', 'trial_time', 'aa', 'bb', 'cc']
    # for i in range(0, len(arr) // result_count):
    #     j = i * result_count
    #     sub_arr = arr[j:j + result_count]
    #     res.append(dict(zip(key, sub_arr)))
    #
    # return res

    pipeline = getConn().pipeline(True)

    pipeline.zrevrange(FILES_LIST_KEY, 0, -1)
    file_ids = pipeline.execute()[0]

    for fid in file_ids:
        result_key = RESULT_KEY_PREFIX + fid
        pipeline.hmget(result_key, ALL_RESULT_ITEM)

    items = pipeline.execute()

    res = []
    for item in items:
        res.append(dict(zip(ALL_RESULT_ITEM, item)))

    return res


# 获取搜索结果
def getSearchResult(prefix):
    conn = getConn()
    pipeline = conn.pipeline()
    items = auto_complete(prefix)

    for i in range(0, len(items)):
        filename = decoding(items[i])
        fid = filename[filename.rfind(':') + 1:]
        items[i] = filename
        pipeline.hgetall(RESULT_KEY_PREFIX + fid)

    res = pipeline.execute()
    for i in range(0, len(items)):
        item_idx = items[i].rfind(':')
        res[i]['filename'] = items[i][:item_idx]

    rev_res = []
    for i in range(len(res) - 1, -1, -1):
        rev_res.append(res[i])

    return rev_res


# 根据前缀自动补全
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


# 寻找前缀在 zset 中的范围
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


# 删除文件
def deleteFile(md5):
    file_dir = osp.join(log_save_root, app.config['UPLOAD_FOLDER'])
    file_path = file_dir + '/' + md5 + '.pkl'
    if not osp.exists(file_dir):
        return False
    os.remove(file_path)
    return True


# 获取配置信息
def getPersonInfo(username):
    return getConn().hgetall(PERSON_INFO_KEY_PREFIX + username)


# 获取体态文件名
def getBodyFileName(username):
    return getConn().hget(PERSON_INFO_KEY_PREFIX + username, 'body_filename')


# 配置信息
def setPersonInfo(username, age, min_beats, max_beats):
    getConn().hmset(PERSON_INFO_KEY_PREFIX + username, {'username': username,
                                                        'age': age,
                                                        'min_beats': min_beats,
                                                        'max_beats': max_beats})


# 设置体态文件名到配置信息
def setBodyFileAttr(username, filename):
    getConn().hset(PERSON_INFO_KEY_PREFIX + username, "body_filename", filename)


# 设置最小心率
def setMinBeats(username, min_beats):
    getConn().hset(PERSON_INFO_KEY_PREFIX + username, "min_beats", min_beats)

