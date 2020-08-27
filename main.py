import requests
import os
import sys
import telebot
from dotenv import load_dotenv
from time import sleep
import logging


def send_message(tg_token, tg_chat_id, new_attempts):
    bot = telebot.TeleBot(tg_token, parse_mode='MARKDOWN')

    for attempt in new_attempts:
        lesson_title = attempt['lesson_title']
        if attempt['is_negative']:
            is_negative = 'Преподаватель *не принял* вашу работу. Нужно исправить ошибки.'
        else:
            is_negative = 'Преподаватель *принял* вашу работу! Можете приступать к следующему уроку.'

        bot.send_message(tg_chat_id, f'Урок: *{lesson_title}.*\nВаша работа проверена!\n\n{is_negative}')


def send_log_message(tg_token, tg_chat_id, text):
    bot = telebot.TeleBot(tg_token, parse_mode='MARKDOWN')
    bot.send_message(tg_chat_id, text)


def check_dvmn_result(dvmn_token, tg_token, tg_chat_id):
    header = {'Authorization': f'Token {dvmn_token}'}
    payload = {}
    url = 'https://dvmn.org/api/long_polling/'
    while True:
        try:
            response = requests.get(url, headers=header, params=payload, timeout=60)
            response.raise_for_status()
            dvmn_response = response.json()

            if dvmn_response['status'] == 'timeout':
                timestamp = dvmn_response['timestamp_to_request']

            if dvmn_response['status'] == 'found':
                timestamp = dvmn_response['last_attempt_timestamp']
                send_message(tg_token, tg_chat_id, dvmn_response['new_attempts'])

            payload.update({'timestamp': timestamp})
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError as e:
            sys.stderr.write('No Internet Connection \n')
            print(sys.stderr, e)
            sleep(60)


def main():

    load_dotenv()

    dvmn_token = os.getenv('DVMN_TOKEN')
    tg_token = os.getenv('TG_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')

    class MyLogsHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            send_log_message(tg_token, tg_chat_id, log_entry)


    logging.basicConfig(level=10)
    logger = logging.getLogger('TG')
    logger.addHandler(MyLogsHandler())

    while True:
        try:
            logger.warning('Бот запущен!')
            check_dvmn_result(dvmn_token, tg_token, tg_chat_id)
        except Exception as err:
            logger.error('Бот упал с ошибкой!')
            logger.error(err, exc_info=True)


if __name__ == '__main__':
    main()
