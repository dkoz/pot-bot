# Path of Titans RCON Bot
![Discord](https://img.shields.io/discord/1009881575187566632?style=flat-square&label=support)

 A Path of Titans discord bot designed to allow remote rcon between multiple servers using my asynchronous rcon protocol.

 This bot was designed for a server called Envirma. I don't have time to develop this any further. Fork it and use it if you want. Feel free to join my [discord](https://discord.gg/3HUq8cJSrX).

## Features
- RCON Control
- Webhook Server
- Leaderboards
- Weather System
- Server Monitor
- Alderon ID
- Player Profiles

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
    }
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