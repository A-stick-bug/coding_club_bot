import discord
from PIL import ImageDraw, ImageFont, ImageOps, Image

from user_data import get_user_data
from dmoj import fetch_points
from levels import get_next_level_experience, get_next_level_percentage

from common import (
    BLACK, WHITE, GREEN, BLUE, ORANGE, YELLOW,
    FONT_PATH,
    draw_user_avatar, text_shadow
)

font_side = ImageFont.truetype(FONT_PATH, 30)
font_experience = ImageFont.truetype(FONT_PATH, 25)


def _create_base_image():
    """
    Creates the base image for `make_banner`.
    This function is not called from within the codebase; it is here for reproducibility.
    """
    img = Image.new("RGB", (800, 200), BLUE)
    draw = ImageDraw.Draw(img)

    # Background
    draw.ellipse((40, -240, 460, 300), GREEN)
    draw.rectangle((0, 0, 200, 200), GREEN)

    img.save("assets/fetch_points_base.png")


def draw_progress_bar_inside(bar_inside_image, width: int, height: int, percentage: float) -> None:
    """
    Draws the inside of a progress bar onto the given image.
    """
    bar_inside_draw = ImageDraw.Draw(bar_inside_image)
    x_end = width * percentage
    points = [(0, 0), (x_end + 5, 0), (x_end - 5, height), (0, height)]
    bar_inside_draw.polygon(points, YELLOW)


def draw_progress_bar(draw, dest, bounding_box, percentage: float) -> None:
    """
    Draws a progress bar onto the destination image.
    """
    # Get the size of the progress bar
    width = bounding_box[2] - bounding_box[0]
    height = bounding_box[3] - bounding_box[1]
    size = (width, height)

    # Create a mask
    mask = Image.new("L", size, 1)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(((0, 0), size), 16, 255, 0, 3)

    # Create an image for the inside of the bar
    bar_inside = Image.new("RGB", size, WHITE)
    draw_progress_bar_inside(bar_inside, width, height, percentage)
    # Crop the image using the mask
    inside_masked = ImageOps.fit(bar_inside, mask.size, centering=(0.5, 0.5))
    inside_masked.putalpha(mask)

    # Draw the rectangle
    draw.rounded_rectangle(bounding_box, 16, WHITE, ORANGE, 3)

    # Draw the progress bar
    dest.paste(inside_masked, bounding_box[:2], inside_masked)


def abbreviate_integer(value: int) -> str:
    """
    Returns an abbreviated version of the given integer: `100` -> `100`, `1500` -> `1.5K`.
    """
    if value >= 1000:
        return f"{(value // 100) / 10}K"
    else:
        return str(value)


def make_banner(user: discord.User) -> str:
    """
    Generates a banner for the given user.
    Returns the filename of the generated banner.
    """
    img = Image.open("assets/fetch_points_base.png")
    img.load()

    draw = ImageDraw.Draw(img)

    draw_user_avatar(user, img, 120, (30, 20))

    # Write the user's name
    name_length = len(user.name)
    if name_length <= 12:
        font_username_size = 38
        name_text_y = 36
    else:
        font_username_size = round(38 * 12 / name_length)
        name_text_y = 36 + (name_length - 12) // 2
    font_username = ImageFont.truetype(FONT_PATH, font_username_size)
    draw.text((175, name_text_y), user.name, BLACK, font=font_username)

    # Get user data
    user_data = get_user_data(user.id)

    # Draw the progress bar
    next_level_percentage = get_next_level_percentage(user_data)
    draw_progress_bar(draw, img, (175, 95, 425, 130), next_level_percentage)

    # Write statistics
    points = fetch_points(user_data.dmoj_username)
    text_shadow(draw, (490, 25), f"CCC Points: {points:,}", font_side)
    text_shadow(draw, (490, 65), f"Level: {user_data.level:,}", font_side)
    text_shadow(draw, (490, 105), f"XP: {user_data.experience:,}", font_side)
    text_shadow(draw, (490, 145), f"Messages: {user_data.messages:,}", font_side)

    # Write experience under the progress bar
    experience_str = abbreviate_integer(user_data.experience)
    next_level = get_next_level_experience(user_data.level)
    next_level_str = abbreviate_integer(next_level)
    draw.text((185, 150), f"XP: {experience_str} / {next_level_str}", BLACK, font_experience)

    img.save("assets/temp_banner.png")
    return "assets/temp_banner.png"
