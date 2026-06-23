import time
import uuid
from typing import Optional

from open_webui.internal.db import Base, JSONField, get_async_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession


class WebhookDelivery(Base):
    __tablename__ = 'webhook_delivery'

    id = Column(Text, primary_key=True, unique=True)
    url = Column(Text, nullable=False)
    name = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    event_data = Column(JSONField, nullable=True)
    status = Column(Text, nullable=False, default='pending') # pending, success, failed
    retries = Column(Integer, nullable=False, default=0)
    error = Column(Text, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class WebhookDeliveryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: Optional[str] = None
    message: Optional[str] = None
    event_data: Optional[dict] = None
    status: str
    retries: int
    error: Optional[str] = None

    created_at: int
    updated_at: int


class WebhookDeliveriesTable:
    async def insert_new_delivery(self, url: str, name: str, message: str, event_data: dict, db: Optional[AsyncSession] = None) -> WebhookDeliveryModel:
        async with get_async_db_context(db) as db:
            delivery = WebhookDelivery(
                id=str(uuid.uuid4()),
                url=url,
                name=name,
                message=message,
                event_data=event_data,
                status='pending',
                retries=0,
                error=None,
                created_at=int(time.time_ns()),
                updated_at=int(time.time_ns())
            )
            db.add(delivery)
            await db.commit()
            return WebhookDeliveryModel.model_validate(delivery)

    async def get_deliveries(self, db: Optional[AsyncSession] = None) -> list[WebhookDeliveryModel]:
        async with get_async_db_context(db) as db:
            result = await db.execute(select(WebhookDelivery).order_by(WebhookDelivery.created_at.desc()))
            deliveries = result.scalars().all()
            return [WebhookDeliveryModel.model_validate(delivery) for delivery in deliveries]

    async def get_pending_deliveries(self, db: Optional[AsyncSession] = None) -> list[WebhookDeliveryModel]:
        async with get_async_db_context(db) as db:
            result = await db.execute(select(WebhookDelivery).filter(WebhookDelivery.status == 'pending'))
            deliveries = result.scalars().all()
            return [WebhookDeliveryModel.model_validate(delivery) for delivery in deliveries]

    async def update_delivery(self, delivery_id: str, status: str, retries: int, error: Optional[str] = None, db: Optional[AsyncSession] = None) -> Optional[WebhookDeliveryModel]:
        async with get_async_db_context(db) as db:
            result = await db.execute(select(WebhookDelivery).filter(WebhookDelivery.id == delivery_id))
            delivery = result.scalars().first()
            if delivery:
                delivery.status = status
                delivery.retries = retries
                delivery.error = error
                delivery.updated_at = int(time.time_ns())
                await db.commit()
                return WebhookDeliveryModel.model_validate(delivery)
            return None

WebhookDeliveries = WebhookDeliveriesTable()
