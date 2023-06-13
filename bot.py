from twitchio.ext import commands
from src.channel import Channel
from asyncio import sleep
from random import randint, choice
from src.utils import get_command, socials_to_list, socials_to_string, Language
from environment.config import TMI_TOKEN, CLIENT_ID, BOT_NAME, BOT_PREFIX, CLIENT_SECRET

from environment.database import Session
from environment.database import engine
from environment.models import Channel as ChannelModel
from environment.database import Base
import json


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TMI_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            nick=BOT_NAME,
            prefix=BOT_PREFIX,
            initial_channels=[BOT_NAME]
        )
        with open('info/banned-words.txt', 'r', encoding='utf8') as file:
            self.__BANNED_WORDS = file.read().split(', ')

        with open('info/phrases.json', 'r', encoding='utf8') as file:
            self.phrases = json.load(file)

        self.channels = dict()
        self.session = Session()

    @commands.command()
    async def add_bot(self, ctx: commands.Context):
        if ctx.channel.name == BOT_NAME:
            if ctx.author.name not in self.channels:
                new_channel = Channel()
                channel_is_added = new_channel.add_to_database(self.session, ctx.author.name)
                if channel_is_added:
                    await self._start_bot(ctx.author, new_channel)
                    await ctx.send("Success. Next step is to setup your bot. Use !setup_help command to continue.")
            else:
                await ctx.send("It seems like you already have the bot.")

    @commands.command()
    async def me(self, ctx: commands.Context):
        for chatter in ctx.chatters:
            if chatter.name == ctx.author.name:
                await ctx.send(f"{chatter.name}")
                return

    @commands.command()
    async def remove_bot(self, ctx: commands.Context):
        language = self.channels[ctx.channel.name].language_choice.value
        if ctx.channel.name not in (ctx.author.name, BOT_NAME):
            return

        for channel in ChannelModel.get_all(session=self.session):
            if channel.name == ctx.author.name:
                ChannelModel.delete_channel(
                    session=self.session,
                    channel_name=ctx.author.name
                )
                self.channels.pop(ctx.author.name)
                await ctx.send(self.phrases['remove_bot'][language])
                await self.part_channels([ctx.author.name])
                break
        else:
            await ctx.send(self.phrases['dont_have_bot'][language])

    async def _start_bot(self, context_channel, new_channel):
        await self.join_channels([context_channel.name])
        self.channels[context_channel.name] = new_channel

    async def event_ready(self):
        for channel in ChannelModel.get_all(session=self.session):
            self.channels[channel.name] = Channel(
                channel.dota_player_id,
                channel.donation_link,
                channel.language_choice,
                True,  # is_in_database
                *socials_to_list(channel.socials)
            )
            await self.join_channels([channel.name])
            print(f'Loaded {channel.name} from database.')
        print('-' * 25)
        print(f'Logged in as: {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return

        command = get_command(message.content)
        ac = ("!add_bot", "!remove_bot", "!language", "!change_language", "!set_language")

        if message.channel.name.lower() == BOT_NAME.lower():
            if message.author.name in self.channels and self.channels[message.author.name].is_complete():
                return
            if command not in ac and "etup" not in command:
                message.content = '!bot_help'
            await self.handle_commands(message)
            return
        elif message.first and message.channel.name in self.channels:
            language = self.channels[message.channel.name].language_choice.value
            await message.channel.send(self.phrases['first'][language].format(message.author.mention))

        if self.channels[message.channel.name].is_online or command == "!bot_on":
            await self.check_message(message)
            await self.handle_commands(message)

    async def check_message(self, message):
        content = message.content.lower()
        channel = await message.channel.user()
        bot = await self.fetch_channel(BOT_NAME)
        for word in self.__BANNED_WORDS:
            if word in content:
                await message.channel.send(f'{message.author.mention} shut up!  PunOko')
                # await channel.timeout_user(
                #     moderator_id=bot.user.id,
                #     user_id=message.author.id,
                #     duration=1,
                #     reason="Ban word",
                #     token=TMI_TOKEN
                # )
                return

    @commands.command(aliases=("hel", "elp"))
    async def help(self, ctx: commands.Context):
        language = self.channels[ctx.channel.name].language_choice.value
        await ctx.send(self.phrases['help'][language])

    @commands.command(aliases=("donat", "donation", "донат", "Donate", "DONATE", "donations"))
    async def donate(self, ctx: commands.Context):
        channel = self.channels[ctx.channel.name]
        language = channel.language_choice.value
        if channel.has_donation_link():
            await ctx.send(self.phrases['donate'][language].format(ctx.author.mention, channel.donate_link))
        else:
            await ctx.send(self.phrases['donation_not_setup'][language])

    @commands.command(aliases=("socials", "ocials", "socia", "Social", "SOCIAL"))
    async def social(self, ctx: commands.Context):
        language = self.channels[ctx.channel.name].language_choice.value
        channel = self.channels[ctx.channel.name]
        if channel.has_socials():
            socials = ', '.join(channel.socials)
            await ctx.send(self.phrases['social'][language].format(ctx.author.mention, socials))
        else:
            await ctx.send(self.phrases['socials_not_setup'][language])

    @commands.command(aliases=("winrate", "winlose", "games", "wl", "wins", "винрейт", "Wr", "WR"))
    async def wr(self, ctx: commands.Context):
        language = self.channels[ctx.channel.name].language_choice.value
        if self.channels[ctx.channel.name].has_dota_id():
            win, lose = self.channels[ctx.channel.name].opendota.get_player_win_rate()
            if win or lose:
                message = f'W {win} - L {lose}. {"PunOko" if win <= lose else "PogChamp"}'
            else:
                message = self.phrases['wr_no_games'][language]
            await ctx.send(f'{ctx.author.mention} {message}')
        else:
            await ctx.send(self.phrases['dota_id_not_setup'][language])

    @commands.command(aliases=("last_game", "lastgame", "lastinfo", "ласт", "Last", "LAST"))
    async def last(self, ctx: commands.Context):
        language = self.channels[ctx.channel.name].language_choice.value
        if self.channels[ctx.channel.name].has_dota_id():
            try:
                game = self.channels[ctx.channel.name].opendota.get_last_game()
                k, d, a = game.KDA
                if game.result.lower() == "won match":
                    game_result = self.phrases['last_game_result_win'][language]
                else:
                    game_result = self.phrases['last_game_result_lose'][language]
                message = self.phrases['last_game_info'][language].format(game_result, game.hero_name, k, d, a, game.duration, game.match_link[12:])
            except IndexError:
                message = self.phrases['wr_no_games'][language]
            await ctx.send(f'{ctx.author.mention} {message}')
        else:
            await ctx.send(self.phrases['dota_id_not_setup'][language])

    @commands.command(aliases=("rang", "ранг", "streamerrank", "mmr", "ммр", "Rank", "RANK"))
    async def rank(self, ctx: commands.Context):
        language = self.channels[ctx.channel.name].language_choice.value
        if self.channels[ctx.channel.name].has_dota_id():
            rank = self.channels[ctx.channel.name].opendota.get_player_rank()
            await ctx.send(f'{ctx.author.mention} {rank}')
        else:
            await ctx.send(self.phrases['dota_id_not_setup'][language])

    @commands.command(aliases=("мойммр", "myrank", "Mymmr", "MYMMR"))
    async def mymmr(self, ctx: commands.Context):
        language = self.channels[ctx.channel.name].language_choice.value
        mmr1 = randint(0, 3000)
        mmr2 = randint(1000, 4500)
        mmr3 = randint(3000, 5500)
        mmr4 = randint(4500, 6500)
        mmr5 = randint(6500, 11000)
        mmr = choice([mmr1, mmr2, mmr3, mmr4, mmr5])

        name = ''
        emoji = ''

        if mmr <= 2000:
            name = 'noobie'
            emoji = 'SMOrc'
        elif mmr <= 4000:
            name = 'wimp'
            emoji = 'TearGlove'
        elif mmr <= 6500:
            name = 'player'
            emoji = 'VoHiYo'
        elif mmr <= 8500:
            name = 'tough guy'
            emoji = 'B)'
        elif mmr <= 11000:
            name = 'GOD'
            emoji = 'PogChamp'

        await ctx.send(self.phrases['mymmr'][language].format(ctx.author.mention, mmr, name, emoji))

    @commands.command()
    async def bot_off(self, ctx: commands.Context):
        if not ctx.author.name == ctx.channel.name:
            return

        if not self.channels[ctx.channel.name].is_online:
            await ctx.send('Bot is already off..')
            return

        self.channels[ctx.channel.name].opendota.clear_match_story()
        self.channels[ctx.channel.name].is_online = False
        await ctx.send('Bot is OFF')

    @commands.command()
    async def bot_on(self, ctx: commands.Context):
        if not ctx.author.name == ctx.channel.name:
            return

        if self.channels[ctx.channel.name].is_online:
            await ctx.send('Bot is already working')
            return

        self.channels[ctx.channel.name].is_online = True
        self.channels[ctx.channel.name].opendota.refresh_last_match()
        await ctx.send('Bot is ON!')

    @commands.command(aliases=("change_dota", "change_id"))
    async def change_dota_id(self, ctx: commands.Context, new_id: int):
        language = self.channels[ctx.channel.name].language_choice.value
        if not ctx.author.name == ctx.channel.name:
            return

        if self.channels[ctx.channel.name].has_dota_id():
            response = self.channels[ctx.channel.name].opendota.change_player_id(new_id)
            if response:
                self.channels[ctx.channel.name].dota_player_id = new_id
                ChannelModel.update(
                    session=self.session,
                    name=ctx.author.name,
                    dota_id=new_id
                )
            await ctx.send('DONE' if response else self.phrases['change_error'][language].format("!change_dota_id"))
        else:
            await ctx.send(self.phrases['did_not_setup'][language])

    @commands.command(aliases=("change_donate", "change_donations", "change_donates"))
    async def change_donation(self, ctx: commands.Context, new_link: str):
        language = self.channels[ctx.channel.name].language_choice.value
        if not ctx.author.name == ctx.channel.name:
            return

        if self.channels[ctx.channel.name].has_donation_link():
            response = self.channels[ctx.channel.name].donate_link = new_link
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                donation_link=new_link
            )
            await ctx.send('DONE' if response else self.phrases['change_error'][language].format("!change_donation"))
        else:
            await ctx.send(self.phrases['did_not_setup'][language])

    @commands.command(aliases=("change_social", "change_soc"))
    async def change_socials(self, ctx: commands.Context, *socials):
        language = self.channels[ctx.channel.name].language_choice.value
        if not ctx.author.name == ctx.channel.name:
            return

        if self.channels[ctx.channel.name].has_socials():
            response = self.channels[ctx.channel.name].socials = socials
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                socials=socials_to_string(list(socials))
            )
            await ctx.send('DONE' if response else self.phrases['change_error'][language].format("!change_socials"))
        else:
            await ctx.send(self.phrases['did_not_setup'][language])

    @commands.command()
    async def bot_help(self, ctx: commands.Context):
        language = self.channels[ctx.author.name].language_choice.value
        await ctx.send(self.phrases['bot_help'][language])

    async def _check_setup_process(self, ctx: commands.Context):
        channel = self.channels[ctx.author.name]
        language = channel.language_choice.value
        if channel.is_complete():
            await ctx.send(self.phrases['check_setup_process_success'][language])
        else:
            await ctx.send(self.phrases['check_setup_process_failure'][language])

    @commands.command(aliases=("setup_dota_id", "setup_id"))
    async def setup_dota(self, ctx: commands.Context, dota_player_id: int):
        language = self.channels[ctx.author.name].language_choice.value
        if not ctx.channel.name == BOT_NAME:
            return
        if ctx.author.name in self.channels:
            self.channels[ctx.author.name].setup_dota(dota_player_id)
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                dota_id=dota_player_id
            )
            await ctx.send(self.phrases['setup_success'][language])
        else:
            await ctx.send(self.phrases['setup_failure'][language])

        await self._check_setup_process(ctx)

    @commands.command(aliases=("setup_social", "setup_soc"))
    async def setup_socials(self, ctx: commands.Context, *socials):
        language = self.channels[ctx.author.name].language_choice.value
        if not ctx.channel.name == BOT_NAME:
            return
        if ctx.author.name in self.channels:
            for social in socials:
                self.channels[ctx.author.name].add_social(social)
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                socials=socials_to_string(list(socials))
            )
            await ctx.send(self.phrases['setup_success'][language])
        else:
            await ctx.send(self.phrases['setup_failure'][language])

        await self._check_setup_process(ctx)

    @commands.command(aliases=("setup_donate", "setup_donations", "setup_donates"))
    async def setup_donation(self, ctx: commands.Context, donation_link: str):
        language = self.channels[ctx.author.name].language_choice.value
        if not ctx.channel.name == BOT_NAME:
            return
        if ctx.author.name in self.channels:
            self.channels[ctx.author.name].setup_donation(donation_link)
            ChannelModel.update(
                session=self.session,
                name=ctx.author.name,
                donation_link=donation_link
            )
            await ctx.send(self.phrases['setup_success'][language])
        else:
            await ctx.send(self.phrases['setup_failure'][language])

        await self._check_setup_process(ctx)

    @commands.command(aliases=("setup_hel", "etup_help"))
    async def setup_help(self, ctx: commands.Context):
        language = self.channels[ctx.author.name].language_choice.value
        if not ctx.channel.name == BOT_NAME:
            return
        if self.channels[ctx.author.name].is_complete():
            await ctx.send(self.phrases['setup_completed'][language])
        else:
            await ctx.send(self.phrases['setup_help'][language])

    @commands.command(aliases=("change_languag", "hange_language",
                               "language", "set_language",
                               "set_languag", "et_language"))
    async def change_language(self, ctx: commands.Context, language_choice: str):
        if ctx.channel.name not in (BOT_NAME, ctx.author.name):
            return

        language = self.channels[ctx.author.name].language_choice.value

        if ctx.channel.name in self.channels or ctx.author.name in self.channels and ctx.channel.name == BOT_NAME:
            if language_choice.lower() in ("ru", "russian", "rus", "russ", "russia", "ру", "русский", "рус", "русс"):
                self.channels[ctx.author.name].language_choice = Language.Russian
                ChannelModel.update(
                    session=self.session,
                    name=ctx.author.name,
                    language_choice=Language.Russian.value
                )
                await ctx.send("Вы поставили Русский язык.")
            elif language_choice.lower() in ("en", "eng", "english", "англ", "английский"):
                self.channels[ctx.author.name].language_choice = Language.English
                ChannelModel.update(
                    session=self.session,
                    name=ctx.author.name,
                    language_choice=Language.English.value
                )
                await ctx.send("English has been set.")
        else:
            await ctx.send(self.phrases['setup_failure'][language])


def main():
    Base.metadata.create_all(engine)
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
