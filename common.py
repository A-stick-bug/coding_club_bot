from PIL import ImageDraw, ImageOps, Image
import requests
from io import BytesIO

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (10, 143, 60)
BLUE = (20, 69, 181)
ORANGE = (240, 149, 22)
YELLOW = (255, 200, 0)

FONT_PATH = "assets/consola.ttf"


def request_image(url: str):
    """
    Fetches an image from the given URL.
    """
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image


def crop_circle(src, dest, position: tuple[int, int]) -> None:
    """
    Crops the source image into a circle and draws it onto the destination image.
    """
    # Create a circular mask
    mask = Image.new("L", src.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.pieslice(((0, 0), (mask.size)), 0, 360, fill=255)
    # Crop the source image using the mask
    output = ImageOps.fit(src, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    # Draw it to the destination image
    dest.paste(output, position, output)


def draw_user_avatar(user, dest_image, size: int, position: tuple[int, int]) -> None:
    """
    Draws the avatar of the given user onto the destination image at the given position.
    """
    avatar_image = request_image(user.display_avatar.url)
    avatar_image = avatar_image.resize((size, size))
    crop_circle(avatar_image, dest_image, position)


def text_shadow(draw, position: tuple[int, int], text: str, font, fore=WHITE, back=BLACK, offset=3,
                anchor="la") -> None:
    """
    Draws text with a shadow.
    """
    draw.text((position[0] + offset, position[1] + offset), text, back, font=font, anchor=anchor)
    draw.text(position, text, fore, font=font, anchor=anchor)
