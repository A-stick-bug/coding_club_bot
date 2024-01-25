from PIL import ImageDraw, ImageFont, ImageOps, Image
import requests
from io import BytesIO
import os

from user_data import UserData, USER_DATA_DIRECTORY

from common import (
    BLACK, WHITE, GREEN, BLUE, ORANGE, YELLOW,
    FONT_PATH,
    draw_user_avatar, text_shadow
)

font_leaderboard = ImageFont.truetype(FONT_PATH, 55)
font_username = ImageFont.truetype(FONT_PATH, 38)


def get_top_users():
    """
    Returns data for the top users in the server.
    At most 10 entries will be returned.
    """
    users = []
    for partial_filename in os.listdir(USER_DATA_DIRECTORY):
        if partial_filename.endswith(".txt"):
            full_filename = f"{USER_DATA_DIRECTORY}/{partial_filename}"
            users.append(UserData.from_filename(full_filename))
    users.sort(key=lambda user_data: user_data.experience, reverse=True)
    return users[:10]


def make_leaderboard(bot) -> str:
    """
    Generates the current server-wide leaderboard.
    Returns the filename of the generated leaderboard.
    """
    top_users = get_top_users()

    img_size = img_width, img_height = 800, 1110
    img = Image.new("RGB", img_size, BLUE)
    draw = ImageDraw.Draw(img)

    text_shadow(draw, (img_width // 2, 55), "Leaderboard", font_leaderboard, anchor="mm")

    for i, user_data in enumerate(top_users):
        bounding_box = (25, i * 100 + 110, img_width - 25, i * 100 + 185)
        draw.rounded_rectangle(bounding_box, 15, GREEN)

        # Draw the user's avatar
        user = bot.get_user(user_data.user_id)
        if user:
            draw_user_avatar(user, img, 55, (35, i * 100 + 120))

        # Write the user's position in the leaderboard
        position = f"{i + 1}. "
        if i <= 2:
            text_shadow(draw, (105, i * 100 + 148), position, font_username, fore=YELLOW, back=BLACK, anchor="lm")
        else:
            draw.text((105, i * 100 + 148), position, BLACK, font_username, anchor="lm")

        # Write the user's name
        username = " " * len(position)
        username += user.name if user else "[unknown user]"
        draw.text((105, i * 100 + 148), username, BLACK, font_username, anchor="lm")
        draw.text((img_width - 35, i * 100 + 148), f"Level {user_data.level}", BLACK, font_username, anchor="rm")

    img.save("assets/temp_leaderboard.png")
    return "assets/temp_leaderboard.png"
