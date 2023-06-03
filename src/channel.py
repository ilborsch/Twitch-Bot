from helper.opendota import OpenDota
from typing import Optional


class Channel:
    def __init__(self, dota_player_id: Optional[int] = None,
                 steam_link: str = '',
                 donate_link: str = '',
                 *social_links):

        self.socials = social_links or []
        self.steam_link = steam_link
        self.donate_link = donate_link
        self.dota_player_id = None
        self.opendota = None
        self._is_online = True

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


