import datetime

from peewee import *

from model.item import Item
from model.user import User

pg_db = PostgresqlDatabase('itemexchanger', user='postgres', password='0000', host='localhost', port=5432)


class TradeOffer(Model):
    sender = ForeignKeyField(User, backref='sent_offers')
    receiver = ForeignKeyField(User, backref='received_offers')
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = pg_db

    @staticmethod
    def create_offer(sender, receiver, items):
        tradeoffer = TradeOffer()
        tradeoffer.sender = sender
        tradeoffer.receiver = receiver
        tradeoffer.save()
        for item in items:
            tradeofferitem = TradeOfferItem()
            tradeofferitem.trade_offer = tradeoffer
            tradeofferitem.item = item
            tradeofferitem.save()

    @staticmethod
    def delete_offer(tradeoffer):
        offer_to_delete = TradeOffer.get(TradeOffer.id == tradeoffer.id)
        related_items = TradeOfferItem.select().where(TradeOfferItem.trade_offer_id == offer_to_delete.id)

        # Delete related items
        for item in related_items:
            item.delete_instance()
        offer_to_delete.delete_instance()


    @staticmethod
    def get_offer_by_id(id):
        query = TradeOffer.select().where(TradeOffer.id == id)
        if query.exists():
            return query.get()


class TradeOfferItem(Model):
    trade_offer = ForeignKeyField(TradeOffer, backref='items')
    item = ForeignKeyField(Item, backref='trade_offers')

    class Meta:
        database = pg_db


TradeOffer.items = ManyToManyField(Item, through_model=TradeOfferItem, backref='trade_offers')
