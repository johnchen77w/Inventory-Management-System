import asyncio
import json
import os

import redis.asyncio as redis

from app.services.ws_manager import manager

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CHANNEL_NAME = "inventory_updates"

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


async def publish_event(event: dict):
    await redis_client.publish(CHANNEL_NAME, json.dumps(event))


async def redis_listener():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(CHANNEL_NAME)

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            data = json.loads(message["data"])
            await manager.broadcast(data)
    except asyncio.CancelledError:
        await pubsub.unsubscribe(CHANNEL_NAME)
        await pubsub.close()
        raise