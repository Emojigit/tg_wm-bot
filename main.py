# -*- coding: utf-8 -*-
import sys, re, logging, requests, json, emoji, traceback
exit = sys.exit
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackContext
from telegram.ext.filters import Filters
from telegram.error import InvalidToken
from telegram import ParseMode, Update
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s[%(name)s] %(message)s")
log = logging.getLogger("MainScript")
chan = ""

try:
    with open("chan.txt","r") as f:
        chan = f.read().rstrip('\n')
except FileNotFoundError:
    log.error("No chan.txt!")
    exit(1)

def token():
    try:
        with open("token.txt","r") as f:
            return f.read().rstrip('\n')
    except FileNotFoundError:
        log.error("No token.txt!")
        exit(3)

def GetCMDCallBack(cname,rcont):
    def CMDCB(update: Update, context: CallbackContext):
        log.info("Got {} command!".format(cname))
        update.message.reply_text(rcont)
    return CMDCB

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def contain_emoji(s):
    return bool(emoji.get_emoji_regexp().search(s))

def invalid(s):
    ILST = ["￣"]
    for x in ILST:
        if x in s:
            return True
    return False

def main():
    log.info("Getting wm-bot info")
    URL = "https://wm-bot.wmflabs.org/dump/%23{}_dump.js".format(chan)
    log.info("URl: {}".format(URL))
    RGR = requests.get(URL)
    if RGR.status_code != 200:
        log.error("HTTP Error {}".format(str(RGR.status_code)))
        exit(4)
    RGR.encoding = "unicode"
    # print(RGR.text.splitlines()[0].rstrip('\n'))
    CLST = json.loads(RGR.text.splitlines()[0].rstrip('\n'))
    tok = token()
    try:
        updater = Updater(tok, use_context=True)
        log.info("Get updater success!")
    except InvalidToken:
        log.critical("Invalid Token! Plase edit token.txt and fill in a valid token.")
        raise
    dp = updater.dispatcher
    FCL = []
    for x in CLST:
        key = x["Key"]
        txt = x["Text"]
        log.info("Registering {} command with '{}'".format(key,txt))
        try:
            dp.add_handler(CommandHandler(key, GetCMDCallBack(key,txt)))
        except ValueError as error:
            log.error("Not register {} because error".format(key))
            log.exception(error)
            continue
        FCL.insert(-1,key)
    log.info("Finally i registered these commands: {}".format(str(FCL)))
    updater.start_polling()
    log.info("Started the bot! Use Ctrl-C to stop it.")
    updater.idle()

if __name__ == '__main__':
    main()
