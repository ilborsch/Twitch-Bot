import requests_html
import bs4
from typing import Optional
from src.utils import MethodNotAllowedError, get_time_difference


class Game:

    def __str__(self):
        return f'Match ID: {self.match_id}, Hero: {self.hero_name}, WL: {self.result}, Duration: {self.duration}, KDA: {self.KDA}'

    def __init__(self, hero_name: str, result: str, duration: str, kda: tuple, match_id: str):
        self._hero_name = hero_name
        self._result = result
        self._duration = duration
        self._KDA = kda
        self._match_id = match_id
        self._match_link = f'dotabuff.com{match_id}'

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
    def __init__(self, dota_player_id: int):
        self.__session = requests_html.HTMLSession()
        self._api_prefix = r'https://api.opendota.com/api'
        self.__dota_player_id = dota_player_id
        self.__matches = list()
        self.__last_match_before_stream = None
        self.refresh_last_match()

    def refresh_last_match(self):
        self.__last_match_before_stream = self.__get_last_match_before_stream()

    def clear_match_story(self):
        self.__matches.clear()

    def get_player_rank(self) -> Optional[str]:
        response = self.__session.get(f'https://www.dotabuff.com/players/{self.__dota_player_id}')
        bs = bs4.BeautifulSoup(response.content, "html.parser")
        return bs.find('div', class_='rank-tier-wrapper')['title']

    def change_player_id(self, new_id: int) -> bool:
        if isinstance(new_id, int):
            self.__init__(new_id)
            return True
        return False

    def get_last_game(self) -> Game:
        self.__parse_player_games()
        return self.__matches[0]

    def get_player_win_rate(self):
        wins, losses = 0, 0
        self.__parse_player_games()
        for match in self.__matches:
            result = match.result.lower() == 'won match'
            wins += result
            losses += not result

        return wins, losses

    def __get_last_match_before_stream(self):
        session = requests_html.HTMLSession()
        response = session.get(f'https://www.dotabuff.com/players/{self.__dota_player_id}/matches')
        bs = bs4.BeautifulSoup(response.content, "html.parser")

        match = bs.find_all('tr')[1]

        return self.__get_game_from_match_info(match)

    @staticmethod
    def __get_match_date_from_match(match) -> str:
        return match.find_all('td')[3].div.time['datetime']

    @staticmethod
    def __get_game_from_match_info(match) -> Game:
        hero_name_and_match_link = match.find('td', class_='cell-large')
        hero_name = hero_name_and_match_link.a.text
        match_link = hero_name_and_match_link.a['href']

        match_result_search = match.find_next('td')
        for _ in range(3):
            match_result_search = match_result_search.find_next_sibling('td')
        match_result = match_result_search.a.text

        duration_search = match_result_search.find_next_sibling('td').find_next_sibling('td')
        duration = duration_search.text

        kda_search = duration_search.find_next_sibling('td')
        values = kda_search.find_all('span', class_='value')
        kda = tuple(map(lambda x: x.text, values))

        game = Game(hero_name=hero_name,
                    result=match_result,
                    duration=duration,
                    kda=kda,
                    match_id=match_link
                    )

        return game

    def __parse_player_games(self):
        self.clear_match_story()
        session = requests_html.HTMLSession()
        response = session.get(f'https://www.dotabuff.com/players/{self.__dota_player_id}/matches')
        bs = bs4.BeautifulSoup(response.content, "html.parser")

        matches = bs.find_all('tr')
        del matches[0]

        for match in matches:

            date = get_time_difference(self.__get_match_date_from_match(match))
            game = self.__get_game_from_match_info(match)

            if date.days > 1 or date.seconds > 6 * 60 * 60:  # 6 hours
                self.__last_match_before_stream = game
                break

            if game.match_id == self.__last_match_before_stream.match_id:
                break

            self.__matches.append(game)

        return self.__matches

    def __make_get_request(self, url: str) -> Optional[dict]:
        response = self.__session.get(url)
        if response.status_code == 200:
            return response.json()

    def __get_player_api_info(self) -> Optional[dict]:
        url = self._api_prefix + f'/players/{self.__dota_player_id}'
        return self.__make_get_request(url)

    def __get_match_api_info(cls, match_id: int):
        url = cls._api_prefix + f'/matches/{match_id}'
        return cls.__make_get_request(url)





