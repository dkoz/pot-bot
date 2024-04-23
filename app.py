from flask import Flask, request, jsonify, g
import requests
import logging
from utils.database import Database
import settings

app = Flask(__name__)

DISCORD_WEBHOOK_URL = settings.webhook_url

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

def send_to_discord(content):
    payload = {"content": content}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error sending to Discord: {e}")

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

        send_to_discord(f"Player '{player_name}' logged in to server '{server_name}'")

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

        send_to_discord(f"Player '{player_name}' logged out from server '{server_name}'")

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

        send_to_discord(f"{player_name} ({player_alderon_id}) has respawned at {location}!")

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

        send_to_discord(f"Victim '{victim_name}' was killed by '{killer_name}' at '{victim_poi}' during '{time_of_day}'.")

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

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=8000)
