import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from config import BOT_TOKEN
import sqlite3
import datetime as dt

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG  # logging
)
logger = logging.getLogger(__name__)
name = ''


async def handler(update, context):  # Любое сообщение кроме команд и нужного
    await update.message.reply_html('Very intresting position')


async def start(update, context):  # /start func добавление в data base.
    print('\033[33mRunning start\033[0m')
    user = update.effective_user
    con = sqlite3.connect('data/people_acco.db')
    c = con.cursor()
    if c.execute('''SELECT name FROM chat
                    WHERE name == ?''', (user.username,)).fetchone() is None:
        print('\033[33mADDING A NEW USER\033[0m')
        c.execute('''INSERT INTO chat VALUES (?, ?)''', (user.username, ''))
        print('\033[33mADDED A NEW USER\033[0m')
    else:
        print('\033[91mUSER IS ALREADY INSYSTEM\033[0m')
    await update.message.reply_html(
        rf"Hello {user.mention_html()}! I am VSMS.")
    con.commit()
    con.close()


async def check(update, context):  # проверка на наличие message
    print('\033[33mRunning check\033[0m')
    user = update.effective_user.username
    con = sqlite3.connect('data/people_acco.db')
    c = con.cursor()
    messages = c.execute('''SELECT messages FROM chat
                            WHERE name = ?''', (user,)).fetchone()
    c.execute('''UPDATE chat
                SET messages = ?
                WHERE name = ?''', ('', user))
    con.commit()
    con.close()
    messages = messages[0].split('\n')
    if len(messages) > 1:
        await update.message.reply_html(f'You have {len(messages) - 1} new messages\n' + '\n'.join(
            [f'{x + 1}) Message:\n\t{messages[x + 1]}' for x in range(len(messages[1:]))]))
    else:
        await update.message.reply_html('You have no new messages')


async def send(update, context):  # отправка сообщений
    print('\033[33mRunning send\033[0m')
    await update.message.reply_html("To: Pass name.\nSend /stop if you want to cancel action")
    return 1


async def first_response(update, context):  # для отправки
    username = update.message.text
    con = sqlite3.connect('data/people_acco.db')
    c = con.cursor()
    if c.execute('''SELECT name FROM chat
                    WHERE name = ?''', (username,)).fetchone() is not None:
        await update.message.reply_text(
            'Found a user: What message do you want to send them?.\nSend /stop if you want to cancel action')
        global name
        name = username
        con.close()
        return 2
    con.close()
    await update.message.reply_text("Can't find a user: try again.\nSend /stop if you want to cancel action")
    return 1


async def second_response(update, context):  # для отправки
    global name
    message = update.message.text
    con = sqlite3.connect('data/people_acco.db')
    c = con.cursor()
    c.execute('''UPDATE chat
                SET messages = ?
                WHERE name = ?''', (c.execute('''SELECT messages FROM chat
                                                WHERE name = ?''', (name,)).fetchone()[0] + '\n' + message, name))
    con.commit()
    con.close()
    with open(rf'data/VSMStorage/{update.effective_user.username}.txt', mode='a', encoding='utf-8') as a:
        a.writelines(f'{dt.datetime.now()} To: {name}; Message: {message}\n')
    await update.message.reply_text("Message was successfully sent")
    return ConversationHandler.END


async def stop(update, context):  # stop func
    await update.message.reply_text("Stopping")
    return ConversationHandler.END


async def creator(update, context):  # creator
    print('\033[33mRunning creator\033[0m')
    await update.message.reply_html('<a href="tg://user?id=1027803322">Xemonay</a>')


def main():  # связь с классами
    application = Application.builder().token(BOT_TOKEN).build()
    text_handler = MessageHandler(filters.TEXT, handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("creator", creator))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('send', send)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)
    application.add_handler(text_handler)
    print('\033[32mthe Sstart of the bot\033[0m')
    application.run_polling()
    # After Closing the bot
    print('\033[43mthe End of the bot\033[0m')


if __name__ == '__main__':  # beautiful
    main()
