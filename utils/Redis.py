import json

import redis
from django.conf import settings


class RedisManager:
    """
    Singleton Redis connection pool manager with helper methods
    for common Key-Value and Queue operations.

    Settings required in settings.py:
        REDIS_HOST (str): Redis server host (default: "localhost")
        REDIS_PORT (int): Redis server port (default: 6379)
        REDIS_PASSWORD (str|None): Redis password (default: None)
        REDIS_DATABASES (dict): Mapping of database names to numbers
            e.g. {"otp": 0, "cache": 1, "session": 2}

    Usage:
        from utils.Redis import redis_manager
        redis_manager.set_data("otp", "user:123", "048371", expire=120)
        redis_manager.get_data("otp", "user:123")
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._pools = {}
        return cls._instance

    @property
    def _host(self):
        return getattr(settings, "REDIS_HOST", "localhost")

    @property
    def _port(self):
        return getattr(settings, "REDIS_PORT", 6379)

    @property
    def _password(self):
        return getattr(settings, "REDIS_PASSWORD", None)

    @property
    def _databases(self):
        return getattr(settings, "REDIS_DATABASES", {})

    def get_client(self, name):
        """
        Get a raw redis.Redis client for a named database.

        Args:
            name (str): The database name defined in settings.REDIS_DATABASES

        Returns:
            redis.Redis: A Redis client connected via connection pool

        Raises:
            ValueError: If the database name is not defined in REDIS_DATABASES
        """
        if name not in self._databases:
            raise ValueError(
                f"Redis database '{name}' is not defined in REDIS_DATABASES. "
                f"Available databases: {list(self._databases.keys())}"
            )

        if name not in self._pools:
            db_number = self._databases[name]
            self._pools[name] = redis.ConnectionPool(
                host=self._host,
                port=self._port,
                password=self._password,
                db=db_number,
                decode_responses=True,
            )

        return redis.Redis(connection_pool=self._pools[name])

    # -------------------------
    # Key-Value operations
    # -------------------------
    def set_data(self, name, key, data, expire=None):
        # set data into redis database
        try:
            self.get_client(name).set(key, json.dumps(data), ex=expire)
        except Exception as e:
            raise RuntimeError(f"Redis SET failed: {e}") from e

    def get_data(self, name, key):
        # get data from redis database
        try:
            data = self.get_client(name).get(key)
            return json.loads(data) if data else None
        except json.JSONDecodeError:
            return None
        except Exception as e:
            raise RuntimeError(f"Redis GET failed: {e}") from e

    def delete_data(self, name, key):
        # delete data from redis
        self.get_client(name).delete(key)

    # -------------------------
    # Queue operations (List)
    # -------------------------
    def push_queue(self, name, queue_name, data):
        # Push item to queue (left push)
        self.get_client(name).lpush(queue_name, json.dumps(data))

    def pop_queue(self, name, queue_name):
        # Pop item from queue (right pop)
        data = self.get_client(name).rpop(queue_name)
        return json.loads(data) if data else None

    def get_length(self, name, queue_name):
        return self.get_client(name).llen(queue_name)

    def get_items(self, name, queue_name, start=0, end=-1):
        # Get range of items from queue
        items = self.get_client(name).lrange(queue_name, start, end)
        return [json.loads(item) for item in items]

    def trim_redis(self, name, queue_name, length):
        if not length or length <= 0:
            return
        return self.get_client(name).ltrim(queue_name, length, -1)


redis_manager = RedisManager()
