from telegram import *
from telegram.ext import *
import logging
import youtube_dl
from yout import YoutubeSearch
from flask import Flask, Response
from os import environ
from threading import Thread
import requests
from uuid import uuid4

GET_DOWNLOADMUSIC1, GET_DOWNLOADMUSIC2, GET_DOWNLOADMUSIC3 = range(3)

song_url = str()
song_name = str()
app = Flask(__name__)


ctx = app.test_request_context()
ctx.push()


def flask_streaming():

    r = requests.get(url, stream=True)
    return Response(
        r.iter_content(chunk_size=10 * 1024), content_type=r.headers["Content-Type"]
    )


@app.route("/")
def hello():
    return "sedlyf"


def start_flask():
    port = int(environ.get("PORT", 5000))
    app.run(threaded=True, host="0.0.0.0", port=port)


def yt_url(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:

        result = ydl.extract_info(url, download=False)
    return result.get("url")


def start(update, context):
    update.message.reply_text("hi, enter song name to listen")
    return GET_DOWNLOADMUSIC1


def downloadmusic(update, context):
    names = list()
    global title
    title = dict()
    song_name = update.message.text
    print(song_name)
    update.message.reply_text("searching")

    try:
        search_results = YoutubeSearch(str(song_name), max_results=5).to_dict()

        for i in search_results:
            title[i["title"]] = "https://youtube.com" + i["url_suffix"]
            names.append(i["title"])

        keyboard = [
            [InlineKeyboardButton(names[0], callback_data="0")],
            [InlineKeyboardButton(names[1], callback_data="1")],
            [InlineKeyboardButton(names[2], callback_data="2")],
            [InlineKeyboardButton(names[3], callback_data="3")],
            [InlineKeyboardButton(names[4], callback_data="4")],
            [InlineKeyboardButton("Cancel", callback_data="5")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("Please choose:", reply_markup=reply_markup)

        return GET_DOWNLOADMUSIC2
    except:
        return ConversationHandler.END


def button(update, context):
    query = update.callback_query
    onk = list()

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    print(title)
    for i in title:
        onk.append(i)
    choice = query.data
    if int(choice) == 5:
        query.edit_message_text(
            text="You have choosen cancel, \n /start to start bot again"
        )
        return ConversationHandler.END

    global url
    url = yt_url(title[onk[int(choice)]])
    print(url)
    streamlink = "/" + str(uuid4())
    app.add_url_rule(streamlink, "flask_streaming", flask_streaming)
    global song_url
    song_url = "your host with port" + streamlink
    print(song_url)

    query.edit_message_text(
        text="Selected title : {}\n reply 'confirm'   to confirm".format(
            onk[int(choice)]
        )
    )
    return GET_DOWNLOADMUSIC3


def display_results(update, context):
    title = dict()

    update.message.reply_text(song_url)
    return ConversationHandler.END


def error(update, error):
    print('Update "{}" caused error "{}"'.format(update, error))
    return ConversationHandler.END


if __name__ == "__main__":

    t1 = Thread(target=start_flask)
    t1.start()

    key = "your api key"
    updater = Updater(key, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_DOWNLOADMUSIC1: [MessageHandler(Filters.text, downloadmusic)],
            GET_DOWNLOADMUSIC2: [CallbackQueryHandler(button)],
            GET_DOWNLOADMUSIC3: [MessageHandler(Filters.text, display_results)],
        },
        fallbacks=[MessageHandler(Filters.text, error, pass_user_data=True),],
    )
    dp.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()
