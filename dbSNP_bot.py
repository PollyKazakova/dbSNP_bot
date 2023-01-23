#!/usr/bin/env python
"""
Version: 0.0.1
Date: 23/01/2023 09:00

Usage:
    python3 dbSNP_bot.py
"""

#pip install pytelegrambotapi
#pip install requests
#pip install bs4
#pip install lxml


import telebot
from telebot import types
import logging
import requests
from bs4 import BeautifulSoup


logger = telebot.logger
logging.basicConfig(filename='dbSNP_bot.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

bot = telebot.TeleBot(<TOKEN>)


@bot.message_handler(commands=['start'])
def get_start(message):
    bot.send_message(message.chat.id, 'Welcome to dbSNP_bot ☑️\nSend me your name, please!')
    bot.register_next_step_handler(message, get_choice)

@bot.message_handler(commands=['help'])
def get_help(message):
    bot.send_message(message.chat.id, 'I can send you information about dbSNP: overview, last release and any rs. \
                     \n\nSend /start for to get started (main menu). Send /continue for check rs again and again.')

@bot.message_handler(commands=['stop'])
def get_stop(message):
    bot.send_message(message.chat.id, 'Hope you have got necessary information.\nBye!')

@bot.message_handler(commands=['continue'])
def get_continue(message):
    bot.send_message(message.chat.id,'Send your rs, please.\n\nCorrect format: rs1874')
    bot.register_next_step_handler(message, continue_check_rs)


def get_choice(message):
    keyboard = types.InlineKeyboardMarkup()
    key_about = types.InlineKeyboardButton(text='dbSNP Overview', callback_data='overview')
    keyboard.add(key_about)
    key_release= types.InlineKeyboardButton(text='Current version', callback_data='release')
    keyboard.add(key_release)
    key_rs = types.InlineKeyboardButton(text='Check information about rs', callback_data='rs')
    keyboard.add(key_rs)
    question = f'{message.text}, pick what you want to do:'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'overview':
        bot.send_message(call.message.chat.id, get_overview())
        bot.send_message(call.message.chat.id, 'Send /continue for checking else one rs. \
                         \n\nSend /start for enter to the main menu. \
                         \n\nSend /stop for finish work.')

    elif call.data == 'release':
        bot.send_message(call.message.chat.id, get_current_release())
        bot.send_message(call.message.chat.id, 'Send /continue for checking else one rs. \
                         \n\nSend /start for enter to the main menu. \
                         \n\nSend /stop for finish work.')

    elif call.data == 'rs':
        bot.send_message(call.message.chat.id, 'Send your rs, please.\n\nCorrect format: rs1874')
        @bot.message_handler(content_types=['text'])
        def get_rs(message):
            url =  f'https://www.ncbi.nlm.nih.gov/snp/{message.text}#frequency_tab'
            if requests.get(url).status_code != 200:
                bot.send_message(message.chat.id, "It's an incorrent rs. Please check it.")
                bot.send_message(message.chat.id, 'Send /continue for checking else one rs. \
                         \n\nSend /start for enter to the main menu. \
                         \n\nSend /stop for finish work.')
            else:
                bot.send_message(message.chat.id, get_check_rs(url))
                bot.send_message(message.chat.id, 'Send /continue for checking else one rs. \
                         \n\nSend /start for enter to the main menu. \
                         \n\nSend /stop for finish work.')

def get_overview():
    url = 'https://www.ncbi.nlm.nih.gov/projects/SNP/get_html.cgi?whichHtml=overview'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/108.0.0.0 Safari/537.36'
    }
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml").findAll('p')
    data = ''

    for i in soup[1:5]:
        if i.get_text().strip().replace('\n', ' ').__contains__(' (see How To Submit)'):
            data = data + i.get_text().strip().replace('\n', ' ').replace(' (see How To Submit)', '') + '\n' * 2
        else:
            data = data + i.get_text().strip().replace('\n', ' ') + '\n' * 2

    return data

def get_current_release():
    url = 'https://www.ncbi.nlm.nih.gov/projects/SNP/snp_summary.cgi'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/108.0.0.0 Safari/537.36'
    }
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml").find_all('strong')

    return soup[0].text

def continue_check_rs(message):
    url = f'https://www.ncbi.nlm.nih.gov/snp/{message.text}#frequency_tab'
    if requests.get(url).status_code != 200:
        bot.send_message(message.chat.id, "It's an incorrent rs or dbSNP doesn't contain information about it. \
        Please check it.")
        bot.send_message(message.chat.id, 'Send /continue for checking else one rs. \
                         \n\nSend /start for enter to the main menu. \
                         \n\nSend /stop for finish work.')
    else:
        bot.send_message(message.chat.id, get_check_rs(url))
        bot.send_message(message.chat.id, 'Send /continue for checking else one rs. \
                         \n\nSend /start for enter to the main menu. \
                         \n\nSend /stop for finish work.')

def get_check_rs(url):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/108.0.0.0 Safari/537.36'
    }
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    summary = soup.find(class_='summary-box usa-grid-full')
    text = summary.text.split('\n')
    main_words = ['Organism', 'Position', 'Alleles', 'Variation Type', 'Frequency', 'Clinical Significance',
                  'Gene : Consequence', 'Status']
    data = ''

    if len(text) <= 20:
        for i in text:
            if i.__contains__('was withdrawn on') or i.__contains__('was merged into') or i.__contains__('Build'):
                data = data + i.strip() + ' '
            elif len(i) == 0 or i.isspace() == 1 or i.__contains__('more') == 1:
                continue
            elif i in main_words:
                data = data + '\n' + i.strip() + '\n'
            else:
                data = data + i.strip() + '\n'

    else:
        for i in text[:len(text)-14]:
            if len(i) == 0 or i.isspace() == 1 or i.__contains__('more') == 1:
                continue
            else:
                if i.__contains__('Help'):
                    i = i.rstrip('HelpThe anchor position for this RefSNP. Includes all nucleotides potentially \
                    affected by this change, thus it can differ from HGVS, which is right-shifted. \
                    See here for details.')
                    data = data + i + '\n'
                elif i in main_words:
                    data = data + '\n' + i + '\n'
                else:
                    data = data + i.strip() + '\n'

    return data


if __name__ == "__main__":

    try:
        bot.polling(none_stop=True, interval=0)

    except Exception as e:
        print(str(e))
