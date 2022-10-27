import pickle
import threading
from time import perf_counter

import requests
from environs import Env
from loguru import logger
from urlextract import URLExtract

ENV = Env()
ENV.read_env()
LOCKER = threading.Lock()
logger.add(
    "logs/debug.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation=ENV.str("create_new_logfile_every"),
    retention=ENV.str("delete_logfile_older_then"))


def get_file_data(filename: str):
    """Получает данные на чтение из файла."""
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
    
    except FileNotFoundError as error_message:
        logger.error(error_message)

    else:
        return data


def check_url(checked_urls: list, url: str):
    """Отправлет запрос по ссылке и формирует два словаря:
    1) Ключ — изначальная ссылка, значение — статус ответа.
    2) Ключ — изначальная ссылка, значение — финальная ссылка.\n
    Записывает их в общий список."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        head_request = requests.head(url, allow_redirects=True, timeout=5)
        url_status_code = head_request.status_code
        unshorten_url = head_request.url
    
    except requests.exceptions.RequestException as error_message:
        logger.error(f"{url} —→ {error_message}")
    
    else:
        with LOCKER:
            checked_urls.append(
                ({url: url_status_code}, {url: unshorten_url}))


@logger.catch
def extract_urls_from_file(filename: str):
    """Ищет и сохраняет в список ссылки из файла."""
    urls = list()
    extract = URLExtract()
    file_data = get_file_data(filename)
    if file_data:
        for strng in file_data:
            urls.extend(extract.find_urls(strng))
    
    return urls


@logger.catch
def checking_urls(list_urls: list):
    """Проверяет ссылки и возвращает список данных по ним."""
    thr_list = list()
    checked_urls = list()
    for url in list_urls:
        thr = threading.Thread(
            target=check_url,
            args=(checked_urls, url)
        )
        thr_list.append(thr)
        thr.start()

    for thr in thr_list:
        thr.join()

    del thr_list
    return checked_urls


@logger.catch
def logging_output_data(data: list):
    """Записывает в журнал выходные данные программы."""
    raw_logging = logger.opt(raw=True)
    raw_logging.info(" OUTPUT DATA ".join(("=" * 43,) * 2) + "\n")
    for first_dict, second_dict in (url_data for url_data in data):
        raw_logging.info(f"{first_dict} || {second_dict}\n")
    
    raw_logging.info(
        f"\nAmount first and second dictionaries: {len(data)}\n")


if __name__ == "__main__":
    logger.info("The URLs Checker program started working.")
    t0 = perf_counter()
    urls = extract_urls_from_file(ENV.str("URLs_filename"))
    urls_data = checking_urls(urls)
    logging_output_data(urls_data)
    logger.info((
        "The program completed its work in: "
        f"{round(perf_counter() - t0, 2)}s.\n{'=' * 99}"))
