from datetime import datetime
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


def get_command_from_message(message):
    if len(message) and message[0] == '!':
        return message.split()[0]

