import sql, processor
from uuid import uuid4
import os, sys, json, sqlite3, logging, requests
from urllib.parse import quote_plus as linkparse
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, InlineQueryHandler, Filters, run_async
from telegram import Bot, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ChatAction, InlineQueryResultCachedPhoto

def link(update, context):
    'add new user'
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        button = InlineKeyboardMarkup([[InlineKeyboardButton(text="Link",url="t.me/spotifynowbot")]])
        update.effective_message.reply_text("Contact me in private chat to link your Spotify account.", reply_markup=button)
        return ConversationHandler.END
    message = "I'm gonna need some information for linking your Spotify account. Tell me, what should I call you?"
    update.effective_message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    return USERNAME

def getusername(update, context):
    'save username and id'
    username = update.effective_message.text.strip()
    sql.add_user(update.effective_user.id, username)
    message = "Next up is Authorization. I need permissions to see what you're listening to."
    button = InlineKeyboardMarkup([[InlineKeyboardButton(text="Authorize", url=authlink)]])
    update.effective_message.reply_text(message, reply_markup=button)
    return ConversationHandler.END

def relink(update, context):
    'update stored token'
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        button = InlineKeyboardMarkup([[InlineKeyboardButton(text="Link",url="t.me/spotifynowbot")]])
        update.effective_message.reply_text("Contact me in private chat to link your Spotify account.", reply_markup=button)
        return
    if not sql.get_user(update.effective_user.id): 
        update.effective_message.reply_text("You need to /link before using this function.")
        return
    message = "Tap the button below to authorize."
    button = InlineKeyboardMarkup([[InlineKeyboardButton(text="Authorize", url=authlink)]])
    update.effective_message.reply_text(message, reply_markup=button)
    return

def unlink(update, context):
    'remove user from db'
    sql.del_user(update.effective_user.id)
    print(update.message.from_user.username+' just unlinked their account.')
    message = "You've been unlinked from my database. You can disable the authorization from your [Account's Apps Overview](https://www.spotify.com/us/account/apps/) section."
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def code(text):
    'get authtoken from a temporary json given by the webserver'
    tempjson = requests.get('https://jsonblob.com/api/'+jkey).json()
    code = tempjson[text[7:]]
    keycount = len(tempjson.keys())
    if keycount > 10:
        for x in range(0, 5):
            tempjson.pop(list(tempjson.keys())[x])
    requests.put('https://jsonblob.com/api/'+jkey, json=tempjson)
    return(code)

def start(update, context):
    'handle start command with deep linking'
    text = update.effective_message.text
    if len(text) <= 7:
        update.message.reply_text("Hi! I'm SpotifyNow and I you flex what you're listening to on Spotify. Tap /now to get started.")
    elif text.endswith('link'):
        update.message.reply_text("Hi! I'm SpotifyNow and I you flex what you're listening to on Spotify. Tap /link to connect your account.")
    elif text.endswith('relink'):
        update.message.reply_text("Spotify isn't letting me see what you're listening to! Try to /relink your Spotify account.")
    elif text.endswith('notsure'):
        update.message.reply_text("I'm not sure what you're listening to.")
    elif text.endswith('ads'):
        update.message.reply_text("Ads. You're listening to those annoying ads!")
    elif text.endswith('notlistening'):
        update.message.reply_text("You're not listening to anything on Spotify at the moment.")
    else:
        try: 
            data = {'grant_type':'authorization_code','code':code(text),'redirect_uri':redirect_uri,'client_id':client_id,'client_secret':client_secret}
            authtoken = requests.post('https://accounts.spotify.com/api/token', data=data).json()['refresh_token']
        except: 
            update.message.reply_text(f'Something went wrong. Try to /relink your account.')
        else:
            sql.add_token(authtoken, update.effective_user.id)
            print(update.message.from_user.username+' just linked their account.')
            message = "Yay! Your Spotify account is now linked. Tap /now anytime to flex what you're listening to. You can also use the inline mode by typing @SpotifyNowBot in any chat."
            update.message.reply_text(message)
    update.effective_message.delete()

def getpic(r, uid, context):
    'retrives and passes all arguments to the image processor'
    username  = list(sql.get_user(uid)[0])[1]
    songname  = r['item']['name']
    albumname = r['item']['album']['name']
    totaltime = r['item']['duration_ms']
    crrnttime = r['progress_ms']
    coverart  = requests.get(r['item']['album']['images'][1]['url'])
    artists   = ', '.join([x['name'] for x in r['item']['artists']])
    try:
        pfp  = context.bot.getUserProfilePhotos(uid, limit=1)['photos'][0][0]['file_id']
        user = requests.get(context.bot.getFile(pfp).file_path)
    except:
        user = requests.get('https://files.catbox.moe/jp6szj.jpg')
    return(processor.process(username, songname, albumname, artists, crrnttime, totaltime, user, coverart))

