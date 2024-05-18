from flask import Flask, request, jsonify, g
import discord
import requests
import logging
from utils.database import Database
import settings

app = Flask(__name__)

DISCORD_WEBHOOK_URL = settings.webhook_url

WEBHOOKS = {
    'login': settings.webhook_login,
    'logout': settings.webhook_logout,
    'respawn': settings.webhook_respawn,
    'killed': settings.webhook_killed,
    'admincommand': settings.webhook_admincommand,
    'adminspectate': settings.webhook_adminspectate,
    'playerchat': settings.webhook_playerchat,
    'playerdamage': settings.webhook_playerdamage,
    'playerreport': settings.webhook_playerreport,
    'playerleave': settings.webhook_playerleave,
    'waystone': settings.webhook_waystone,
    'questcomplete': settings.webhook_questcomplete,
    'questfailed': settings.webhook_questfailed
}

def get_db():
    if 'db' not in g:
        g.db = Database("players.db")
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_to_discord(embed=None, content=None, webhook_url=None):
    if not webhook_url:
        webhook_url = DISCORD_WEBHOOK_URL

    payload = {}
    if content:
        payload["content"] = content
    if embed:
        payload["embeds"] = [embed.to_dict()]

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error sending to Discord: {e}")

@app.route('/')
def index():
    return "Webhook Server is running."

@app.route('/health')
def health():
    health_data = {}

    for event, url in WEBHOOKS.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            health_data[event] = {"status": "OK"}
        except requests.RequestException as e:
            health_data[event] = {"status": "Error", "message": str(e)}

    return jsonify(health_data)

@app.route('/pot/login', methods=['POST'])
def login():
    request_data = request.get_json()

    db = get_db()
    try:
        server_name = request_data['ServerName']
        player_name = request_data['PlayerName']
        alderon_id = request_data['AlderonId']
        battleye_guid = request_data['BattlEyeGUID']
        is_admin = request_data['bServerAdmin']

        if db.get_player(alderon_id):
            db.update_player(alderon_id)
        else:
            db.insert_player(player_name, alderon_id)

        db.connection.commit()
        
        embed = discord.Embed(
            title=f"Player Connected",
            description=f"{player_name} ({alderon_id}) has logged in to {server_name}.",
            color=discord.Color.blurple()
        )

        send_to_discord(embed=embed, webhook_url=WEBHOOKS['login'])

        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/pot/logout', methods=['POST'])
def logout():
    request_data = request.get_json()

    try:
        server_name = request_data['ServerName']
        player_name = request_data['PlayerName']
        alderon_id = request_data['AlderonId']
        battleye_guid = request_data['BattlEyeGUID']
        
        embed = discord.Embed(
            title=f"Player Disconnected",
            description=f"{player_name} ({alderon_id}) has logged out of {server_name}.",
            color=discord.Color.blurple()
        )

        send_to_discord(embed=embed, webhook_url=WEBHOOKS['logout'])

        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/pot/respawn', methods=['POST'])
def respawn():
    request_data = request.get_json()

    db = get_db()
    try:
        player_name = request_data['PlayerName']
        player_alderon_id = request_data['PlayerAlderonId']
        location = request_data['Location']
        dinosaur_type = request_data['DinosaurType']
        dinosaur_growth = request_data['DinosaurGrowth']

        db.update_player(player_alderon_id, location=location, dinosaur=dinosaur_type)

        db.connection.commit()
        
        embed = discord.Embed(
            title=f"Player Respawned",
            description=f"{player_name} ({player_alderon_id}) has respawned at {location}\nDinosaur: {dinosaur_type} ({dinosaur_growth})",
            color=discord.Color.blurple()
        )

        send_to_discord(embed=embed, webhook_url=WEBHOOKS['respawn'])

        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/pot/killed', methods=['POST'])
