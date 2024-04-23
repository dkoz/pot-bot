import sqlite3
from typing import Optional, Tuple, List

class Database:
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        with self.connection:
            # Create players table if it doesn't exist
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY,
                    in_game_name TEXT,
                    alderon_id TEXT UNIQUE,
                    kills INTEGER DEFAULT 0,
                    deaths INTEGER DEFAULT 0,
                    dinosaur TEXT,
                    location TEXT
                )
                """
            )
            # Create link table if it doesn't exist
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS link (
                    discord_id INTEGER UNIQUE,
                    discord_name TEXT,
                    alderon_id TEXT UNIQUE
                )
                """
            )

    def insert_player(self, name: str, alderon_id: str):
        with self.connection:
            self.connection.execute(
                "INSERT INTO players (name, alderon_id) VALUES (?, ?)",
                (name, alderon_id),
            )

    def link_discord_to_alderon(self, discord_id: int, discord_name: str, alderon_id: str):
        with self.connection:
            self.connection.execute(
                "INSERT INTO link (discord_id, discord_name, alderon_id) VALUES (?, ?, ?)",
                (discord_id, discord_name, alderon_id),
            )

    def update_player(
        self,
        alderon_id: str,
        kills: Optional[int] = None,
        deaths: Optional[int] = None,
        dinosaur: Optional[str] = None,
        location: Optional[str] = None,
    ):
        with self.connection:
            self.connection.execute(
                """
                UPDATE players
                SET kills = COALESCE(?, kills),
                    deaths = COALESCE(?, deaths),
                    dinosaur = COALESCE(?, dinosaur),
                    location = COALESCE(?, location)
                WHERE alderon_id = ?
                """,
                (kills, deaths, dinosaur, location, alderon_id),
            )
            
    def increment_stat(self, alderon_id: str, stat: str, increment_by: int = 1):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT {stat} FROM players WHERE alderon_id = ?", (alderon_id,))
        result = cursor.fetchone()

        if result is not None:
            current_value = result[0]
            new_value = current_value + increment_by

            cursor.execute(
                f"UPDATE players SET {stat} = ? WHERE alderon_id = ?",
                (new_value, alderon_id),
            )
            self.connection.commit()
        else:
            raise ValueError(f"Player with AlderonId {alderon_id} not found.")

    def get_player(self, alderon_id: str) -> Optional[Tuple[int, str, str]]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM players WHERE alderon_id = ?", (alderon_id,))
        return cursor.fetchone()

    def get_player_by_alderon_id(self, alderon_id: str) -> Optional[Tuple[int, str, str, int, int, str, str]]:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT name, alderon_id, kills, deaths, dinosaur, location FROM players WHERE alderon_id = ?", 
            (alderon_id,)
        )
        return cursor.fetchone()

    def get_player_by_discord_id(self, discord_id: int) -> Optional[str]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT alderon_id FROM link WHERE discord_id = ?", (discord_id,))
        result = cursor.fetchone()

        return result[0] if result else None

    def get_all_players(self) -> List[Tuple[int, str, str]]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM players")
        return cursor.fetchall()

    def close(self):
        self.connection.close()