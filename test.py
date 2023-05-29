import requests_html
import bs4
import json
from datetime import datetime
from opendota import Game
games = []


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


def get_played_games(player_id: int, hours: int = 16):
    session = requests_html.HTMLSession()
    response = session.get(f'https://www.dotabuff.com/players/{player_id}/matches')
    bs = bs4.BeautifulSoup(response.content, "html.parser")

    matches = bs.find_all('tr')
    del matches[0]

    for match in matches:
        # print(match.find('time')['datetime'])
        time = parse_time(match.find('time')['datetime'])

        if time.seconds <= hours * 60 * 60 and time.days == 0:

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

            games.append(game)

    return games


player_id = 56939869

get_played_games(884929704)

for i in games:
    print(i)