# from peewee import *
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, DateTime, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# import sqlalchemy as sql
from datetime import datetime

# db = SqliteDatabase('logrecords.db')
db = create_engine('logrecords.db')

# class BaseModel(Model):
#     class Meta:
#         database = db
Base = declarative_base()

#todo: turn this into classic mode, finish building relationship
class TrackingSession(Base):
    __tablename__ = 'sessions'

    id=Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow())
    end_time = Column(DateTime, nullable=True)

class WindowRecord(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    tracking_session = relationship("TrackingSession")#ForeignKeyField(TrackingSession)
    process_name = Column(String)
    window_title = Column(String)
    pid = Column(Integer)
    idle_time = Column(DECIMAL)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow())
    end_time = Column(DateTime)

# db.connect()
# db.create_tables([TrackingSession, WindowRecord], safe=True)