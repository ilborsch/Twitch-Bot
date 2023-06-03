from environment.database import Base
from sqlalchemy import Column, String, Integer
from src.utils import socials_to_string



class Channel(Base):
    __tablename__ = "channel"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    dota_player_id = Column(Integer)
    steam_link = Column(String)
    donation_link = Column(String)
    socials = Column(String)

    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name}, dota_id={self.dota_player_id})>"

    @staticmethod
    def create_channel(session, *, name, dota_id, steam_link, donation_link, socials):
        new_channel = Channel(
            name=name,
            dota_player_id=dota_id,
            steam_link=steam_link,
            donation_link=donation_link,
            socials=socials_to_string(socials)
        )
        session.add(new_channel)
        session.commit()

    @staticmethod
    def delete_channel(session, *, channel_name):
        session.query(Channel).filter(Channel.name == channel_name).delete()
        session.commit()

    @staticmethod
    def get_all(session):
        return session.query(Channel).all()


class Chatter(Base):
    __tablename__ = "chatter"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    language_choice = Column(String)

    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name}, dota_id={self.dota_player_id})>"

    @staticmethod
    def create_chatter(session, *, name, language):
        if not isinstance(language, str):
            language = language.value
        new_channel = Chatter(
            name=name,
            language_choice=language
        )
        session.add(new_channel)
        session.commit()


    @staticmethod
    def get_all(session):
        return session.query(Channel).all()

    @staticmethod
    def update_language(session, chatter_name, new_language):
        if not isinstance(new_language, str):
            new_language = new_language.value
        session.query(Chatter).filter(Chatter.name == chatter_name).update(
            {'language_choice': new_language}
        )
        session.commit()




