import time
import random
import logging
from datetime import datetime, date
import json
from banal.dicts import clean_dict


QUEUE_EXPIRE = 84600 * 14
log = logging.getLogger(__name__)


def backoff(failures=0):
    """Implement a random, growing delay between external service retries."""
    sleep = max(1, failures - 1) + random.random()
    log.debug("Back-off: %.2fs", sleep)
    time.sleep(sleep)


def service_retries():
    """A default number of tries to re-try an external service."""
    return range(30)


def unpack_int(value):
    try:
        return int(value)
    except Exception:
        return 0


def pack_datetime(value):
    if value is not None:
        return str(value)


def pack_now():
    return pack_datetime(datetime.utcnow())


def unpack_datetime(value, default=None):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return default


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        if isinstance(obj, set):
            return [o for o in obj]
        return json.JSONEncoder.default(self, obj)


def dump_json(data):
    if data is None:
        return ''
    data = clean_dict(data)
    return JSONEncoder().encode(data)


def load_json(encoded):
    if encoded is None or encoded == '':
        return
    return json.loads(encoded)
