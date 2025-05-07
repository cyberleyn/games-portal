from peewee import *

pg_db = PostgresqlDatabase('itemexchanger', user='postgres', password='0000', host='localhost', port=5432)


class User(Model):
    username = CharField()
    password = CharField()
    nickname = CharField()
    avatar = CharField(default="https://cdn3.iconfinder.com/data/icons/avatars-15/64/_Ninja-2-1024.png")
    steam = CharField(null=True)

    class Meta:
        database = pg_db

    @staticmethod
    def create_user(username, password, nickname):
        user = User()
        user.username = username
        user.password = password
        user.nickname = nickname
        user.save()
        return user


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
    def sent_steamlink(user, link):
        if User.select().where(User.id == user.id).exists():
            updating_query = {'steam': link}
            query = User.update(updating_query).where(User.id == user.id)
            query.execute()


    @staticmethod
    def get_user_by_id(userid):
        query = User.select().where(User.id == userid)
        if query.exists():
            return query.get()


class Pending_invite(Model):
    from_user = ForeignKeyField(User, backref='outgoing_invites')
    to_user = ForeignKeyField(User, backref='incoming_invites')
    class Meta:
        database = pg_db

    @staticmethod
    def create_invite(user_from, user_to):
        query = Pending_invite.select().where(
            (Pending_invite.from_user == user_from),  # Первое условие
            (Pending_invite.to_user == user_to)  # Второе условие
        )
        if query.exists():
            return None
        invite = Pending_invite()
        invite.from_user = user_from
        invite.to_user = user_to
        invite.save()
        return invite

    @staticmethod
    def delete_invite(invite):
        query = Pending_invite.delete().where(Pending_invite.id == invite.id)
        query.execute()


class User_friend(Model):
    user1 = ForeignKeyField(User, backref='friendships')
    user2 = ForeignKeyField(User, backref='friendships')
    class Meta:
        database = pg_db

    @staticmethod
    def create_friendship(user1, user2):
        friendship = User_friend()
        friendship.user1 = user1
        friendship.user2 = user2
        friendship.save()

