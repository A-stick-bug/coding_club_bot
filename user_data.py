from __future__ import annotations
from dataclasses import dataclass
import os

USER_DATA_DIRECTORY = "userdata"


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
    
    def save_to_file(self) -> None:
        """
        Saves this object's user data to the appropriate file.
        """
        text = f"{self.user_id}\n{self.dmoj_username}\n{self.level}\n{self.experience}\n{self.messages}\n{self.next_experience_gain_time}"
        filename = get_user_id_filename(self.user_id)
        with open(filename, "w") as save_file:
            save_file.write(text)
    
    @staticmethod
    def from_filename(filename: str) -> UserData | None:
        """
        Creates a UserData object from a filename.
        Returns `None` if the given file does not exist.
        """
        try:
            with open(filename, "r") as user_data_file:
                raw_data = user_data_file.read()
                data = raw_data.split("\n")
                return UserData(
                    user_id=int(data[0]),
                    dmoj_username=data[1],
                    level=int(data[2]),
                    experience=int(data[3]),
                    messages=int(data[4]),
                    next_experience_gain_time=int(data[5])
                )
        except FileNotFoundError:
            return None


def get_user_id_filename(user_id: int) -> str:
  """
  Returns the name of the file in which the given user's data can be saved.
  """
  return f"{USER_DATA_DIRECTORY}/{user_id}.txt"


def get_user_data(user_id: int) -> UserData | None:
    """
    Returns a UserData object containing the given user's data.
    """
    return UserData.from_filename(get_user_id_filename(user_id))

