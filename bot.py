from twitchio.ext import commands
from helper.opendota import OpenDota
from asyncio import sleep
from helper.routines import start_routines
from random import randint, choice
from helper.utils import get_command_from_message
from config import (TMI_TOKEN, CLIENT_ID, BOT_NAME, BOT_PREFIX,
                    CHANNEL, CLIENT_SECRET, DOTA_PLAYER_ID,
                    VK, INSTAGRAM, STEAM, DONATE)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TMI_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            nick=BOT_NAME,
            prefix=BOT_PREFIX,
            initial_channels=[CHANNEL]
        )
        with open('info/banned-words.txt', 'r', encoding='utf8') as file:
            self.__BANNED_WORDS = file.read().split(', ')

        with open('info/greetings.txt', 'r', encoding='utf8') as file:
            self.__GREETINGS = file.read().split(', ')

        self._is_online = True

    async def event_ready(self):
        self._is_online = True
        logged_text = f'Бот здесь и готов выполнять свой машинный долг! KonCha'
        help_text = f'Ты можешь узнать что я умею с помощью команды !help VoHiYo'
        enjoy_watching_text = f'Приятного просмотра! <3'

        OpenDota.init_session(DOTA_PLAYER_ID)
        channel = self.get_channel(CHANNEL)

        start_routines(channel)
        await channel.send(logged_text)
        await sleep(1.5)
        await channel.send(help_text)
        await sleep(1.5)
        await channel.send(enjoy_watching_text)

    async def event_message(self, message):
        if message.echo:
            return

        command = get_command_from_message(message.content)
        if command in ("!bot_on", "!bot_off") and message.author.name != BOT_NAME:
            return

        if bot._is_online or command == "!bot_on":
            content = message.content.lower()
            for word in self.__BANNED_WORDS:
                if word in content:
                    await message.channel.send(f'{message.author.mention} не ругайся!  PunOko')
                    break

            await self.handle_commands(message)

    @commands.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(f'''
           KonCha Доступные команды - !help, !greet, !rank, !wr, !mmr, !last, !donate, !steam, !social. Спасибо что смотрите меня! <3
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
            message = f'Win Rate за сегодня - {int(wr)}%. ' \
                      f' | {w} W - {l} L  {"PunOko" if wr < 50 else "PogChamp"} '
        except ZeroDivisionError:
            message = 'Сегодня не было сыграно ни одной игры.. PunOko'
        await ctx.send(f'{ctx.author.mention} {message}')

    @commands.command()
    async def last(self, ctx: commands.Context):
        try:
            game = OpenDota.get_last_game()
            k, d, a = game.KDA
            game_result = 'ПОБЕДА VoteYea' if game.result.lower() == "won match" else "ПОРАЖЕНИЕ VoteNay"
            message = f'{game_result}. Герой - {game.hero_name}, KDA - {k}/{d}/{a}.' \
                      f' Игра длилась {game.duration}. Ссылка на игру: {game.match_link[12:]}'
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
        mmr2 = randint(1000, 4500)
        mmr3 = randint(3000, 5500)
        mmr4 = randint(4500, 6500)
        mmr5 = randint(6500, 11000)
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

    @commands.command()
    async def bot_off(self, ctx: commands.Context):
        OpenDota.clear_match_story()
        await ctx.send('OFF')
        self._is_online = False

    @commands.command()
    async def bot_on(self, ctx: commands.Context):
        if not self._is_online:
            await self.event_ready()
        else:
            await ctx.send('Bot is already working')

    @commands.command()
    async def change_dota_id(self, ctx : commands.Context):
        try:
            new_id = int(ctx.message.content.split()[1])
            global DOTA_PLAYER_ID
            DOTA_PLAYER_ID = new_id
            await ctx.send('DONE')
        except ValueError:
            await ctx.send('Error occurred during !change_dota_id ')


if __name__ == '__main__':
    bot = Bot()
    print('start')
    bot.run()


