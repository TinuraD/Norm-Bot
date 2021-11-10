from sqlalchemy import Column, String
from normbot.utils.sql import BASE, SESSION


class Chatbot(BASE):
    __tablename__ = "hatbot"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


Chatbot.__table__.create(checkfirst=True)


def add_hatbot(chat_id: str):
    nightmoddy = Chatbot(str(chat_id))
    SESSION.add(nightmoddy)
    SESSION.commit()


def rmhatbot(chat_id: str):
    rmnightmoddy = SESSION.query(Chatbot).get(str(chat_id))
    if rmnightmoddy:
        SESSION.delete(rmnightmoddy)
        SESSION.commit()


def get_all_chat_id():
    stark = SESSION.query(Chatbot).all()
    SESSION.close()
    return stark


def is_chatbot_indb(chat_id: str):
    try:
        s__ = SESSION.query(Chatbot).get(str(chat_id))
        if s__:
            return str(s__.chat_id)
    finally:
        SESSION.close()
