# look at apsw
from peewee import *

#todo: look at sqlite plugins
db = SqliteDatabase('test.db')

class BaseModel(Model):
    class Meta:
        database = db