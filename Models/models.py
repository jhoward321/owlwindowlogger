from peewee import *
from datetime import datetime

db = SqliteDatabase('logrecords.db')

class BaseModel(Model):
    class Meta:
        database = db

class TrackingSession(BaseModel):
    start_time = DateTimeField(null=False, default=datetime.utcnow())
    end_time = DateTimeField(null=True)

class WindowRecord(BaseModel):
    tracking_session = ForeignKeyField(TrackingSession)
    process_name = CharField()
    window_title = CharField()
    pid = IntegerField()
    idle_time = DoubleField()
    start_time = DateTimeField(default=datetime.utcnow())
    end_time = DateTimeField()

# db.connect()
db.create_tables([TrackingSession, WindowRecord], safe=True)