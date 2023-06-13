from environment.database import Base
from sqlalchemy import Column, String, Integer
from src.utils import socials_to_string


class Channel(Base):
    __tablename__ = "channel"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dota_player_id = Column(Integer, nullable=True)
    donation_link = Column(String, nullable=True)
    socials = Column(String, nullable=True)
    language_choice = Column(String, default="en")

    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name}, dota_id={self.dota_player_id})>"

    @staticmethod
    def create_channel(session, *, name, dota_id, donation_link, socials):
        new_channel = Channel(
            name=name,
            dota_player_id=dota_id,
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

    @staticmethod
    def update(session, *, name, dota_id=None, donation_link=None, socials=None, language_choice=None):
        query = session.query(Channel).filter(Channel.name == name)
        channel = query.first()
        query.update({
            'dota_player_id': dota_id or channel.dota_player_id,
            'donation_link': donation_link or channel.donation_link,
            'socials': socials_to_string(socials) if socials else channel.socials,
            'language_choice': language_choice or channel.language_choice
        })
        session.commit()

