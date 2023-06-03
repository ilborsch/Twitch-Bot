from twitchio.ext import commands
from src.channel import Channel
from random import randint, choice
from src.utils import get_command, socials_to_list
from environment.config import TMI_TOKEN, CLIENT_ID, BOT_NAME, BOT_PREFIX, CLIENT_SECRET

from environment.database import Session
from environment.database import engine
from environment.models import Channel as ChannelModel
from environment.database import Base


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

        self.channels = dict()
        self.session = Session()

    @commands.command()
    async def add_bot(self, ctx: commands.Context):
        if ctx.channel.name == BOT_NAME:
            if ctx.author.name not in self.channels:
                new_channel = Channel()
                await self._start_bot(ctx.author, new_channel)
                await ctx.send('Success. Next step is to setup your bot.'
                               ' Use !setup_help command to get further information. ')
            else:
                await ctx.send('Bot is already working.')

    # @commands.command()
    # async def set_language(self, ctx:commands.Context, language):
    #     if "ru" in language or "ру" in language:
    #         language = Language.Russian
    #     elif "en" in language or "aнгл" in language:
    #         language = Language.English
    #     ChatterModel.update_language(self.session, ctx.author.name, new_language=language.value)
    #     await ctx.send('Success!')

    @commands.command()
    async def remove_bot(self, ctx: commands.Context):
        if ctx.channel.name not in (ctx.author.name, BOT_NAME):
            return

        for channel in ChannelModel.get_all(session=self.session):
            if channel.name == ctx.author.name:
                await self.part_channels([ctx.author.name])

                ChannelModel.delete_channel(
                    session=self.session,
                    channel_name=ctx.author.name
                )
                self.channels.pop(ctx.author.name)

                await ctx.send('Success. Its a pity to miss you..')
                break
        else:
            await ctx.send("Bot is not working in your channel at the moment.")

    async def _start_bot(self, context_channel, new_channel):
        await self.join_channels([context_channel.name])
        self.channels[context_channel.name] = new_channel

    async def event_ready(self):
        for channel in ChannelModel.get_all(session=self.session):
            self.channels[channel.name] = Channel(
                channel.dota_player_id,
                channel.steam_link,
                channel.donation_link,
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
        lina_acceptable_commands = ('!setup_help', '!setup_donation', '!setup_dota', '!setup_socials', '!setup_steam', "!add_bot")

        if message.channel.name == BOT_NAME:
            if message.author.name in self.channels and self.channels[message.author.name].is_complete():
                await message.channel.send(f"{message.author.mention} Your setup is completed. You can now leave this page.")
                return
            if command not in lina_acceptable_commands:
                message.content = '!bot_help'
            await self.handle_commands(message)
            return

        if self.channels[message.channel.name].is_online or command == "!bot_on":
            await self.check_message(message)
            await self.handle_commands(message)

    async def check_message(self, message):
        content = message.content.lower()
        for word in self.__BANNED_WORDS:
            if word in content:
                await message.channel.send(f'{message.author.mention} не ругайся!  PunOko')
                break

    @commands.command()
    async def help(self, ctx: commands.Context):
        if self.channels[ctx.channel.name].is_complete():
            await ctx.send(f'''
               KonCha Available commands - !help, !rank, !wr, !mmr, !last, !donate, !steam, !social.
               Thanks for watching my stream! <3
            ''')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def donate(self, ctx: commands.Context):
        channel = self.channels[ctx.channel.name]
        if channel.is_complete():
            await ctx.send(f'{ctx.author.mention} Support me: {channel.donate_link}  TehePelo ')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def social(self, ctx: commands.Context):
        channel = self.channels[ctx.channel.name]
        if channel.is_complete():
            socials = ' , '.join(channel.socials)
            await ctx.send(f'{ctx.author.mention} <3  You can find me here: {socials}')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def steam(self, ctx: commands.Context):
        channel = self.channels[ctx.channel.name]
        if channel.is_complete():
            await ctx.send(f'{ctx.author.mention} My steam - {channel.steam_link}  TPFufun')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def wr(self, ctx: commands.Context):
        if self.channels[ctx.channel.name].is_complete():
            win, lose = self.channels[ctx.channel.name].opendota.get_player_win_rate()
            if win or lose:
                message = f'W {win} - L {lose}. {"PunOko" if win <= lose else "PogChamp"}'
            else:
                message = 'There were no games in today stream.. PunOko'
            await ctx.send(f'{ctx.author.mention} {message}')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def last(self, ctx: commands.Context):
        if self.channels[ctx.channel.name].is_complete():
            try:
                game = self.channels[ctx.channel.name].opendota.get_last_game()
                k, d, a = game.KDA
                game_result = 'WIN VoteYea' if game.result.lower() == "won match" else "LOSE VoteNay"
                message = f'{game_result}. Hero - {game.hero_name}, KDA - {k}/{d}/{a}.' \
                          f' Duration - {game.duration}. Game: {game.match_link[12:]}'
            except IndexError:
                message = 'There were no games in today stream.. PunOko'
            await ctx.send(f'{ctx.author.mention} {message}')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def rank(self, ctx: commands.Context):
        if self.channels[ctx.channel.name].is_complete():
            rank = self.channels[ctx.channel.name].opendota.get_player_rank()
            await ctx.send(f'{ctx.author.mention} {rank}')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def mmr(self, ctx: commands.Context):
        if self.channels[ctx.channel.name].is_complete():
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

            await ctx.send(f'{ctx.author.mention}, You are - {mmr} mmr {name} {emoji}')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def bot_off(self, ctx: commands.Context):
        if not ctx.author.name == ctx.channel.name:
            return

        if not self.channels[ctx.channel.name].is_complete():
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")
            return

        self.channels[ctx.channel.name].opendota.clear_match_story()
        self.channels[ctx.channel.name].is_online = False
        await ctx.send('OFF')

    @commands.command()
    async def bot_on(self, ctx: commands.Context):
        if not ctx.author.name == ctx.channel.name:
            return

        if not self.channels[ctx.channel.name].is_complete():
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")
            return

        if self.channels[ctx.channel.name].is_online:
            await ctx.send('Bot is already working')
            return

        self.channels[ctx.channel.name].is_online = True
        self.channels[ctx.channel.name].opendota.refresh_last_match()
        await ctx.send('Bot is ready to work!')

    @commands.command()
    async def change_dota_id(self, ctx: commands.Context, new_id: int):
        if not ctx.author.name == ctx.channel.name:
            return

        if self.channels[ctx.channel.name].is_complete():
            response = self.channels[ctx.channel.name].opendota.change_player_id(new_id)
            if response:
                self.channels[ctx.channel.name].dota_player_id = new_id
            await ctx.send('DONE' if response else 'An error occurred during !change_dota_id ')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def change_steam(self, ctx: commands.Context, new_link: str):
        if not ctx.author.name == ctx.channel.name:
            return

        if self.channels[ctx.channel.name].is_complete():
            response = self.channels[ctx.channel.name].steam_link = new_link
            await ctx.send('DONE' if response else 'An error occurred during !change_steam ')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def change_donation(self, ctx: commands.Context, new_link: str):
        if not ctx.author.name == ctx.channel.name:
            return

        if self.channels[ctx.channel.name].is_complete():
            response = self.channels[ctx.channel.name].donate_link = new_link
            await ctx.send('DONE' if response else 'An error occurred during !change_donation ')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def change_socials(self, ctx: commands.Context, *socials):
        if not ctx.author.name == ctx.channel.name:
            return

        if self.channels[ctx.channel.name].is_complete():
            response = self.channels[ctx.channel.name].socials = socials
            await ctx.send('DONE' if response else 'An error occurred during !change_socials ')
        else:
            await ctx.send(f"You can't use this command yet. Setup the bot in twitch.tv/linadotabot .")

    @commands.command()
    async def bot_help(self, ctx: commands.Context):
        message = f"Hello! This is auto reply message. If you want to add the @linadotabot to your channel - " \
                   f" use the !add_bot command.Important - follow all instructions to setup the bot afterwards. :)"

        await ctx.send(message)

    async def _check_setup_process(self, ctx: commands.Context):
        channel = self.channels[ctx.author.name]
        channel_is_added = channel.add_to_database(self.session, ctx.author.name)
        if channel_is_added or channel.is_in_database:
            await ctx.send('You are now able to use the bot! Congratulation! Good luck in your adventure! ')
        else:
            await ctx.send('You have some more steps left. In case you struggle, just use !setup_help.')

    @commands.command()
    async def setup_dota(self, ctx: commands.Context, dota_player_id: int):
        if not ctx.channel.name == BOT_NAME:
            return
        if ctx.author.name in self.channels:
            self.channels[ctx.author.name].setup_dota(dota_player_id)
            await ctx.send(f'Success. Your dota id is {dota_player_id}.')
        else:
            await ctx.send('You forgot to !add_bot :(')

        await self._check_setup_process(ctx)

    @commands.command()
    async def setup_socials(self, ctx: commands.Context, *socials):
        if not ctx.channel.name == BOT_NAME:
            return
        if ctx.author.name in self.channels:
            for social in socials:
                self.channels[ctx.author.name].add_social(social)
            await ctx.send(f'Success.')
        else:
            await ctx.send('You forgot to !add_bot :(')

        await self._check_setup_process(ctx)

    @commands.command()
    async def setup_steam(self, ctx: commands.Context, steam_link: str):
        if not ctx.channel.name == BOT_NAME:
            return
        if ctx.author.name in self.channels:
            self.channels[ctx.author.name].setup_steam(steam_link)
            await ctx.send(f'Success. Your steam link is: {steam_link} ')
        else:
            await ctx.send('You forgot to !add_bot :(')

        if self.channels[ctx.author.name].is_complete():
            await ctx.send('You are now able to use the bot! Congratulation! Good luck in your adventure! ')

        await self._check_setup_process(ctx)

    @commands.command()
    async def setup_donation(self, ctx: commands.Context, donation_link: str):
        if not ctx.channel.name == BOT_NAME:
            return
        if ctx.author.name in self.channels:
            self.channels[ctx.author.name].setup_donation(donation_link)
            await ctx.send(f'Success. Your donation link is: {donation_link}')
        else:
            await ctx.send('You forgot to !add_bot :(')

        await self._check_setup_process(ctx)

    @commands.command()
    async def setup_help(self, ctx: commands.Context):
        if not ctx.channel.name == BOT_NAME:
            return
        if self.channels[ctx.author.name].is_complete():
            await ctx.send('You are now able to use the bot! Congratulation! Good luck in your adventure! ')
        else:
            message = f"""
                To setup the bot, you need to use 4 commands in ANY order.
                Commands are: !setup_donation, !setup_steam, !setup_dota, !setup_socials.
                More help and information about all commands
                you can find under twitch.tv/linadotabot/about .  
            """
            await ctx.send(message)


def main():
    Base.metadata.create_all(engine)
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
