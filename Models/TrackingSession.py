# look at apsw
from peewee import *
import BaseModel

#todo: look at sqlite plugins
db = SqliteDatabase('test.db')

class TrackingSession(BaseModel):
    start_time = DateTimeField()
    end_time = DateTimeField()
    # records = 

    class Meta:
        database = db

db.connect()