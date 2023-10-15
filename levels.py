import random
import math
import time

from dmoj import fetch_points
from user_data import UserData, get_user_data


def handle_message_sent(ctx, is_slash_command=True) -> None:
    """
    Updates the experience and level of the user who sent a message or used a slash command.
    """
    user_data = get_user_data(ctx.author.id)
    if user_data is not None:
        _handle_message_sent_user_data(ctx, user_data, is_slash_command)
        user_data.save_to_file()

def _handle_message_sent_user_data(ctx, user_data: UserData, is_slash_command: bool) -> None:
    user_data.messages += 1
    
    time_now = int(time.time())
    if time_now < user_data.next_experience_gain_time:
        return
    
    user_data.next_experience_gain_time = time_now + 30
    
    #Increase experience
    gained_experience = random.randint(5, 10)
    if is_slash_command:
        gained_experience *= 5
    elif len(ctx.content) > 0:
        gained_experience *= 1 + math.log(len(ctx.content))
    else:
        gained_experience *= 3
    
    user_data.experience += round(gained_experience)
    
    if user_data.experience >= get_next_level_experience(user_data.level):
        user_data.level += 1
    
    print(gained_experience, "experience earned")


def get_next_level_experience(level: int) -> int:
    """
    Returns the total amount of experience required to reach level `level + 1`.
    """
    levels_sum = level * (level + 1) // 2
    return 150 + levels_sum * 500


def get_next_level_percentage(user_data: UserData) -> float:
    """
    Returns how close the user is to attaining the next level.
    """
    level = user_data.level
    if level == 0:
        previous_level_experience = 0
    else:
        previous_level_experience = get_next_level_experience(level - 1)
    next_level_experience = get_next_level_experience(level)
    delta_experience = next_level_experience - previous_level_experience
    
    current_level_experience = user_data.experience - previous_level_experience
    
    return current_level_experience / delta_experience

