from taskiq_redis import ListQueueBroker

from app.utils.config import settings


broker = ListQueueBroker(
    url=settings.redis.redis_url,
    socket_timeout=None,
    socket_connect_timeout=10,
)
