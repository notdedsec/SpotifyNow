from PIL import Image, ImageDraw

from app.imager.styles.base import Style
from app.models import Stats, Track, User

# track has album art url which needs to be requested and streamed
# where will user pic url come from? or any way to stream it from tg?
# add properties for fonts along with style?


class Classic(Style):

    def now(self, track: Track, user: User):
        font_name = self.load_font('Montserrat', 32)
        font_song = self.load_font('Montserrat', 29, track.name) or self.load_font('Arial', 29)
        font_info = self.load_font('OpenSansCondensed', 26, track.name) or self.load_font('Arial', 26)
        font_time = self.load_font('Roboto', 17)

        frame = self.create_frame()
        image = ImageDraw.Draw(frame)
        image.rectangle((0, 118) + self.size, (30, 180, 96))

        avatar = self.load_image(user.avatar, resize=(80, 80))
        frame.paste(avatar, (52, 20))

        artwork = self.load_image(track.artwork, resize=(128, 128))
        frame.paste(artwork, (28, 146))

        image.text((184, 21), f'{user.name}\nis now listening to', fill=(227, 255, 238), font=font_name)
        image.text((184, 138), f'{self.truncate(track.name, font_song, 380)}', fill=(233, 255, 244), font=font_song)
        image.text((184, 174), f'by {self.truncate(track.artist, font_info, 348)}', fill=(186, 253, 209), font=font_info)
        image.text((184, 207), f'on {self.truncate(track.album, font_info, 348)}', fill=(186, 253, 209), font=font_info)

        image.rectangle((185, 251, 568, 254), (70, 190, 120))
        image.rectangle((185, 251, 185 + int(track.position / track.duration * 383), 254), (180, 240, 200))
        image.text((185, 258), self.get_timestamp(track.position), fill=(186, 253, 209), font=font_time)
        image.text((524, 258), self.get_timestamp(track.duration), fill=(186, 253, 209), font=font_time)

        return self.finalize_frame(frame)


    def top(self, stats: Stats, user: User):
        ...

