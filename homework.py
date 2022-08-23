import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
RESPONSE_JSON_ERROR = ('Произошла ошибка {error_value}. Параметры: {error}'
                       '{url}, {headers}, {params}')

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)
logger.setLevel(logging.CRITICAL)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logger.info('Отправка сообщения...')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError:
        raise exceptions.TelegramMessageException(
            'Сбой при отправке сообщения в Telegram'
        )
    else:
        logger.info('Удачная отправка сообщения в Telegram')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.info(
            f'Делаем запрос к endpoint {ENDPOINT};'
            f'Параметры: {params}')
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        error_message = f'Endpoint error: {error}'
        raise ConnectionError(error_message)
    if response.status_code != HTTPStatus.OK:
        error_message = 'При запросе к ENDPOINT код ответа не равен 200'
        raise ConnectionError(error_message)
    try:
        response_json = response.json()
    except Exception as error:
        raise ValueError(RESPONSE_JSON_ERROR.format(
            error_value=response_json[error],
            error=error)
        )


def check_response(response):
    """Проверяет ответ API."""
    if not response:
        raise exceptions.TelegramMessageException('Словарь пуст')
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем')
    homeworks = response.get('homeworks')
    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError('Ключ не найден')
    if not isinstance(homeworks, list):
        raise TypeError('Значение ключа homeworks не является списком')
    return homeworks


def parse_status(homework):
    """Извлекает информацию о конкретной домашней работе."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None or homework_status is None:
        raise KeyError(
            'В ответе отсутствует имя работы или статус '
            f'статус: {homework_status}, имя работы: {homework_name}')

    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if verdict is None:
        raise ValueError(
            f'Такого {homework_status} статуса нет'
        )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности всех переменных окружения."""
    return all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PRACTICUM_TOKEN])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют обязательные переменные окружения')
        sys.exit('Программа остановлена')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    prev_status = ''
    prev_message = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            current_status = parse_status(homeworks[0])
            if current_status != prev_status:
                prev_status = current_status
                send_message(bot, current_status)
            current_timestamp = response.get('current_date')
            logger.debug('Статус не изменился')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if prev_message != message:
                prev_message = message
                send_message(bot, message)
            logger.error(
                'Сбой при отправке сообщения в Telegram',
                exc_info=True)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    log_format = ('%(asctime)s [%(levelname)s] | '
                  'func: %(funcName)s / line: %(lineno)d | %(message)s')
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[logging.FileHandler(filename='main.log', mode='a'),
                  logging.StreamHandler()]
    )
    main()