def killed():
    request_data = request.get_json()

    db = get_db()
    try:
        time_of_day = request_data['TimeOfDay']
        damage_type = request_data['DamageType']
        victim_poi = request_data['VictimPOI']
        victim_name = request_data['VictimName']
        victim_alderon_id = request_data['VictimAlderonId']
        victim_dinosaur_type = request_data['VictimDinosaurType']
        victim_role = request_data['VictimRole']
        victim_is_admin = request_data['VictimIsAdmin']
        victim_growth = request_data['VictimGrowth']
        victim_location = request_data['VictimLocation']
        killer_name = request_data['KillerName']
        killer_alderon_id = request_data['KillerAlderonId']
        killer_dinosaur_type = request_data['KillerDinosaurType']
        killer_role = request_data['KillerRole']
        killer_is_admin = request_data['KillerIsAdmin']
        killer_growth = request_data['KillerGrowth']
        killer_location = request_data['KillerLocation']

        if db.get_player(victim_alderon_id):
            db.increment_stat(victim_alderon_id, 'deaths')
            db.update_player(victim_alderon_id, dinosaur=victim_dinosaur_type,location=victim_location)

        if db.get_player(killer_alderon_id):
            db.increment_stat(killer_alderon_id, 'kills')
            db.update_player(killer_alderon_id, dinosaur=killer_dinosaur_type, location=killer_location)
        else:
            logging.warning("Killer not found in the database.")

        db.connection.commit()

        embed = discord.Embed(
            title=f"Player Killed",
            description=(
                f"Time of Day: {time_of_day}\n"
                f"Damage Type: {damage_type}"
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Victim",
            value=(
                f"Player: {victim_name} ({victim_alderon_id})\n"
                f"Admin: {victim_is_admin}\n"
                f"Dinosaur: {victim_dinosaur_type} ({victim_growth})\n"
                f"Location: {victim_poi}\n"
                f"Coordinates: {victim_location}"
            ),
            inline=False
        )

        embed.add_field(
            name="Killer",
            value=(
                f"Player: {killer_name} ({killer_alderon_id})\n"
                f"Admin: {killer_is_admin}\n"
                f"Dinosaur: {killer_dinosaur_type} ({killer_growth})\n"
                f"Coordinates: {killer_location}"
            ),
            inline=False
        )
        
        send_to_discord(embed=embed, webhook_url=WEBHOOKS['killed'])

        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/pot/admincommand', methods=['POST'])
def admincommand():
    request_data = request.get_json()

    try:
        admin_name = request_data['AdminName']
        admin_id = request_data['AdminAlderonId']
        admin_role = request_data['Role']
        admin_command = request_data['Command']

        embed = discord.Embed(
            title=f"Admin Command",
            description=f"{admin_name} ({admin_id}) used the command: {admin_command}",
            color=discord.Color.blurple()
        )

        send_to_discord(embed=embed, webhook_url=WEBHOOKS['admincommand'])

        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/pot/adminspectate', methods=['POST'])
def adminspectate():
    request_data = request.get_json()

    try:
        admin_name = request_data['AdminName']
        admin_id = request_data['AdminAlderonId']
        admin_action = request_data['Action']

        embed = discord.Embed(
            title=f"Admin Spectate",
            description=f"{admin_name} ({admin_id}) used action: {admin_action}",
            color=discord.Color.blurple()
        )

        send_to_discord(embed=embed, webhook_url=WEBHOOKS['adminspectate'])

        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/pot/playerchat', methods=['POST'])
def playerchat():
    request_data = request.get_json()

    try:
        channel_id = request_data['ChannelId']
        channel_name = request_data['ChannelName']
        player_name = request_data['PlayerName']
        message = request_data['Message']
        alderon_id = request_data['AlderonId']
        is_admin = request_data['bServerAdmin']
        whisper = request_data['FromWhisper']

        embed = discord.Embed(
            title=f"Player Chat",
            description=(
                f"Player: {player_name} ({alderon_id})\n"
                f"Channel: {channel_name} ({channel_id})\n"
                f"Whisper: {whisper}\n"
                f"Admin: {is_admin}"
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Message",
            value=message,
            inline=False
        )

        send_to_discord(embed=embed, webhook_url=WEBHOOKS['playerchat'])

        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/pot/playerdamage', methods=['POST'])
def playerdamage():
    request_data = request.get_json()
    
    try:
        source_name = request_data['SourceName']
        source_alderon_id = request_data['SourceAlderonId']
        source_role = request_data['SourceRole']
        source_dinosaur_type = request_data['SourceDinosaurType']
        source_admin = request_data['SourceIsAdmin']
        source_growth = request_data['SourceGrowth']
        damage_type = request_data['DamageType']
        damage_amount = request_data['DamageAmount']
        target_name = request_data['TargetName']
        target_alderon_id = request_data['TargetAlderonId']
        target_dinosaur_type = request_data['TargetDinosaurType']
        target_role = request_data['TargetRole']
        target_admin = request_data['TargetIsAdmin']
        target_growth = request_data['TargetGrowth']
        
        embed = discord.Embed(
            title=f"Player Damage",
            description=f"{source_name} ({source_alderon_id}) dealt {damage_amount} ({damage_type}) damage to {target_name} ({target_alderon_id}).",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="Source",
            value=(
                f"Player: {source_name} ({source_alderon_id})\n"
                f"Admin: {source_admin}\n"
                f"Role: {source_role}\n"
                f"Dinosaur: {source_dinosaur_type} ({source_growth})"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Target",
            value=(
                f"Player: {target_name} ({target_alderon_id})\n"
                f"Admin: {target_admin}\n"
                f"Role: {target_role}\n"
                f"Dinosaur: {target_dinosaur_type} ({target_growth})"
            ),
            inline=False
        )
        
        send_to_discord(embed=embed, webhook_url=WEBHOOKS['playerdamage'])
        
        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/pot/playerreport', methods=['POST'])
def playerreport():
    request_data = request.get_json()
    
    try:
        reporter_name = request_data['ReporterPlayerName']
        reporter_alderon_id = request_data['ReporterAlderonId']
        server_name = request_data['ServerName']
        secure = request_data['Secure']
        reported_name = request_data['ReportedPlayerName']
        reported_alderon_id = request_data['ReportedAlderonId']
        reported_platform = request_data['ReportedPlatform']
        report_type = request_data['ReportType']
        report_reason = request_data['ReportReason']
        recent_damage_causer_ids = request_data['RecentDamageCauserIDs']
        nearby_player_ids = request_data['NearbyPlayerIDs']
        title = request_data['Title']
        message = request_data['Message']
        location = request_data['Location']
        version = request_data['Version']
        platform = request_data['Platform']
        
        embed = discord.Embed(
            title=f"Player Report - {server_name}",
            description=f"{reporter_name} ({reporter_alderon_id}) has submitted a report on {platform}.",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="Report",
            value=(
                f"Reported: {reported_name} ({reported_alderon_id})\n"
                f"Title: {title}\n"
                f"Type: {report_type}\n"
                f"Reason: {report_reason}\n"
                f"Secure: {secure}\n"
                f"Platform: {reported_platform}\n"
                f"Location: {location}\n"
                f"Version: {version}\n"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Recent Damage Causers",
            value=", ".join(recent_damage_causer_ids) if recent_damage_causer_ids else "None reported",
            inline=False
        )

        embed.add_field(
            name="Nearby Players",
            value=", ".join(nearby_player_ids) if nearby_player_ids else "None reported",
            inline=False
        )
        
        embed.add_field(
            name="Message",
            value=message,
            inline=False
        )            
        
        send_to_discord(embed=embed, webhook_url=WEBHOOKS['playerreport'])
        
        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/pot/waystone', methods=['POST'])
def waystone():
    request_data = request.get_json()
    
    try:
        inviter_name = request_data['InviterName']
        inviter_alderonid = request_data['InviterAlderonId']
        player_name = request_data['TeleportedPlayerName']
        player_alderonid = request_data['TeleportedPlayerAlderonId']
        
        embed = discord.Embed(
            title=f"Waystone Teleport",
            description=f"{inviter_name} ({inviter_alderonid}) teleported {player_name} ({player_alderonid}) to a waystone.",
            color=discord.Color.blurple()
        )
        
        send_to_discord(embed=embed, webhook_url=WEBHOOKS['waystone'])
        
        return jsonify({"status": "success"}), 200
    
    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/pot/questcomplete', methods=['POST'])
def questcomplete():
    request_data = request.get_json()
    
    try:
        quest_name = request_data['Quest']
        quest_id = request_data['QuestRewardGrowth']
        quest_marks = request_data['QuestRewardMarks']
        player_name = request_data['PlayerName']
        player_alderonid = request_data['PlayerAlderonId']
        group_quest = request_data['GroupQuest']
        
        embed = discord.Embed(
            title=f"Quest Complete",
            description=f"{player_name} ({player_alderonid}) has completed the quest: {quest_name}",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="Rewards",
            value=(
                f"Growth: {quest_id}\n"
                f"Marks: {quest_marks}\n"
                f"Group Quest: {group_quest}"
            ),
            inline=False
        )
        
        send_to_discord(embed=embed, webhook_url=WEBHOOKS['questcomplete'])
        
        return jsonify({"status": "success"}), 200
    
    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/pot/questfailed', methods=['POST'])
def questfailed():
    request_data = request.get_json()
    
    try:
        quest_name = request_data['Quest']
        player_name = request_data['PlayerName']
        player_alderonid = request_data['PlayerAlderonId']
        group_quest = request_data['GroupQuest']
        
        embed = discord.Embed(
            title=f"Quest Failed",
            description=f"{player_name} ({player_alderonid}) has failed the quest: {quest_name}",
            color=discord.Color.blurple()
        )
        
        send_to_discord(embed=embed, webhook_url=WEBHOOKS['questfailed'])
        
        return jsonify({"status": "success"}), 200
    
    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/pot/playerleave', methods=['POST'])
def playerleave():
    request_data = request.get_json()
    
    try:
        player_name = request_data['PlayerName']
        player_alderonid = request_data['PlayerAlderonId']
        from_death = request_data['FromDeath']
        safe_log = request_data['SafeLog']
        character_name = request_data['CharacterName']
        dinosaur_type = request_data['DinosaurType']
        dinosaur_growth = request_data['DinosaurGrowth']
        player_location = request_data['Location']
        
        embed = discord.Embed(
            title=f"Player Leave",
            description=f"{player_name} ({player_alderonid}) has left the server.",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="Character",
            value=(
                f"Name: {character_name}\n"
                f"Dinosaur: {dinosaur_type} ({dinosaur_growth})\n"
                f"Location: {player_location}\n"
                f"From Death: {from_death}\n"
                f"Safe Log: {safe_log}"
            ),
            inline=False
        )
        
        send_to_discord(embed=embed, webhook_url=WEBHOOKS['playerleave'])
        
        return jsonify({"status": "success"}), 200
    
    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(host=settings.app_host, port=settings.app_port)