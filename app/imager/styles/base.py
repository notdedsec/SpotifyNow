from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import Optional, Union, Tuple, overload

import requests
from colour import Color
from fontTools.ttLib import TTFont
from PIL import Image, ImageColor, ImageDraw, ImageFont

from app.models import Stats, Track, User


class Style:

    def __init__(self, color: str, accent: str):
        self.color = ImageColor.getcolor(color, 'RGBA')
        self.accent = ImageColor.getcolor(accent, 'RGBA')

        self.size = (600, 300)

        self.font_dir = Path('app/imager/fonts')
        self.font_luma = Color(color).get_luminance()
        self.font_color = ImageColor.getcolor('white' if self.font_luma < 0.5 else 'black', 'RGBA')


    def create_frame(self, size: Optional[Tuple[int, int]] = None, color: Optional[Tuple] = None) -> Image.Image:
        size = size or self.size
        color = color or self.color
        image = Image.new('RGBA', size, color) # type: ignore
        return image


    # how do i load telegram pfp?
    # what about default pfp? 'https://i.imgur.com/dzddC5q.jpeg'
    def load_image(self, image_url: str, resize: Optional[Tuple[int, int]] = None) -> Image.Image:
        response = requests.get(image_url)
        if not response.ok:
            raise ValueError('Failed to load image from URL')
        image = Image.open(BytesIO(response.content))
        if resize:
            image.thumbnail(resize) # Image.ANTIALIAS
        return image


    @overload
    def load_font(self, font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
        ...

    @overload
    def load_font(self, font_name: str, font_size: int, text: str) -> Optional[ImageFont.FreeTypeFont]:
        ...

    def load_font(self, font_name: str, font_size: int, text: Optional[str] = None) -> Optional[ImageFont.FreeTypeFont]:
        font_file = self.font_dir.glob(f'*{font_name.strip("*")}*')
        font_path = next(font_file, None)
        if not font_path:
            return

        font_temp = TTFont(str(font_path))
        supported = set(font_temp.getBestCmap())
        if text and not all(ord(char) in supported for char in text):
            return

        font = ImageFont.truetype(font=str(font_path), size=font_size)
        return font


    def truncate(self, text: str, font: ImageFont.FreeTypeFont, limit: int) -> str:
        truncated = font.getlength(text) > limit
        while font.getlength(text) > limit:
            text = text[:-1]
        return f'{text.strip()}..' if truncated else text


    def get_timestamp(self, time_ms: int) -> str:
        delta = timedelta(milliseconds=time_ms)
        timestamp = delta.__str__()[2:7].lstrip('0')
        return timestamp


    def finalize_frame(self, image: Image.Image) -> BytesIO:
        now = BytesIO()
        image.save(now, 'JPEG', quality=200)
        now.seek(0)
        return now


    def now(self, track: Track, user: User) -> Image.Image:
        ...


    def top(self, stats: Stats, user: User) -> Image.Image:
        ...
