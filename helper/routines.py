from twitchio.ext import routines
from config import VK, INSTAGRAM, DONATE


def start_routines(channel):
    social.start(channel)
    donate.start(channel)


@routines.routine(minutes=70)
async def social(channel):
    await channel.send(f'Мой VK: {VK}, Instagram: {INSTAGRAM} TehePelo')


@routines.routine(hours=1)
async def donate(channel):
    await channel.send(f'Поддержать меня: {DONATE}  TehePelo ')

