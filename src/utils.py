from datetime import datetime
from enum import Enum
from googletrans import Translator
import json


class MethodNotAllowedError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)


def get_time_difference(time: str):
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


def prettify(data) -> str:
    if not isinstance(data, dict):
        data = data.json()
    return json.dumps(data, indent=4)


def get_command(message):
    if len(message) and message[0] == '!':
        return message.split()[0]


def socials_to_string(socials: list) -> str:
    return ' , '.join(socials)


def socials_to_list(socials: str) -> list:
    return socials.split(' , ')


class Language(Enum):
    Russian = "ru"
    English = "en"


def to_russian(english: str) -> str:
    tr = Translator()
    return tr.translate(english, dest='ru', src='en')


def to_english(russian: str) -> str:
    tr = Translator()
    return tr.translate(russian, dest='en', src='ru')