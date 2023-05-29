import requests_html
import json
import bs4
from typing import Optional
from utils import MethodNotAllowedError
from config import DOTA_PLAYER_ID
from datetime import datetime


class Game:

    def __str__(self):
        return f'Match ID: {self.match_id}, Hero: {self.hero_name}, WL: {self.result}, Duration: {self.duration}, KDA: {self.KDA}'

    def __init__(self, hero_name: str, result: str, duration: str, kda: tuple, match_id: str):
        self._hero_name = hero_name
        self._result = result
        self._duration = duration
        self._KDA = kda
        self._match_id = match_id
        self._match_link = f'https://www.dotabuff.com{match_id}'

    @property
    def hero_name(self):
        return self._hero_name

    @hero_name.setter
    def hero_name(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def KDA(self):
        return self._KDA

    @KDA.setter
    def KDA(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def match_link(self):
        return self._match_link

    @match_link.setter
    def match_link(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")

    @property
    def match_id(self):
        return self._match_id

    @match_id.setter
    def match_id(self, value):
        raise MethodNotAllowedError("Cannot change game data after initialization")


class OpenDota:

    _api_prefix = None
    __session = None

    __matches = None
    __dota_player_id = None

    def __init__(self):
        raise MethodNotAllowedError("Call class method init_session() !!!")

    @classmethod
    def init_session(cls, dota_player_id):
        cls.__dota_player_id = dota_player_id
        cls.__matches = list()
        cls.__session = requests_html.HTMLSession()
        cls._api_prefix = r'https://api.opendota.com/api'

    @staticmethod
    def __prettify(data) -> str:
        if not isinstance(data, dict):
            data = data.json()
        return json.dumps(data, indent=4)

    @classmethod
    def __make_get_request(cls, url: str) -> Optional[dict]:
        response = cls.__session.get(url)
        if response.status_code == 200:
            print(cls.__prettify(response.json()))
            return response.json()

    @classmethod
    def __get_player_api_info(cls) -> Optional[dict]:
        url = cls._api_prefix + f'/players/{cls.__dota_player_id}'
        return cls.__make_get_request(url)

    @classmethod
    def __get_match_api_info(cls, match_id: int):
        url = cls._api_prefix + f'/matches/{match_id}'
        return cls.__make_get_request(url)

    @classmethod
    def get_player_rank(cls) -> Optional[str]:
        response = cls.__session.get(f'https://www.dotabuff.com/players/{cls.__dota_player_id}')
        bs = bs4.BeautifulSoup(response.content, "html.parser")
        return bs.find('div', class_='rank-tier-wrapper')['title']

    @classmethod
    def get_player_win_rate(cls):
        wins, losses = 0, 0
        cls.get_played_games()
        for match in cls.__matches:
            result = match.result.lower() == 'won match'
            wins += result
            losses += not result

        return wins, losses

    @staticmethod
    def parse_time(time: str):
        year = int(time[:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hour = int(time[11:13])
        minutes = int(time[14:16])
        seconds = int(time[17:19])
        return datetime.now() - datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minutes,
            second=seconds
        )

    @classmethod
    def get_played_games(cls, hours: int = 16):
        cls.__matches.clear()
        session = requests_html.HTMLSession()
        response = session.get(f'https://www.dotabuff.com/players/{cls.__dota_player_id}/matches')
        bs = bs4.BeautifulSoup(response.content, "html.parser")

        matches = bs.find_all('tr')
        del matches[0]

        for match in matches:
            # print(match.find('time')['datetime'])
            time = cls.parse_time(match.find('time')['datetime'])

            if time.days == 0 and time.seconds <= hours * 60 * 60:

                hero_name_and_match_link = match.find('td', class_='cell-large')
                hero_name = hero_name_and_match_link.a.text
                match_link = hero_name_and_match_link.a['href']
                # print(hero_name, match_link)

                match_result_search = match.find_next('td')
                for i in range(3):
                    match_result_search = match_result_search.find_next_sibling('td')
                match_result = match_result_search.a.text
                # print(match_result)

                duration_search = match_result_search.find_next_sibling('td').find_next_sibling('td')
                duration = duration_search.text
                # print(duration)

                kda_search = duration_search.find_next_sibling('td')
                values = kda_search.find_all('span', class_='value')
                kda = tuple(map(lambda x: x.text, values))
                # print(kda)

                game = Game(hero_name=hero_name,
                            result=match_result,
                            duration=duration,
                            kda=kda,
                            match_id=match_link
                            )

                cls.__matches.append(game)

        return cls.__matches

    @classmethod
    def get_last_game(cls) -> Game:
        return cls.__matches[0]




