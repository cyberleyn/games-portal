from peewee import *

from helpers.itemtag import ItemTag
from model.user import User

pg_db = PostgresqlDatabase('itemexchanger', user='postgres', password='0000', host='localhost', port=5432)


class Game(Model):
    owner = ForeignKeyField(User, backref='games')
    app_id = IntegerField()
    name = CharField()
    playtime_forever = IntegerField()
    img_icon_url = CharField(max_length = 400)


    class Meta:
        database = pg_db

    @staticmethod
    def create_game_from_json(user, json):
        game = Game()
        game.owner = user
        game.app_id = json["appid"]
        game.name = json["name"]
        game.playtime_forever = json["playtime_forever"]
        game.img_icon_url = "http://media.steampowered.com/steamcommunity/public/images/apps/" + str(json["appid"]) + "/" \
                            + json["img_icon_url"] + ".jpg"
        game.save()
        return game