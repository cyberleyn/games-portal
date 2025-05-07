import requests
from flask import request
from peewee import JOIN
from werkzeug.security import generate_password_hash, check_password_hash

from helpers.validatesteam import get_steamid64
from model.game import Game
from model.item import Item
from model.tradeoffer import TradeOffer, TradeOfferItem
from model.user import User, Pending_invite, User_friend

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/37.0.2062.120 Safari/537.36'}


class Repository:

    @staticmethod
    def register_manual(username, password, nickname):
        User.create_user(username=username, password=generate_password_hash(password), nickname=nickname)


    @staticmethod
    def auth(username, password):
        user = User.get_user_by_name(username)
        if user is None:
            return {"user": user, "success": False}
        if check_password_hash(user.password, password):
            return {"user": user, "success": True}
        else:
            return {"user": user, "success": False}

    @staticmethod
    def register():
        username = request.form.get("uname")
        password = generate_password_hash(request.form.get("psw"))
        nickname = request.form.get("nickname")
        avatar = request.form.get("avatar")
        user = User.create_user(username, password, nickname, avatar)
        return user

    @staticmethod
    def get_user_by_id(userid):
        return User.get_user_by_id(userid)

    @staticmethod
    def get_user_by_name(username):
        return User.get_user_by_name(username)

    @staticmethod
    def save_user_changes(user):
        nickname = request.form.get("user-nickname")
        avatar = request.form.get("user-avatar")
        User.update_user(user, nickname=nickname, avatar=avatar)

    @staticmethod
    def can_edit(userid):
        cookie = request.cookies.get("user")
        if not cookie:
            return False
        return int(cookie) == int(userid)

    @staticmethod
    def add_friend(userid, friendid):
        user = User.get_user_by_id(userid)
        friend = User.get_user_by_id(friendid)
        return Pending_invite.create_invite(user, friend)

    @staticmethod
    def get_pending_invites(user):
        pendings = []
        for invite in user.incoming_invites:
            print(type(invite.from_user))
            pendings.append(invite)
        return pendings

    @staticmethod
    def accept_invite(inviteid):
        invite = Pending_invite.select().where(Pending_invite.id == inviteid).get()
        User_friend.create_friendship(invite.from_user, invite.to_user)
        Pending_invite.delete_invite(invite)

    @staticmethod
    def decline_invite(inviteid):
        invite = Pending_invite.select().where(Pending_invite.id == inviteid).get()
        Pending_invite.delete_invite(invite)

    @staticmethod
    def connect_steam(userid, link):
        user = User.get_user_by_id(userid)
        steam_id64 = get_steamid64(link)
        link = "https://steamcommunity.com/inventory/" + steam_id64 + "/730/2"
        games = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=EBC3BF7531236D84C2330A0AFD33F13A&steamid=" \
                + steam_id64 + "&include_appinfo=true&format=json"
        print(link)
        if steam_id64 is None:
            return
        response = requests.get(url=link, headers=HEADERS).json()
        try:
            items_count = response["total_inventory_count"]
            print(type(items_count))
            if items_count == 0:
                return
        except BaseException:
            pass
        try:

            for item in response["descriptions"]:
                Item().create_item_from_json(user, item)
        except TypeError:
            return
        response = requests.get(url=games, headers=HEADERS).json()
        try:

            for item in response["response"]["games"]:
                Game().create_game_from_json(user, item)
        except TypeError:
            return
        User().sent_steamlink(user, link)
        return

    @staticmethod
    def get_user_inventory(userid):
        user = User.get_user_by_id(userid)
        items = []
        for item in user.items:
            items.append(item)
        return items

    @staticmethod
    def get_friends(user):
        query = User_friend.select().where(
            (User_friend.user1 == user) | (User_friend.user2 == user)
        )
        friends = []
        for friendship in query:
            if friendship.user1 == user:
                friends.append(friendship.user2)
            else:
                friends.append(friendship.user1)

        return friends

    @staticmethod
    def check_friendship(userid):
        current_user = request.cookies.get("user")
        if not current_user:
            # Handle case if the user is not logged in
            return {"status": "not_logged_in", "invite": None}

        if userid == current_user:
            return {"status": "me", "invite": None}

        target = User.get_user_by_id(userid)
        user = User.get_user_by_id(current_user)

        # Check incoming invites
        for invite in user.incoming_invites:
            if invite.from_user.id == target.id:
                return {"status": "incoming", "invite": invite}

        # Check outgoing invites
        for invite in user.outgoing_invites:
            if invite.from_user.id == target.id:
                return {"status": "outgoing", "invite": invite}

        # Check if they are already friends
        for friend in target.friendships:
            if friend.user1 == user or friend.user2 == user:
                return {"status": "friends", "invite": None}

        # No relationship found
        return {"status": "not_friends", "invite": None}


    @staticmethod
    def create_offer(sender, receiver, items):
        TradeOffer().create_offer(sender, receiver, items)


    @staticmethod
    def get_offers(user):
        query = TradeOffer.select().where(
            (TradeOffer.sender == user) | (TradeOffer.receiver == user)
        )
        result = []
        for item in query:
            offer = {"id": item.id, "sender": item.sender, "receiver": item.receiver, "sender_items": [], "receiver_items": []}
            trade_offer_items = (TradeOfferItem
                                 .select(TradeOfferItem, Item)
                                 .join(Item)
                                 .where(TradeOfferItem.trade_offer == item))

            # Выводим информацию о предметах в предложении обмена
            for trade_offer_item in trade_offer_items:
                print(f"Item ID: {trade_offer_item.item.id}")
                print(f"Item Name: {trade_offer_item.item.name}")
                if trade_offer_item.item.owner == item.sender:
                    offer["sender_items"].append(trade_offer_item.item)
                else:
                    offer["receiver_items"].append(trade_offer_item.item)
            result.append(offer)
        print(result)
        return result


    @staticmethod
    def accept_offer(tradeoffer):
        trade_offer_items = (TradeOfferItem
                             .select(TradeOfferItem, Item)
                             .join(Item)
                             .where(TradeOfferItem.trade_offer == tradeoffer))
        for skin in trade_offer_items:
            if skin.item.owner == tradeoffer.sender:
                # Query the record you want to update
                skin_to_update = Item.get(Item.id == skin.item.id)

                # Update the record
                skin_to_update.owner = tradeoffer.receiver
                skin_to_update.save()

            else:
                # Query the record you want to update
                skin_to_update = Item.get(Item.id == skin.item.id)

                # Update the record
                skin_to_update.owner = tradeoffer.sender
                skin_to_update.save()
        TradeOffer.delete_offer(tradeoffer)

    @staticmethod
    def delete_offer(tradeoffer):
        TradeOffer.delete_offer(tradeoffer)


    @staticmethod
    def get_offer_by_id(id):
        return TradeOffer.get_offer_by_id(id)


    @staticmethod
    def get_all_users():
        return [user for user in User.select()]

    @staticmethod
    def get_user_games(userid):
        user = User.get_user_by_id(userid)
        items = []
        for item in user.games:
            items.append(item)
        return items
