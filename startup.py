# Starts up the flask app and discord bot.
from multiprocessing import Process, freeze_support
import subprocess
import signal
import sys

def start_discord():
    subprocess.call(["python", "main.py"])

def start_flask():
    subprocess.call(["python", "app.py"])

if __name__ == '__main__':
    freeze_support()

    discord_process = Process(target=start_discord)
    flask_process = Process(target=start_flask)

    def signal_handler(sig, frame):
        print("Terminating both processes...")

        discord_process.terminate()
        flask_process.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    discord_process.start()
    flask_process.start()

    discord_process.join()
    flask_process.join()
