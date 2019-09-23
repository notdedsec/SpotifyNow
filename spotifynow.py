import sql, processor
import os, sys, json, sqlite3, logging, requests
from urllib.parse import quote_plus as linkparse
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, run_async
from telegram import Bot, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatAction

# add new user
def link(bot, update):
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        update.effective_message.reply_text("Contact me in private chat to link your Spotify account.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Link",url="t.me/spotifynowbot")]]))
        return ConversationHandler.END
    message = "I'm gonna need some details to link your Spotify account. Don't worry, I'll guide you through the process.\n\nFirst, tell me your Spotify account's username. You can check it in your [Spotify Account Overview](https://www.spotify.com/us/account/overview/) page. Send it to me once you have it."
    update.effective_message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    return USERNAME

# save username and id
def getusername(bot, update):
    username = update.effective_message.text.strip()
    sql.add_user(update.effective_user.id, username)
    link = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={linkparse(redirect_uri)}&scope=user-read-currently-playing"
    message = "Next is Authourization. I need some permissions to check what you're listening to. Tap the button below to authourize. Once done, copy the link from the adress bar and send it to me."
    update.effective_message.reply_text(message, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Authourize", url=link)]]))
    return AUTHTOKEN

# add/update token
def getauthtoken(bot, update):
    code = update.effective_message.text.replace(f'{redirect_uri}?code=', '')
    data = {'grant_type':'authorization_code','code':code,'redirect_uri':redirect_uri,'client_id':client_id,'client_secret':client_secret}
    try: authtoken = requests.post('https://accounts.spotify.com/api/token', data=data).json()['refresh_token']
    except: update.message.reply_text('Something went wrong. Try to /relink your Spotify account. Make sure you send the full link.')
    else:
        sql.add_token(authtoken, update.effective_user.id)
        print(update.message.from_user.username+' just linked his account.')
        message = "Yay! Your Spotify account is now linked. Tap /now anytime to display what you're currently listening to. You can use /unlink to remove your account any time you want."
        update.message.reply_text(message)
    return ConversationHandler.END

# update stored token
def relink(bot, update):
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        update.effective_message.reply_text("Contact me in private chat to link your Spotify account.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Link",url=redirect_uri)]]))
        return ConversationHandler.END
    if not sql.get_user(update.effective_user.id): return ConversationHandler.END
    link = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={linkparse(redirect_uri)}&scope=user-read-currently-playing"
    message = "Tap the button below to authourize. Once done, copy the link from the adress bar and send it to me."
    update.effective_message.reply_text(message, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Authourize", url=link)]]))
    return AUTHTOKEN

# remove user from db
def unlink(bot, update):
    sql.del_user(update.effective_user.id)
    print(update.message.from_user.username+' just unlinked their account.')
    message = "You've been unlinked from my database. You can disable the authourization from your [Account's Apps Overview](https://www.spotify.com/us/account/apps/) section."
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# cancel message
def cancel(bot, update):
    update.message.reply_text('Canceled.')

# send start message
def start(bot, update):
    update.message.reply_text('Hi.\nI\'m SpotifyNow and I can help you share what music you\'re listening to on Spotify. Tap /now to get started.')

# send help message
def help(bot, update):
    update.message.reply_text(helptext)

# main
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
        if response['currently_playing_type'] == 'ad': update.message.reply_text('Ads. You\'re listening those annoying ads.')
        elif response['currently_playing_type'] == 'track':
            bot.send_photo( # process info and send output
                update.message.chat_id,
                processor.process(
                    name = update.message.from_user.username,
                    song = response['item']['name'],
                    album = response['item']['album']['name'],
                    artist = ', '.join([x['name'] for x in response['item']['album']['artists']]),
                    total = response['item']['duration_ms'],
                    current = response['progress_ms'],
                    cover = requests.get(response['item']['album']['images'][1]['url']),
                    user = requests.get(bot.getFile(bot.getUserProfilePhotos(userid, limit=1)['photos'][0][0]['file_id']).file_path)),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Play on Spotify", url=response['item']['external_urls']['spotify'])]]))
        else: update.message.reply_text('I\'m not sure what you\'re listening to.')
    except: update.message.reply_text('You\'re not listening to anything on Spotify at the moment.')

# restart from telegram
def restart(bot, update):
    if update.message.from_user.id in sudoList: 
        print('\n---------\nRESTARTED\n---------')
        update.effective_message.reply_text("Restarted.")
        os.execv('launch.bat', sys.argv)
    else: update.effective_message.reply_text("This is a developer restricted command.\nYou don't have permissions to access this.")

# pull latest commit
def gitpull(bot, update):
    if update.message.from_user.id in sudoList:
        print('\n---------\nGITPULLED\n---------')
        update.effective_message.reply_text("Pulling the latest commit from GitHub.")
        os.system('git pull')
        os.execv('launch.bat', sys.argv)
    else: update.effective_message.reply_text("This is a developer restricted command.\nYou don't have permissions to access this.")

helptext = '''Using me is very simple. Just tap /now to share what you\'re listening to on Spotify.\n
If you\'re new, you need to /link your account to get started.\n
If you\'re facing any errors, /relink might help. If the issue persists, report it to @notdedsec.\n
You can always /unlink your account whenever you feel like. Though why would you wanna do that?'''

if __name__ == "__main__": 
    # initialize database and variables
    if not os.path.exists('spotifynow.db'): sql.create_table()
    with open('config.json','r') as conf: config = json.load(conf)
    client_id, client_secret, redirect_uri, bot_token, sudoList = config.values()
    # initialize the bot
    updater = Updater(bot_token)
    os.system("title " + Bot(bot_token).first_name)
    logging.basicConfig(format='\n\n%(levelname)s\n%(asctime)s\n%(name)s\n%(message)s', level=logging.ERROR)
    USERNAME, AUTHTOKEN = range(2)
    link_handler = ConversationHandler(
        entry_points=[CommandHandler('link', link)],
        states={USERNAME: [MessageHandler(Filters.text, getusername)], AUTHTOKEN: [MessageHandler(Filters.text, getauthtoken)]},
        fallbacks=[CommandHandler('cancel', cancel)])
    relink_handler = ConversationHandler(
        entry_points=[CommandHandler('relink', relink)],
        states={AUTHTOKEN: [MessageHandler(Filters.text, getauthtoken)]}, 
        fallbacks=[CommandHandler('cancel', cancel)])
    updater.dispatcher.add_handler(link_handler)
    updater.dispatcher.add_handler(relink_handler)
    updater.dispatcher.add_handler(CommandHandler('now', nowplaying))
    updater.dispatcher.add_handler(CommandHandler('unlink', unlink))
    updater.dispatcher.add_handler(CommandHandler('restart', restart))
    updater.dispatcher.add_handler(CommandHandler('gitpull', gitpull))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.start_polling()
    updater.idle()