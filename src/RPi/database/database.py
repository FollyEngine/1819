#!/usr/bin/python3

# set up initial game database

from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model
import json
import datetime

# http://docs.peewee-orm.com/en/latest/


db = SqliteDatabase('thegame.db')

class BaseModel(Model):
    class Meta:
        database = db

class MagicItem(BaseModel):
    uhf = CharField(unique=True)
    nfc = CharField(unique=True)
    name = CharField(default="")
    Fire = IntegerField(default=10)
    Earth = IntegerField(default=10)
    Air = IntegerField(default=10)
    Water = IntegerField(default=10)

class IngredientItem(BaseModel):
    uhf = CharField(unique=True)
    name = CharField(default="")
    Fire = IntegerField(default=0)
    Earth = IntegerField(default=0)
    Air = IntegerField(default=0)
    Water = IntegerField(default=0)

# class IngredientsTryed(BaseModel):
#     nfc = ForeignKeyField(MagicItem, backref='nfc')
#     ingredient1 = ForeignKeyField(IngredientItem, backref='uhf')
#     ingredient2 = ForeignKeyField(IngredientItem, backref='uhf')


def database_init():
    db.connect()
    db.create_tables([MagicItem, IngredientItem])
    return db

def database_close():
    db.commit()
