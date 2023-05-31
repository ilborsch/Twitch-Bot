# Twitch Bot for Dota 2 streamers - Lina

<p align="center">
    <img src="https://img.shields.io/badge/TwitchIO%20v.-2.6.0-brightgreen" alt="TwitchIO version">
    <img src="https://img.shields.io/badge/Python-3.9-green" alt="Python version">
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>
<p align="center">
    <img src="https://srv4.imgonline.com.ua/result_img/imgonline-com-ua-Resize-2dw0DqERAH0.png">
</p>

## Description


Twitch Bot builded using TwitchIO asynchronous library. Project also contains DotaBuff scraper and OpenDota API parsing script which receive and process data needed for proper and efficient Bot work.
Bot commands:

- !help - Help information about available commands.
- !greet - Greets chatter
- !rank - Responds with streamer's rank
- !wr - Responds with streamer's WinRate for the stream
- !mmr - MMR randomizer. Funny command.
- !last - Responds with information about last streamer's match.
- !donate - Responds with donation info.
- !steam - Responds with Steam account link.
- !social - Responds with streamer's social links.
- !bot_off - Turns bot OFF. (locks commands + cleans dota matches story. Needed to properly analyze stream data. )
- !bot_on - Turns bot ON.
- !change_dota_id {id} - changes Player dota id. 

Routines:

- Social routine - sends social links every 70 mins.
- Donation routine - sends donation info every 60 mins.


## Run Locally

Clone the project

```bash
  git clone https://github.com/ilborsch/Twitch-Lina-Bot.git
```

Go to the project directory

```bash
  cd Twitch-Lina-Bot
```

Install packets

```bash
  pip install -r requirements.txt
```

Start the server

```bash
   python bot.py
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`TMI_TOKEN` - TMI token you get from Twitch

`CLIENT_ID` - Client ID you get from Twitch

`CLIENT_SECRET` - Client Secret you get from Twitch

`BOT_NAME` - Your Bot name

`BOT_PREFIX` - Command prefix 

`CHANNEL` - Channel which is used for the Bot

`DOTA_PLAYER_ID` - Dota player ID 

`VK` - VK page link (needed for command !social )

`INSTAGRAM` - IG page link (needed for command !social )

`STEAM` - Steam page link (needed for command !steam )

`DONATE` - Donation page link (needed for command !donate )



## Authors

- [@ilborsch](https://www.github.com/ilborsch)


## License

[MIT](https://choosealicense.com/licenses/mit/)
