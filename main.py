import requests
import os
import telebot
from dotenv import load_dotenv
from time import sleep

def send_message(new_attempts):
    bot = telebot.TeleBot(token_tlgrm, parse_mode='MARKDOWN')

    for attempt in new_attempts:
        lesson_title = attempt['lesson_title']
        if attempt['is_negative'] == True:
            is_negative = 'Преподаватель *не принял* вашу работу. Нужно исправить ошибки'
        else:
            is_negative = 'Преподаватель *принял* вашу работу! Можете приступать к следующему уроку'

        bot.send_message(70148681, f'{lesson_title}\n*Работа проверена!*\n\n{is_negative}')



def check_info(token_dvmn):
    url = 'https://dvmn.org/api/long_polling/'
    header = {'Authorization': f'Token {token_dvmn}'}

    while True:
        try:
            response = requests.get(url, headers=header).json()
            if 'timestamp_to_request' in response:
                timestamp = str(response['timestamp_to_request'])
            if 'last_attempt_timestamp' in response:
                timestamp = str(response['last_attempt_timestamp'])
                send_message(response['new_attempts'])
            url = f'https://dvmn.org/api/long_polling/?timestamp={timestamp}'
        except requests.exceptions.ReadTimeout:
            sleep(60)
        except requests.exceptions.ConnectionError:
            sleep(60)


def main():
    load_dotenv()
    token_dvmn = os.getenv('TOKEN_DVMN')
    global token_tlgrm
    token_tlgrm = os.getenv('TOKEN_TLGRM')
    check_info(token_dvmn)


if __name__ == '__main__':
    main()
