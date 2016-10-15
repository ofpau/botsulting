#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
This Bot uses the Updater class to handle the bot.

First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line
    Define a ConversationHandler where one if its states corresponds to another ConversationHandler
    Trigger the nested ConversationHandler
    End the nested ConversationHandler using the Conversation.END state.

Expected behaviour

There should be an option to manipulate the "external" conversation state, as possible with other Handlers.
Actual behaviour

Since the last return value of the nested conversation is END, there is no option to alter the external conversation state, and it's "stuck" in that state.

Linked to #385 ne or send a signal to the process to stop the
bot.
"""

from telegram import (ReplyKeyboardMarkup, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging
import os
import urllib2
import json
import random

TELEGRAM_KEY = os.environ['TELEGRAM_KEY']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

# Program setup
MENU, TRIVIA, GAME, RIDDLE = range(4)
BOT_NAME = "Botsulting"


def start(bot, update):
    reply_keyboard = [['Trivia knowledge', 'Riddle me this', 'Multiplayer Game']]

    update.message.reply_text(
        'Hello, I am ' + BOT_NAME +
        '. <b>What</b> do you want to do today?\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True),
        parse_mode=ParseMode.HTML) # Doesn't parse it as HTML :(

    return MENU


def menu(bot, update):
    text = update.message.text
    print text
    update.message.reply_text('Got it! You chose ' + text + 'Let\'s get started.')


def riddle(bot, update):
    text = update.message.text
    print update.message.from_user.first_name + ' started playing ' + text
    update.message.reply_text('Welcome to ' + text + '! Let\'s get started...')
    return RIDDLE


def trivia(bot, update):
    text = update.message.text
    print update.message.from_user.first_name + ' started playing ' + text
    update.message.reply_text('Welcome to ' + text + '! Let\'s get started...')
    return TRIVIA


def game(bot, update):
    text = update.message.text
    print update.message.from_user.first_name + ' started playing ' + text
    update.message.reply_text('Welcome to ' + text + '! Let\'s get started...')
    return GAME


def get_trivia_list(amount=100, category=None, difficulty=None):
    url = "http://opentdb.com/api.php?"
    urlfinal = "http://opentdb.com/api.php?amount=10&category=24&difficulty=easy"

    if amount:
        url = url + '&amount=' + str(amount)
    if category:
        url = url + '&category=' + category
    if difficulty:
        url = url + '&difficulty=' + difficulty
    logger.info('Getting trivia from ' + url)

    result = urllib2.urlopen(url).read()
    result_json = json.loads(result)
    if result_json['response_code'] == 0:
        logger.info('Fetched result correctly.')
        return result_json['results']
    else:
        logger.exception('No results!!')
        return []


trivia_collection = get_trivia_list()

'''
[,
    {
      u'category': u'Entertainment: Board Games',
      u'correct_answer': u'Monopoly',
      u'difficulty': u'easy',
      u'incorrect_answers': [u'Pay Day', u'Cluedo', u'Coppit'],
      u'question': u'Which of these games includes the phrase &quot;Do not pass Go, do not collect $200&quot;?',
      u'type': u'multiple'
    },
]
'''

OPTIONS = ['A', 'B', 'C', 'D']

def trivia(bot, update, points=0):
    logger.info('I\'m playing trivia! Points: ' + str(points))

    update.message.reply_text('You\'re playing trivia!')
    update.message.reply_text('Ready to loose, ' + update.message.from_user.first_name + '?')
    logger.info('Returning ' + str(TRIVIA))

    question = random.choice(trivia_collection).copy()
    question_text = question['question'] + '\n'
    answers_list = question['incorrect_answers'][:]
    answers_list.append(question['correct_answer'])
    random.shuffle(answers_list)
    final_text = question_text + '\n'.join(['\\' + OPTIONS[i] + ' ' + a for i, a in enumerate(answers_list)])
    logger.info(final_text)

    reply_keyboard = [OPTIONS[:2], OPTIONS[-2:]]

    update.message.reply_text(
        final_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    update.message

    return TRIVIA


# setup of individual funtions within program
def triviaPreview(question, correct_answer, wrong_answers):  # questions and answers taken from api
    for question in trivia_collection:
        update.message.text_question  # sends question for player
        # send possible answers
        update.message.reply_text(
            'What do you think?',
            reply_keyboard=[['A', 'B', 'C', 'D']],  # answer keyboard for player
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        if reply_markup == correct_answer:
            update.message.text("So you think you\'re smart, huh? Let\'s try another?",
                                reply_keyboard=[['Yes', 'No']],
                                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            if reply_markup == "No":
                return MENU
            else:
                return TRIVIA


def gender(bot, update):
    user = update.message.from_user
    answer = update.message.text
    if trivia_list[question].correctAnswer == answer:
        logger.info("Gender of %s: %s" % (user.first_name, update.message.text))
        update.message.reply_text('I see! Please send me a photo of yourself, '
                                  'so I know what you look like, or send /skip if you don\'t want to.')

    return PHOTO


def photo(bot, update):
    user = update.message.from_user
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s" % (user.first_name, 'user_photo.jpg'))
    update.message.reply_text('Gorgeous! Now, send me your location please, '
                              'or send /skip if you don\'t want to.')

    return LOCATION


def skip_photo(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a photo." % user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return LOCATION


def location(bot, update):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f"
                % (user.first_name, user_location.latitude, user_location.longitude))
    update.message.reply_text('Maybe I can visit you sometime! '
                              'At last, tell me something about yourself.')

    return BIO


def skip_location(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a location." % user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'At last, tell me something about yourself.')

    return BIO


def bio(bot, update):
    user = update.message.from_user
    logger.info("Bio of %s: %s" % (user.first_name, update.message.text))
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Oh no... Did I insult you? I thought you wouldn\'t notice')

    return ConversationHandler.END


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TELEGRAM_KEY)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states MENU, TRIVIA, GAME and RIDDLE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            MENU: [RegexHandler('^(Riddle me this)$', riddle),
                   RegexHandler('^(Trivia knowledge)$', trivia),
                   RegexHandler('^(Multiplayer Game)$', game)],

            TRIVIA: [MessageHandler([Filters.text], trivia),
                     CommandHandler('skip', skip_photo)],

            GAME: [MessageHandler([Filters.location], location),
                   CommandHandler('skip', skip_location)],

            RIDDLE: [MessageHandler([Filters.text], bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
