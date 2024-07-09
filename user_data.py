from __future__ import annotations
from dataclasses import dataclass
import os
import mysql.connector as connector
from dotenv import load_dotenv

# connect to database
load_dotenv("environment/.env")
database_password = os.getenv("DATABASE_PASSWORD")
db = connector.connect(host="localhost",
                       username="root",
                       password=database_password,
                       database="coding_club_bot")
print("Database connection successful")

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
        control = db.cursor()

        # add user to database if it doesn't exist yet
        control.execute(f"select * from user_data where user_id = '{self.user_id}'")
        length = 0
        for _ in control:
            length += 1
        if length == 0:
            control.execute(f"insert into user_data values ('{self.user_id}', '', 0, 0, 0, 0)")
            db.commit()

        # put the user_object's information into the database
        query = f"""update user_data set 
        user_id = '{self.user_id}',
        dmoj_username = '{self.dmoj_username}',
        user_level = {self.level},
        experience = {self.experience},
        messages = {self.messages},
        next_experience_gain_time = {self.next_experience_gain_time} 
        where user_id = '{self.user_id}'"""
        control.execute(query)
        db.commit()


def get_user_data(user_id: int) -> UserData | None:
    """
    Returns a UserData object containing the given user's data.
    Returns `None` if the given id does not exist in the database
    """
    control = db.cursor()
    control.execute(f"select * from user_data where user_id = '{user_id}'")
    try:
        return UserData(*next(control))  # return first and only element returned from query
    except StopIteration:
        return None


def get_top_users():
    """
    Returns data for the top users in the server.
    At most 10 entries will be returned.
    """
    control = db.cursor()
    control.execute("select * from user_data order by experience desc limit 10")
    return [UserData(*user) for user in control]


if __name__ == '__main__':
    dt = get_user_data(123)
    dt.experience = 9999999
    dt.save_to_db()
