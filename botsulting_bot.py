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
MENU, WAITING_TRIVIA_ANSWER, GAME, RIDDLE = range(4)
BOT_NAME = "Botsulting"


def start(bot, update):
    reply_keyboard = [['Trivia knowledge', 'Riddle me this', 'Multiplayer Game']]

    update.message.reply_text(
        'Hello, I am ' + BOT_NAME +
        '. <b>What</b> do you want to do today?\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True),
        parse_mode=ParseMode.HTML)  # Doesn't parse it as HTML :(

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


def game(bot, update):
    text = update.message.text
    print update.message.from_user.first_name + ' started playing ' + text
    update.message.reply_text('Welcome to ' + text + '! Let\'s get started...')
    return GAME


def get_trivia_list(amount=10, category=None, difficulty=None):
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
users = {}


def send_trivia(bot, update):
    update.message.reply_text('You\'re playing trivia!')
    update.message.reply_text('Ready to loose, ' + update.message.from_user.first_name + '?')

    # add user to users array if not there yet
    telegram_user = update.message.from_user

    if not telegram_user.id in users:
        users[telegram_user.id] = {
            'telegram_user': telegram_user,
            'points': 0,
            'asked_questions': []
        }

    user = users[telegram_user.id]
    logger.info('I\'m playing trivia! Points: ' + str(user['points']))

    # get, generate and send NEW trivia question
    question = random.choice(trivia_collection)
    while question['question'] in user['asked_questions']:
        question = random.choice(trivia_collection)
    final_text, correct_choice = build_trivia_question(question)
    logger.info(final_text)

    reply_keyboard = [OPTIONS[:2], OPTIONS[-2:]]

    update.message.reply_text(
        final_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    # add question and correct choice to the user object
    user['current_question'] = question
    user['correct_choice'] = correct_choice

    # mark question as asked
    user['asked_questions'].append(question['question'])

    # return state waiting_trivia_answer
    return WAITING_TRIVIA_ANSWER


def build_trivia_question(question):
    question_text = question['question'] + '\n'
    answers_list = question['incorrect_answers'][:]
    answers_list.append(question['correct_answer'])
    random.shuffle(answers_list)
    correct_choice = answers_list.index(question['correct_answer'])
    final_text = question_text + '\n'.join(['\\' + OPTIONS[i] + ' ' + a for i, a in enumerate(answers_list)])
    return final_text, correct_choice


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


def check_trivia_answer(bot, update):
    # get current question, check correctness
    telegram_user = update.message.from_user
    user = users[telegram_user.id]
    question = user['current_question']
    user_answer = update.message.text

    logger.info('User answer: ' + user_answer)
    logger.info('Correct answer: ' + OPTIONS[user['correct_choice']])
    if user_answer == OPTIONS[user['correct_choice']]:
        # correct answer
        update.message.reply_text('Hum, so you got it right this time... Don\'t get used to it')
        user['points'] += 1
    else:
        # jej poor noob
        update.message.reply_text('Oh, that\'s wrong! Don\'t worry, I wasn\'t expecting much.' +
                                  '\n The correct answer was ' + question['correct_answer'])

    # insult appropriately
    # [increase user points]
    # call send_trivia
    return send_trivia(bot, update)


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
                   RegexHandler('^(Trivia knowledge)$', send_trivia),
                   RegexHandler('^(Multiplayer Game)$', game)],

            WAITING_TRIVIA_ANSWER: [MessageHandler([Filters.text], check_trivia_answer),
                                    CommandHandler('skip', error)],

            GAME: [MessageHandler([Filters.location], error),
                   CommandHandler('skip', error)],

            RIDDLE: [MessageHandler([Filters.text], error)]
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