@run_async
def nowplaying(update, context):
    'collects user info, requests spotify api for song info and sends the processed image'
    context.bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    try: 
        uid = update.message.from_user.id
        authtoken = list(sql.get_user(uid)[0])[2]
    except: 
        update.message.reply_text('You need to /link your Spotify account with me first.')
        return
    try: 
        data = {
            'grant_type': 'refresh_token', 
            'refresh_token': authtoken, 
            'redirect_uri': redirect_uri, 
            'client_id': client_id, 
            'client_secret': client_secret
        }
        token = requests.post('https://accounts.spotify.com/api/token', data=data).json()
    except:
        update.message.reply_text('Something went wrong. Try to /relink your account.')
        return
    try: 
        headers = {
            'Accept': 'application/json', 
            'Content-Type': 'application/json', 
            'Authorization': 'Bearer '+token['access_token']
        }
        r = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers).json()
        if   r['currently_playing_type'] == 'ad': 
            update.message.reply_text("Ads. You're listening to those annoying ads.")
        elif r['currently_playing_type'] == 'track':
            button = InlineKeyboardButton(text="Play on Spotify", url=r['item']['external_urls']['spotify'])
            context.bot.send_photo(update.message.chat_id, getpic(r, uid, context), reply_markup=InlineKeyboardMarkup([[button]]))
        else: 
            update.message.reply_text("I'm not sure what you're listening to.")
    except Exception as e: 
        print(e)
        update.message.reply_text("You're not listening to anything on Spotify at the moment.")

def sstats(update, context):
    'returns the number of registered users, devs only'
    if update.message.from_user.id in sudoList:
        userlist = sql.list_users()
        update.message.reply_text(f'{len(userlist)} Users')
    else: 
        update.effective_message.reply_text("This is a developer restricted command.\nYou don't have permissions to access this.")

def cancel(update, context):
    update.message.reply_text('Canceled.')
    return ConversationHandler.END

def sendhelp(update, context):
    update.message.reply_text(helptext)

def inlinenow(update, context):
    'inline implementation of notplaying() function along with exception handeling for new users'
    try: 
        uid = update.inline_query.from_user.id
        authtoken = list(sql.get_user(uid)[0])[2]
    except: 
        update.inline_query.answer(
            results=[], 
            switch_pm_text='Connect your Spotify account.',
            switch_pm_parameter='link', 
            cache_time=0
        )
        return
    try: 
        data = {
            'grant_type':'refresh_token',
            'refresh_token':authtoken,
            'redirect_uri':redirect_uri,
            'client_id':client_id,
            'client_secret':client_secret
        }
        token = requests.post('https://accounts.spotify.com/api/token', data=data).json()
    except:
        update.inline_query.answer(
            results=[], 
            switch_pm_text="Something's wrong. Lets fix it.", 
            switch_pm_parameter='relink', 
            cache_time=0
        )
        return
    try: 
        headers = {
            'Accept':'application/json', 
            'Content-Type':'application/json', 
            'Authorization':'Bearer '+token['access_token']
        }
        r = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers).json()
        if   r['currently_playing_type'] == 'ad': 
            update.inline_query.answer([], switch_pm_text="You're listening to annoying ads.", switch_pm_parameter='ads', cache_time=0)
        elif r['currently_playing_type'] == 'track':
            button = InlineKeyboardButton(text="Play on Spotify", url=r['item']['external_urls']['spotify'])
            image   = getpic(r, uid, context)
            dump    = context.bot.send_photo(dumpchannel, photo=image)
            photo   = dump['photo'][1]['file_id']
            dump.delete()
            update.inline_query.answer(
                [
                    InlineQueryResultCachedPhoto(
                        id=uuid4(),
                        photo_file_id=photo,
                        reply_markup=InlineKeyboardMarkup([[button]])
                    )
                ], cache_time=0
            )
        else: 
            update.inline_query.answer([], switch_pm_text="Not sure what you're listening to.", switch_pm_parameter='notsure', cache_time=0)
    except Exception as e: 
        print(e)
        update.inline_query.answer([], switch_pm_text="You're not listening to anything.", switch_pm_parameter='notlistening', cache_time=0)

helptext = '''
Tap /now to share what you're listening to on Spotify. You can also use the inline mode by typing @SpotifyNowBot in any chat.\n
If you're new, you need to /link your account to get started. You can always /unlink it whenever you feel like.\n
If you're facing errors, try restarting Spotify. No good? Send /cancel followed by /relink and if the issue persists, report it to @notdedsec.\n'''

if __name__ == "__main__": 
    if not os.path.exists('spotifynow.db'): 
        sql.create_table()
    with open('config.json','r') as conf: 
        config = json.load(conf)
    dumpchannel, jkey, client_id, client_secret, redirect_uri, bot_token, sudoList = config.values()
    authlink = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={linkparse(redirect_uri)}&scope=user-read-currently-playing"

    updater = Updater(bot_token, use_context=True)
    os.system("title " + Bot(bot_token).first_name)
    logging.basicConfig(format='\n\n%(levelname)s\n%(asctime)s\n%(name)s\n%(message)s', level=logging.ERROR)

    USERNAME, AUTHTOKEN = range(2)
    link_handler = ConversationHandler(
        entry_points=[CommandHandler('link', link)],
        states={USERNAME: [MessageHandler(Filters.text, getusername)]},
        fallbacks=[CommandHandler('cancel', cancel)])

    updater.dispatcher.add_handler(link_handler)
    updater.dispatcher.add_handler(InlineQueryHandler(inlinenow))
    updater.dispatcher.add_handler(CommandHandler('now', nowplaying))
    updater.dispatcher.add_handler(CommandHandler('help', sendhelp))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('unlink', unlink))
    updater.dispatcher.add_handler(CommandHandler('relink', relink))
    updater.dispatcher.add_handler(CommandHandler('sstats', sstats))
    updater.start_polling()
    updater.idle()
