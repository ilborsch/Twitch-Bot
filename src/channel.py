from src.opendota import OpenDota
from typing import Optional
from environment.models import Channel as ChannelModel


class Channel:
    def __init__(self, dota_player_id: Optional[int] = None,
                 steam_link: str = '',
                 donate_link: str = '',
                 is_in_database: bool = False,
                 *social_links):

        self.socials = social_links or []
        self.steam_link = steam_link
        self.donate_link = donate_link
        self.dota_player_id = dota_player_id
        self.opendota = OpenDota(self.dota_player_id) if self.dota_player_id else None
        self.is_in_database = is_in_database
        self._is_online = True

    def add_to_database(self, session, channel_name):
        if self.is_complete() and not self.is_in_database:
            ChannelModel.create_channel(
                session=session,
                name=channel_name,
                dota_id=self.dota_player_id,
                steam_link=self.steam_link,
                donation_link=self.donate_link,
                socials=self.socials
            )
            self.is_in_database = True
        return self.is_in_database

    def is_complete(self):
        return bool(self.steam_link) and bool(self.donate_link) and bool(self.dota_player_id)

    def setup_dota(self, dota_player_id: int):
        self.dota_player_id = dota_player_id
        self.opendota = OpenDota(self.dota_player_id)

    def setup_donation(self, link: str):
        if isinstance(link, str):
            self.donate_link = link

    def setup_steam(self, link: str):
        if isinstance(link, str):
            self.steam_link = link

    def add_social(self, link: str):
        if isinstance(link, str):
            self.socials.append(link)

    @property
    def is_online(self):
        return self._is_online

    @is_online.setter
    def is_online(self, value):
        self._is_online = value


