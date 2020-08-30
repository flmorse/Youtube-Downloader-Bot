import os
from pytube import YouTube
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def start_help_handler(update, context):
    bot = context.bot
    bot.send_message(reply_to_message_id=update.message.message_id, chat_id=update.message.chat.id,
                     text='send your video link !!!')


def get_video_info(link):
    try:
        video = YouTube(link)
        info = 'Duration : ' + time.strftime('%H:%M:%S', time.gmtime(video.length)) + '\nTittle :' + video.title
        return info, video.streams.filter(type="video", file_extension="mp4").all()

    except:
        return 'Error', None


def get_link_video_handler(update, context):
    bot = context.bot
    msg = bot.send_message(reply_to_message_id=update.message.message_id, chat_id=update.message.chat.id, text='Processing...')
    info, streams = get_video_info(update.message.text)
    if info == 'Error':
        bot.edit_message_text(chat_id=update.message.chat.id, message_id=msg.message_id, text=info + ' , Try Again !!!')
    else:
        dont_add = []
        keyborad = []
        for stream in streams:
            text = stream.resolution
            let = 1
            for i in dont_add:
                if i == text:
                    let = 0
                    break
            dont_add.append(text)
            if let == 1:
                keyborad.append([InlineKeyboardButton(text=text, callback_data=text)])

            let = 1
        bot.edit_message_text(message_id=msg.message_id, chat_id=update.message.chat.id, text=info+"\nSelect preferred file  !!!!\n", reply_markup=InlineKeyboardMarkup(keyborad))


def download_video(link, res):
    try:
        video = YouTube(link)
        stream = video.streams.filter(file_extension="mp4")
        stream.get_by_resolution(res=res).download(filename=link+'-'+res)
        #stream = stream.first()
        #stream.download(filename=link+'-'+res)
        return link+'-'+res
    except:
        return 'Error'


def resolution_choice_handler(update, context):
    bot = context.bot
    query = update.callback_query
    bot.edit_message_text(message_id=query.message.message_id, chat_id=query.message.chat.id, text='Downloading.....', reply_markup=None)
    download = download_video(link=query.message.reply_to_message.text, res=query.data)
    if download == 'Error':
        bot.edit_message_text(message_id=query.message.message_id, chat_id=query.message.chat.id,
                              text='Error , try again !!!', reply_markup=None)
    else:
        bot.edit_message_text(message_id=query.message.message_id, chat_id=query.message.chat.id,
                              text='Downloaded .', reply_markup=None)
        bot.send_video(reply_to_message_id=query.message.message_id, chat_id=query.message.chat.id, video=download)


if __name__ == '__main__':
    updater = Updater(token=open(os.getcwd() + '/Token.txt', 'r').read(), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_help_handler))
    dp.add_handler(CommandHandler("help", start_help_handler))
    dp.add_handler(MessageHandler(Filters.regex(pattern="^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"), callback=get_link_video_handler))
    dp.add_handler(CallbackQueryHandler(resolution_choice_handler))

    updater.start_polling()
    updater.idle()