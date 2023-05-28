import requests_html
import json
import bs4
from typing import Optional


class OpenDota:
    prefix = r'https://api.opendota.com/api'
    session = requests_html.HTMLSession()
    __rank = None

    @staticmethod
    def __pretty(data) -> str:
        if not isinstance(data, dict):
            data = data.json()
        return json.dumps(data, indent=4)

    @classmethod
    def __make_get_request(cls, url: str) -> Optional[dict]:
        response = cls.session.get(url)
        if response.status_code == 200:
            print(cls.__pretty(response.json()))
            return response.json()

    @classmethod
    def __get_player_info(cls, player_id: int) -> Optional[dict]:
        url = cls.prefix + f'/players/{player_id}'
        return cls.__make_get_request(url)

    @classmethod
    def __get_match_info(cls, match_id: int):
        url = cls.prefix + f'/matches/{match_id}'
        return cls.__make_get_request(url)

    @classmethod
    def get_player_rank(cls, player_id: int) -> Optional[str]:
        if not cls.__rank:
            response = cls.session.get(f'https://www.dotabuff.com/players/{player_id}')
            bs = bs4.BeautifulSoup(response.content, "html.parser")

            return bs.find('div', class_='rank-tier-wrapper')['title']
        return cls.__rank

    @classmethod
    def get_player_win_rate(cls, player_id: int, limit: int = 10):
        url = cls.prefix + f'/players/{player_id}/wl?limit={limit}'
        return cls.__make_get_request(url)











