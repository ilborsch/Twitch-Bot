from twitchio.ext import commands
from opendota import OpenDota
from asyncio import sleep
from random import randint, choice
from config import (TMI_TOKEN, CLIENT_ID, BOT_NAME, BOT_PREFIX,
                    CHANNEL, CLIENT_SECRET, DOTA_PLAYER_ID,
                    VK, INSTAGRAM, STEAM, DONATE)


class Bot(commands.Bot):
    def __init__(self):
        self.__BANNED_WORDS = [
            "nigger", "nigga", "ниггер", "нига", "faggot",
            "пидор", "пидорас", "педик", "гомик", " хохол",
            "хач", "жид", "даун", "аутист", "retard", "pidor",
            "тест на запретку"
        ]

        self.__GREETINGS = ["Приветик", "Салам", "Дароу", "Здравствуй",
                          "Приветствую", "Пошел нахуй", "Мир с тобой",
                          "Привет"
        ]

        super().__init__(
            token=TMI_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            nick=BOT_NAME,
            prefix=BOT_PREFIX,
            initial_channels=[CHANNEL]
        )

    async def event_ready(self):
        logged_text = f'Бот здесь и готов выполнять свой машинный долг! KonCha'
        help_text = f'Ты можешь узнать что я умею с помощью команды !help VoHiYo'
        enjoy_watching_text = f'Приятного просмотра! <3'

        OpenDota.init_session(DOTA_PLAYER_ID)

        channel = self.get_channel(CHANNEL)
        await channel.send(logged_text)
        await sleep(2)
        await channel.send(help_text)
        await sleep(2)
        await channel.send(enjoy_watching_text)
        print('*' * 30)

    async def event_message(self, message):
        if message.echo:
            return

        print(f"{message.author.name} says: {message.content}")

        for word in self.__BANNED_WORDS:
            if word in message.content.lower():
                await message.channel.send(f'{message.author.mention} не ругайся!  PunOko')
                break

        await self.handle_commands(message)

    @commands.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(f'''
           KonCha Доступные команды - !help, !greet, !rank, !wr, !last_game, !donate, !steam, !social. Спасибо что смотрите меня! <3
        ''')

    @commands.command()
    async def greet(self, ctx: commands.Context):
        await ctx.send(f'{self.__GREETINGS[randint(0, len(self.__GREETINGS) - 1)]}, {ctx.author.name}!  KonCha')

    @commands.command()
    async def donate(self, ctx: commands.Context):
        await ctx.send(f'{ctx.author.mention} Поддержать меня: {DONATE}  TehePelo ')

    @commands.command()
    async def social(self, ctx: commands.Context):
        await ctx.send(f'{ctx.author.mention} <3  Мой VK: {VK} , Instagram: {INSTAGRAM}')

    @commands.command()
    async def steam(self, ctx: commands.Context):
        await ctx.send(f'{ctx.author.mention} Мой Steam - {STEAM}  TPFufun')

    @commands.command()
    async def wr(self, ctx: commands.Context):
        w, l = OpenDota.get_player_win_rate()
        try:
            wr = w / (w + l) * 100
            message = f'WinRate за сегодня составляет {wr}%  {"PunOko" if wr < 50 else "PogChamp"}.' \
                      f' {w} W - {l} L.  TehePelo'
        except ZeroDivisionError:
            message = 'Сегодня не было сыграно ни одной игры.. PunOko'
        await ctx.send(f'{ctx.author.mention} {message}')

    @commands.command()
    async def last_game(self, ctx: commands.Context):
        try:
            game = OpenDota.get_last_game()
            k, d, a = game.KDA
            game_result = 'ПОБЕДА VoteYea' if game.result.lower() == "won match" else "ПОРАЖЕНИЕ VoteNay"
            message = f'{game_result}. Герой - {game.hero_name}, KDA - {k}/{d}/{a}.' \
                      f' Игра длилась {game.duration}. Ссылка на игру: {game.match_link}'
        except IndexError:
            message = 'Сегодня не было сыграно ни одной игры.. PunOko'
        await ctx.send(f'{ctx.author.mention} {message}')

    @commands.command()
    async def rank(self, ctx: commands.Context):
        rank = OpenDota.get_player_rank()
        await ctx.send(f'{ctx.author.mention} {rank}')

    @commands.command()
    async def mmr(self, ctx: commands.Context):
        mmr1 = randint(0, 3000)
        mmr2 = randint(1000, 4000)
        mmr3 = randint(3000, 5000)
        mmr4 = randint(4000, 7000)
        mmr5 = randint(6000, 11000)
        mmr = choice([mmr1, mmr2, mmr3, mmr4, mmr5])

        name = ''
        emoji = ''

        if mmr <= 2000:
            name = 'Поносище'
            emoji = 'SMOrc'
        elif mmr <= 4000:
            name = 'Помойка'
            emoji = 'TearGlove'
        elif mmr <= 6500:
            name = 'Игрок'
            emoji = 'VoHiYo'
        elif mmr <= 8500:
            name = 'Красавчик'
            emoji = 'B)'
        elif mmr <= 11000:
            name = 'БОГ'
            emoji = 'PogChamp'

        await ctx.send(f'{ctx.author.mention}, Ты - {mmr} ммр {name} {emoji}')


if __name__ == '__main__':
    bot = Bot()
    print('start')
    bot.run()
    print('stop')


