# URLs-Checker
**Technical task for Auchan company**

*Что делает программа*  
1. Загружает данные из файла [messages_to_parse.dat](/messages_to_parse.dat)
с помощью модуля [pickle](https://docs.python.org/3/library/pickle.html).
2. Используя библиотеку [URLExtract](https://pypi.org/project/urlextract/)
парсит данные и вытаскивает оттуда все URL адреса.
3. Каждый из этих адресов проверяет на доступность с помощью
[requests](https://requests.readthedocs.io/en/latest/).head.
На выходе формирует 2 словаря: один содержит ключи — оригинальные ссылки,
значения — коды статуса ответа, а второй содержит
оригинальные ссылки как ключи и раскрытые (финальные) ссылки как значения.
4. Код покрыт логами ([loguru](https://loguru.readthedocs.io/en/stable/index.html)).
Логи сохраняются в файл.
Каждые 5 минут при работе программы создаётся новый файл с логами.
А файлы логов, которые старше 20 минут, удаляются автоматом.

В работе программы используются потоки
([threading](https://docs.python.org/3/library/threading.html))
для отмизации работы со ссылками.
Чтобы поочерёдно не ждать завершения обработки каждой,
это делается конкурентно, что значительно экономит
время выполнения скрипта.

Среднее время работы программы: 10 секунд (зависит от скорости интернета).  
Количество найденных и обработанных ссылок в словарях: 67  
Количество ссылок с ошибкой по времени ожидания ответа: 4
