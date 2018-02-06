from datetime import datetime

from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# db = SqliteDatabase('logrecords.db')
# db_engine = create_engine('sqlite:///logrecords.db')
# Session = sessionmaker().configure(bind=db_engine, autocommit=True)

Base = declarative_base()

# todo: turn this into classic mode


class TrackingSession(Base):

    """Model representing an overall tracking session

    Attributes:
        end_time (Datetime): End of tracking session
        id (Integer): Id in database
        records (WindowRecord): List of window records recorded during this tracking session
        start_time (Datetime): Start of tracking session
    """

    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow())
    end_time = Column(DateTime, nullable=True)
    records = relationship(
        "WindowRecord", back_populates="tracking_session", cascade="all, delete, delete-orphan")


class WindowRecord(Base):

    """Model representing a tracking record of active application

    Attributes:
        end_time (Datetime): End of windows tracking record
        id (Integer): Id in database
        idle_time (Float): Number of seconds this window was idle
        pid (Integer): Associated PID of this window
        process_name (String): Associated process name
        start_time (Datetime): Start time of record
        tracking_id (Integer): Id of parent tracking session
        tracking_session (TrackingSession): Parent tracking session
        window_title (String): Window title
    """

    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    tracking_id = Column(Integer, ForeignKey('sessions.id'))
    tracking_session = relationship(
        "TrackingSession", back_populates="records")

    process_name = Column(String)
    window_title = Column(String)
    pid = Column(Integer)
    idle_time = Column(Float)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow())
    end_time = Column(DateTime)
