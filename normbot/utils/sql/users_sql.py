import threading

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    UnicodeText,
    UniqueConstraint,
    func,
    Numeric,
    TEXT,
)

from normbot import dispatcher
from normbot.utils.sql import BASE, SESSION


class Users(BASE):
    __tablename__ = "botusers"
    id = Column(Numeric, primary_key=True)
    user_name = Column(TEXT)

    def __init__(self, id, user_name):
        self.id = id
        self.user_name = user_name

class Chats(BASE):
    __tablename__ = "chats"
    chat_id = Column(String(14), primary_key=True)
    chat_name = Column(UnicodeText, nullable=False)

    def __init__(self, chat_id, chat_name):
        self.chat_id = str(chat_id)
        self.chat_name = chat_name

    def __repr__(self):
        return "<Chat {} ({})>".format(self.chat_name, self.chat_id)


class ChatMembers(BASE):
    __tablename__ = "chat_members"
    priv_chat_id = Column(Numeric, primary_key=True)
    # NOTE: Use dual primary key instead of private primary key?
    chat = Column(
        String(14),
        ForeignKey("chats.chat_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    user = Column(
        Numeric,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    __table_args__ = (UniqueConstraint("chat", "user", name="_chat_members_uc"),)

    def __init__(self, chat, user):
        self.chat = chat
        self.user = user

    def __repr__(self):
        return "<Chat user {} ({}) in chat {} ({})>".format(
            self.user.username,
            self.user.id,
            self.chat.chat_name,
            self.chat.chat_id,
        )


Users.__table__.create(checkfirst=True)
Chats.__table__.create(checkfirst=True)
ChatMembers.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()


def ensure_bot_in_db():
    with INSERTION_LOCK:
        bot = Users(dispatcher.bot.id, dispatcher.bot.username)
        SESSION.merge(bot)
        SESSION.commit()

def update_user(id, user_name):
    with INSERTION_LOCK:
        msg = SESSION.query(Users).get(id)
        if not msg:
            usr = Users(id, user_name)
            SESSION.add(usr)
            SESSION.commit()
        else:
            pass

def update_chat(id, chattitle):
    with INSERTION_LOCK:
        msg = SESSION.query(Chats).get(id)
        if not msg:
            usr = Users(id, chattitle)
            SESSION.add(usr)
            SESSION.commit()
        else:
            pass

def get_userid_by_name(username):
    try:
        return (
            SESSION.query(Users)
            .filter(func.lower(Users.username) == username.lower())
            .all()
        )
    finally:
        SESSION.close()


def get_name_by_userid(id):
    try:
        return SESSION.query(Users).get(Users.id == int(id)).first()
    finally:
        SESSION.close()


def get_chat_members(chat_id):
    try:
        return SESSION.query(ChatMembers).filter(ChatMembers.chat == str(chat_id)).all()
    finally:
        SESSION.close()


def get_all_chats():
    try:
        return SESSION.query(Chats).all()
    finally:
        SESSION.close()


def get_all_users():
    try:
        return SESSION.query(Users.id).order_by(Users.id)
    finally:
        SESSION.close()
        
def get_user_num_chats(id):
    try:
        return (
            SESSION.query(ChatMembers).filter(ChatMembers.user == int(id)).count()
        )
    finally:
        SESSION.close()


def get_user_com_chats(id):
    try:
        chat_members = (
            SESSION.query(ChatMembers).filter(ChatMembers.user == int(id)).all()
        )
        return [i.chat for i in chat_members]
    finally:
        SESSION.close()


def num_chats():
    try:
        return SESSION.query(Chats).count()
    finally:
        SESSION.close()


def num_users():
    try:
        return SESSION.query(Users).count()
    finally:
        SESSION.close()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Chats).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)
        SESSION.commit()

        chat_members = (
            SESSION.query(ChatMembers)
            .filter(ChatMembers.chat == str(old_chat_id))
            .all()
        )
        for member in chat_members:
            member.chat = str(new_chat_id)
        SESSION.commit()


ensure_bot_in_db()


def del_user(id):
    with INSERTION_LOCK:
        curr = SESSION.query(Users).get(id)
        if curr:
            SESSION.delete(curr)
            SESSION.commit()
            return True

        ChatMembers.query.filter(ChatMembers.user == id).delete()
        SESSION.commit()
        SESSION.close()
    return False


def rem_chat(chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Chats).get(str(chat_id))
        if chat:
            SESSION.delete(chat)
            SESSION.commit()
        else:
            SESSION.close()
            
def list_users():
    try:
        query = SESSION.query(Users.id).order_by(Users.id)
        return query
    finally:
        SESSION.close()
