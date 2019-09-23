import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# process and format all info into an image
def process(name, song, album, artist, current, total, user, cover):
    print(f'{name} is listening to {song} by {artist} on {album}.')

    #input
    user = Image.open(BytesIO(user.content))
    cover = Image.open(BytesIO(cover.content))
    stotal = str(datetime.timedelta(milliseconds=total))
    stotal = stotal[3:7] if stotal[2] == '0' else stotal[2:7]
    scurrent = str(datetime.timedelta(milliseconds=current))
    scurrent = scurrent[3:7] if scurrent[2] == '0' else scurrent[2:7]

    #background
    image = Image.new('RGB', (600, 300), (30, 215 , 96))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 118) + image.size, (30, 180 , 96))

    #images
    user.thumbnail((80, 80), Image.ANTIALIAS)
    image.paste(user, (52, 20))
    cover.thumbnail((128, 128), Image.ANTIALIAS)
    image.paste(cover, (28, 146))

    #fonts
    namefont = ImageFont.truetype('Fonts\\Montserrat-SemiBold.ttf',32)
    if not song == str(song.encode('utf-8'))[2:-1]:
        songfont = ImageFont.truetype('Fonts\\arial-unicode-ms.ttf',29)
    else:
        songfont = ImageFont.truetype('Fonts\\Montserrat-SemiBold.ttf',29)
    if not album == str(album.encode('utf-8'))[2:-1] or not artist == str(artist.encode('utf-8'))[2:-1]:
        infofont = ImageFont.truetype('Fonts\\arial-unicode-ms.ttf',26)
    else:
        infofont = ImageFont.truetype('Fonts\\OpenSansCondensed-Bold.ttf',26)
    timefont = ImageFont.truetype('Fonts\\Roboto-Medium.ttf',17)

    #texts
    draw.text((184, 21 ), name+'\nis now listening to', fill=(227,255,238), font=namefont)
    draw.text((184, 138), truncate(song, songfont, 380), fill=(233,255,244), font=songfont)
    draw.text((184, 174), 'by '+truncate(artist, infofont, 348), fill=(186,253,209), font=infofont)
    draw.text((184, 207), 'on '+truncate(album, infofont, 348), fill=(186,253,209), font=infofont)

    #progress
    draw.rectangle((568, 251) + (185, 254), (70,190,120))
    draw.rectangle((185+(current/total*383), 251) + (185, 254), (180,240,200))
    draw.text((185, 258), str(scurrent), fill=(186,253,209), font=timefont)
    draw.text((534, 258), str(stotal), fill=(186,253,209), font=timefont)

    #output
    now = BytesIO()
    image.save(now, 'JPEG', quality=200)
    now.seek(0)
    return(now)

# shorten extra long text
def truncate(text, font, limit):
    edited = True if font.getsize(text)[0] > limit else False
    while font.getsize(text)[0] > limit: text = text[:-1]
    if edited: return(text.strip()+'..')
    else: return(text.strip())
