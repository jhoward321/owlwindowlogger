from peewee import *
import BaseModel
import TrackingSession

class WindowRecord(BaseModel):
    tracking_session = ForeignKeyField(TrackingSession)
    