import json
import asyncio

import redis.asyncio as aioredis
from fastapi import WebSocket

from app.config import settings

CHANNEL = "inventory_events"


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._redis: aioredis.Redis | None = None
        self._subscriber_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(
                settings.redis_url,
                socket_connect_timeout=5,
                socket_keepalive=True,
                retry_on_timeout=True,
            )
        return self._redis

    async def _reset_redis(self):
        """Close stale connection so the next call creates a fresh one."""
        if self._redis:
            try:
                await self._redis.close()
            except Exception:
                pass
            self._redis = None

    async def publish(self, message: dict):
        """Publish an event to Redis so all workers receive it."""
        payload = json.dumps(message)
        for attempt in range(2):
            try:
                r = await self._get_redis()
                await r.publish(CHANNEL, payload)
                return
            except Exception:
                await self._reset_redis()
                if attempt == 1:
                    raise

    async def broadcast_local(self, message: dict):
        """Broadcast to WebSocket connections on this worker only."""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        for connection in dead_connections:
            self.disconnect(connection)

    async def start_subscriber(self):
        """Subscribe to Redis channel and broadcast messages to local WS connections.
        Automatically reconnects if the connection drops (e.g. Upstash idle timeout)."""
        while True:
            try:
                await self._reset_redis()
                r = await self._get_redis()
                pubsub = r.pubsub()
                await pubsub.subscribe(CHANNEL)
                async for raw_message in pubsub.listen():
                    if raw_message["type"] == "message":
                        try:
                            data = json.loads(raw_message["data"])
                            await self.broadcast_local(data)
                        except Exception:
                            pass
            except asyncio.CancelledError:
                try:
                    await pubsub.unsubscribe(CHANNEL)
                    await pubsub.close()
                except Exception:
                    pass
                raise
            except Exception as e:
                print(f"Redis subscriber error: {repr(e)}, reconnecting in 2s...")
                await asyncio.sleep(2)

    async def start(self):
        """Start the Redis subscriber as a background task."""
        self._subscriber_task = asyncio.create_task(self.start_subscriber())

    async def stop(self):
        """Stop the Redis subscriber and close connections."""
        if self._subscriber_task:
            self._subscriber_task.cancel()
            try:
                await self._subscriber_task
            except asyncio.CancelledError:
                pass
        if self._redis:
            await self._redis.close()


manager = ConnectionManager()
