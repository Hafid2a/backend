from pydantic import BaseModel
import uuid


class TrackingEventOut(BaseModel):
    id: uuid.UUID
    platform: str
    event_name: str
    event_id: str
    status: str

    model_config = {"from_attributes": True}
