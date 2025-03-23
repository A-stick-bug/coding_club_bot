from __future__ import annotations
from dataclasses import dataclass

import os
import mysql.connector as connector
from mysql.connector import pooling
from dotenv import load_dotenv

# connect to database
load_dotenv("environment/.env")
database_password = os.getenv("DATABASE_PASSWORD")

dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": database_password,
    "database": "coding_club_bot"
}
pool = pooling.MySQLConnectionPool(pool_name="main_pool", pool_size=5, **dbconfig)
print("Database pool successfully created")

"""
Contains data for a particular bot user.
"""


@dataclass
class UserData:
    user_id: int
    """
    The ID of the user's Discord account.
    """

    dmoj_username: str
    """
    The user's DMOJ username.
    """

    level: int
    """
    The user's bot level.
    """

    experience: int
    """
    The user's bot experience.
    """

    messages: int
    """
    The number of messages sent by the user.
    """

    next_experience_gain_time: int
    """
    The earliest time when the user will be able to gain experience again.
    """

    def __post_init__(self):
        """Ensure user_id is an integer since the database stores them as str"""
        self.user_id = int(self.user_id)

    def save_to_db(self) -> None:
        """
        Saves this object's user data to the database.
        """
        db = pool.get_connection()
        try:
            with db.cursor() as control:
                # add user to database if it doesn't exist yet
                control.execute(f"SELECT * FROM user_data WHERE user_id = '{self.user_id}'")
                if not control.fetchone():  # doesn't exist yet
                    control.execute(f"INSERT INTO user_data VALUES ('{self.user_id}', '', 0, 0, 0, 0)")
                    db.commit()

                # update the user_object's information in the database
                query = f"""
                UPDATE user_data SET 
                user_id = '{self.user_id}',
                dmoj_username = %s,
                user_level = {self.level},
                experience = {self.experience},
                messages = {self.messages},
                next_experience_gain_time = {self.next_experience_gain_time}
                WHERE user_id = '{self.user_id}'
                """
                control.execute(query, [self.dmoj_username])
                db.commit()
        except Exception as e:
            print("Failed to save to db: " + str(e))
        finally:
            db.close()


def get_user_data(user_id: int) -> UserData | None:
    """
    Returns a UserData object containing the given user's data.
    Returns `None` if the given id does not exist in the database.
    """
    db = pool.get_connection()
    try:
        with db.cursor() as control:
            control.execute(f"SELECT * FROM user_data WHERE user_id = '{user_id}'")
            try:
                return UserData(*next(control))  # Return first and only element returned from query
            except StopIteration:
                return None
    except Exception as e:
        print("Failed to fetch user data from db: " + str(e))
    finally:
        db.close()


def get_top_users():
    """
    Returns data for the top users in the server.
    At most 10 entries will be returned.
    """
    db = pool.get_connection()
    try:
        with db.cursor() as control:
            control.execute("SELECT * FROM user_data ORDER BY experience DESC LIMIT 10")
            return [UserData(*user) for user in control]
    except Exception as e:
        print("Failed to fetch top users from db: " + str(e))
    finally:
        db.close()


if __name__ == '__main__':
    dt = get_user_data(123)
    dt.level = 9999999
    dt.dmoj_username = "Hello world"
    dt.save_to_db()
