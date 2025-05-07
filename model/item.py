from peewee import *

from helpers.itemtag import ItemTag
from model.user import User

pg_db = PostgresqlDatabase('itemexchanger', user='postgres', password='0000', host='localhost', port=5432)


class Item(Model):
    owner = ForeignKeyField(User, backref='items')
    name = CharField()
    item_type = CharField()
    float = CharField(null=True)
    inspect_link = CharField(null=True)
    class_id = CharField()
    image = CharField()
    bg_color = CharField()


    class Meta:
        database = pg_db

    @staticmethod
    def create_item_from_json(user, json):
        item = Item()
        item.owner = user
        item.name = json["name"]
        item.item_type = json["type"]
        tags = []
        for elem in json["tags"]:
            tags.append(ItemTag().from_json(elem))
        backgroundColor = ""
        for elem in tags:
            if elem.category == "Rarity":
                backgroundColor = elem.color
            if elem.category == "Exterior":
                elem.float = elem.localized_tag_name
        item.bg_color = backgroundColor
        try:
            item.inspect_link = json["actions"][0]["link"]
        except KeyError:
            item.inspect_link = None
        item.class_id = json["classid"]
        item.image = "https://steamcommunity-a.akamaihd.net/economy/image/class/730/" + item.class_id + "/193fx145f"
        item.save()
        return item


    @staticmethod
    def get_user_by_name(username):
        query = User.select().where(User.username == username)
        if query.exists():
            return query.get()

    @staticmethod
    def update_user(user, username=None, password=None, nickname=None, avatar=None):
        if User.select().where(User.username == user.username, User.password == user.password, User.nickname == user.nickname,
                                 User.avatar == user.avatar).exists():
            updating_query = {}
            if username:
                updating_query['username'] = username
            if password:
                updating_query['password'] = password
            if nickname:
                updating_query['nickname'] = nickname
            if avatar:
                updating_query['avatar'] = avatar
            query = User.update(updating_query).where(User.username == user.username, User.password == user.password, User.nickname == user.nickname,
                                 User.avatar == user.avatar)
            query.execute()

    @staticmethod
    def get_user_by_id(userid):
        query = User.select().where(User.id == userid)
        if query.exists():
            return query.get()

