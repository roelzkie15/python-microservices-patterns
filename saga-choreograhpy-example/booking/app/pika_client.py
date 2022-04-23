import aio_pika

from app.dependencies import get_settings


async def init_pika_client(loop = None) -> None:
    settings = get_settings()
    return await aio_pika.connect_robust(
        settings.RABBITMQ_BROKER_URL, loop=loop
    )
