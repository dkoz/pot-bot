# Path of Titans RCON Bot
![Discord](https://img.shields.io/discord/1009881575187566632?style=flat-square&label=support)

 A Path of Titans discord bot designed to allow remote rcon between multiple servers using my asynchronous rcon protocol.

 I made this to test my rcon protocol. I probably won't develop this any further unless there's some interest. Feel free to join my [discord](https://discord.gg/3HUq8cJSrX).

## Environment Variables
You need to rename the `.env.example` to `.env` when you fill out the required fields.
```
BOT_TOKEN='TOKEN_HERE'
BOT_PREFIX=!
```

## Server Configuration
This is an example RCON configuration for your servers.
```
{
    "RCON_SERVERS": {
        "My Server": {
            "RCON_HOST": "127.0.0.1",
            "RCON_PORT": 7779,
            "RCON_PASS": "examplePass",
            "SERVER_PORT": 7777,
            "QUERY_PORT": 7778
        }
    },
    "WEATHER_CHANNEL": 12345678,
    "WEATHER_REPORT": 12345678,
    "WEATHER_PATTERN": 12345678
}
```
## Installation
1. Install the requirements
```
py -m pip install -r requirements.txt
```
2. Configure the `.env` and `config.json` files.

3. Run the bot!
```
py main.py
```