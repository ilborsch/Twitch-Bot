from twitchio.ext import commands
from opendota import OpenDota
from asyncio import sleep
from random import randint
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

        if message.content[:9] == '!win_rate':
            limit = ''
            for i in range(len(message.content)):
                if message.content[i].isnumeric():
                    limit += message.content[i]
                elif limit:
                    break

            message.content = f'!win_rate {limit if limit else "10"}'

        await self.handle_commands(message)

    @commands.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(f'''
           KonCha Доступные команды - !help, !greet, !mmr, !win_rate, !donate, !steam, !social. Спасибо что смотрите меня! <3
        ''')

    @commands.command()
    async def greet(self, ctx: commands.Context):
        await ctx.send(f'{self.__GREETINGS[randint(0, len(self.__GREETINGS) - 1)]}, {ctx.author.name}!  KonCha')

    @commands.command()
    async def donate(self, ctx: commands.Context):
        await ctx.send(f'TehePelo  {ctx.author.mention} Поддержать меня: {DONATE} Спасибо!  TehePelo ')

    @commands.command()
    async def mmr(self, ctx: commands.Context):
        rank = OpenDota.get_player_rank(DOTA_PLAYER_ID)
        await ctx.send(rank)

    @commands.command()
    async def social(self, ctx: commands.Context):
        await ctx.send(f'Добро пожаловать!  <3  Мой VK: {VK} , Instagram: {INSTAGRAM}')

    @commands.command()
    async def steam(self, ctx: commands.Context):
        await ctx.send(f'Мой Steam - {STEAM}  TPFufun')

    @commands.command()
    async def win_rate(self, ctx: commands.Context):
        limit = int(ctx.message.content.split()[1])
        wr_data = OpenDota.get_player_win_rate(DOTA_PLAYER_ID, limit=limit)
        w, l = wr_data['win'], wr_data['lose']
        wr = w / (w + l) * 100
        await ctx.send(f'За последние {limit} игр WR составляет {wr}%  {"PunOko" if wr < 50 else "PogChamp"}. '
                       f' WIN - {w}, LOSE - {l}.  TehePelo')


if __name__ == '__main__':
    bot = Bot()
    print('start')
    bot.run()
    print('stop')


