from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.utils.config import settings


broker = ListQueueBroker(url=settings.redis.redis_url).with_result_backend(
    RedisAsyncResultBackend(settings.redis.redis_url)
)
