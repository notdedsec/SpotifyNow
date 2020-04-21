import sql, processor
from uuid import uuid4
import os, sys, json, sqlite3, logging, requests
from urllib.parse import quote_plus as linkparse
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, InlineQueryHandler, Filters, run_async
from telegram import Bot, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ChatAction, InlineQueryResultCachedPhoto

# add new user
def link(bot, update):
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        update.effective_message.reply_text("Contact me in private chat to link your Spotify account.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Link",url="t.me/spotifynowbot")]]))
        return ConversationHandler.END
    message = "I'm gonna need some information for linking your Spotify account. Tell me, what should I call you?"
    update.effective_message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    return USERNAME

# save username and id
def getusername(bot, update):
    username = update.effective_message.text.strip()
    sql.add_user(update.effective_user.id, username)
    link = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={linkparse(redirect_uri)}&scope=user-read-currently-playing"
    message = "Next is Authourization. I need permissions to see what you're listening to."
    update.effective_message.reply_text(message, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Authourize", url=link)]]))
    return ConversationHandler.END

# update stored token
def relink(bot, update):
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        update.effective_message.reply_text("Contact me in private chat to link your Spotify account.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Link",url=redirect_uri)]]))
        return
    if not sql.get_user(update.effective_user.id): 
        update.effective_message.reply_text("You need to /link before you using this function.")
        return
    message = "Tap the button below to authourize."
    link = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={linkparse(redirect_uri)}&scope=user-read-currently-playing"
    update.effective_message.reply_text(message, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Authourize", url=link)]]))
    return

# remove user from db
def unlink(bot, update):
    sql.del_user(update.effective_user.id)
    print(update.message.from_user.username+' just unlinked their account.')
    message = "You've been unlinked from my database. You can disable the authourization from your [Account's Apps Overview](https://www.spotify.com/us/account/apps/) section."
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def code(text):
    tempjson = requests.get('https://jsonblob.com/api/'+jkey).json()
    code = tempjson[text[7:]]
    keycount = len(tempjson.keys())
    if keycount > 10:
        for x in range(0, 5):
            tempjson.pop(list(tempjson.keys())[x])
    requests.put('https://jsonblob.com/api/'+jkey, json=tempjson)
    return(code)

def start(bot, update):
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
            update.message.reply_text(f'Something went wrong. Try to /relink your Spotify account.')
        else:
            sql.add_token(authtoken, update.effective_user.id)
            print(update.message.from_user.username+' just linked their account.')
            message = "Yay! Your Spotify account is now linked. Tap /now anytime to flex what you're listening to."
            update.message.reply_text(message)
    update.effective_message.delete()

@run_async
def nowplaying(bot, update):
    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    try: # get user info from db
        userid = str(update.message.from_user.id)
        authtoken = list(sql.get_user(update.message.from_user.id)[0])[2]
    except: 
        update.message.reply_text('You need to /link your Spotify account with me first.')
        return
    try: # get access token from api
        data = {'grant_type': 'refresh_token', 'refresh_token': authtoken, 'redirect_uri': redirect_uri, 'client_id': client_id, 'client_secret': client_secret}
        token = requests.post('https://accounts.spotify.com/api/token', data=data).json()
    except:
        update.message.reply_text('Something went wrong. Try to /relink your Spotify account.')
        return
    try: # get current track info
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {token["access_token"]}'}
        response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers).json()
        if response['currently_playing_type'] == 'ad': 
            update.message.reply_text("Ads. You're listening to those annoying ads.")
        elif response['currently_playing_type'] == 'track':
            bot.send_photo( # process info and send output
                update.message.chat_id,
                processor.process(
                    name = list(sql.get_user(update.message.from_user.id)[0])[1],
                    song = response['item']['name'],
                    album = response['item']['album']['name'],
                    artist = ', '.join([x['name'] for x in response['item']['artists']]),
                    total = response['item']['duration_ms'],
                    current = response['progress_ms'],
                    cover = requests.get(response['item']['album']['images'][1]['url']),
                    user = requests.get(bot.getFile(bot.getUserProfilePhotos(userid, limit=1)['photos'][0][0]['file_id']).file_path)),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Play on Spotify", url=response['item']['external_urls']['spotify'])]]))
        else: 
            update.message.reply_text("I'm not sure what you're listening to.")
    except: 
        update.message.reply_text("You're not listening to anything on Spotify at the moment.")

def restart(bot, update):
    if update.message.from_user.id in sudoList: 
        print('\n---------\nRESTARTED\n---------')
        update.effective_message.reply_text("Restarted.")
        os.execv('launch.bat', sys.argv)
    else: 
        update.effective_message.reply_text(restricted)

def gitpull(bot, update):
    if update.message.from_user.id in sudoList:
        print('\n---------\nGITPULLED\n---------')
        update.effective_message.reply_text("Pulling the latest commit from GitHub.")
        os.system('git pull')
        os.execv('launch.bat', sys.argv)
    else: 
        update.effective_message.reply_text(restricted)

def sstats(bot, update):
    if update.message.from_user.id in sudoList:
        update.message.reply_text(str(len(sql.list_users()))+' Users')
    else: 
        update.effective_message.reply_text(restricted)

def cancel(bot, update):
    update.message.reply_text('Canceled.')
    return ConversationHandler.END

def help(bot, update):
    update.message.reply_text(helptext)

def inlinenow(bot, update):
    try: # get user info from db
        userid = str(update.inline_query.from_user.id)
        authtoken = list(sql.get_user(update.inline_query.from_user.id)[0])[2]
    except: 
        update.inline_query.answer([], switch_pm_text='Connect your Spotify account.', switch_pm_parameter='link', cache_time=0)
        return
    try: # get access token from api
        data = {'grant_type':'refresh_token','refresh_token':authtoken,'redirect_uri':redirect_uri,'client_id':client_id,'client_secret':client_secret}
        token = requests.post('https://accounts.spotify.com/api/token', data=data).json()
    except:
        update.inline_query.answer([], switch_pm_text="Something's wrong. Lets fix it.", switch_pm_parameter='relink', cache_time=0)
        return
    try: # get current track info
        headers = {'Accept':'application/json', 'Content-Type':'application/json', 'Authorization':f'Bearer {token["access_token"]}'}
        response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers).json()
        if response['currently_playing_type'] == 'ad': 
            update.inline_query.answer([], switch_pm_text="You're listening to annoying ads.", switch_pm_parameter='ads', cache_time=0)
        elif response['currently_playing_type'] == 'track':
            name = list(sql.get_user(update.inline_query.from_user.id)[0])[1]
            song = response['item']['name']
            album = response['item']['album']['name']
            artist = ', '.join([x['name'] for x in response['item']['artists']])
            current = response['progress_ms']
            total = response['item']['duration_ms']
            cover = requests.get(response['item']['album']['images'][1]['url'])
            user = requests.get(bot.getFile(bot.getUserProfilePhotos(userid, limit=1)['photos'][0][0]['file_id']).file_path)
            link = response['item']['external_urls']['spotify']
            image = processor.process(name, song, album, artist, current, total, user, cover)
            dump = bot.send_photo(dumpchannel, photo=image)
            photo = dump['photo'][1]['file_id']
            dump.delete()
            update.inline_query.answer(
                [
                    InlineQueryResultCachedPhoto(
                        id=uuid4(),
                        photo_file_id=photo,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Play on Spotify", url=link)]])
                    )
                ], cache_time=0
            )
        else: 
            update.inline_query.answer([], switch_pm_text="Not sure what you're listening to.", switch_pm_parameter='notsure', cache_time=0)
    except: 
        update.inline_query.answer([], switch_pm_text="You're not listening to anything.", switch_pm_parameter='notlistening', cache_time=0)

helptext = '''Using me is very simple. Just tap /now to share what you\'re listening to on Spotify.\n
If you\'re new, you need to /link your account to get started.\n
If you\'re facing any errors, try /cancel followed by /relink. If the issue persists, report it to @notdedsec.\n
You can always /unlink your account whenever you feel like. Though why would you wanna do that?'''
restricted = "This is a developer restricted command.\nYou don't have permissions to access this."

if __name__ == "__main__": 
    if not os.path.exists('spotifynow.db'): sql.create_table()
    with open('config.json','r') as conf: config = json.load(conf)
    dumpchannel, jkey, client_id, client_secret, redirect_uri, bot_token, sudoList = config.values()
    updater = Updater(bot_token)
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
    updater.dispatcher.add_handler(CommandHandler('unlink', unlink))
    updater.dispatcher.add_handler(CommandHandler('relink', relink))
    updater.dispatcher.add_handler(CommandHandler('restart', restart))
    updater.dispatcher.add_handler(CommandHandler('gitpull', gitpull))
    updater.dispatcher.add_handler(CommandHandler('sstats', sstats))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.start_polling()
    updater.idle()
