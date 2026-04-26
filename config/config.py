# config.py

# URL тестируемого сайта
BASE_URL = "http://localhost:8000/?balance=30000&reserved=20001"

# Таймауты (в секундах)
WAIT_TIMEOUT = 10  # Имплицитный таймаут для поиска элементов
PAGE_LOAD_TIMEOUT = 30  # Таймаут загрузки страницы
SCRIPT_TIMEOUT = 30  # Таймаут выполнения JavaScript

# Настройки браузера (для Microsoft Edge)
HEADLESS = False  # True — режим «без головы» (без видимого окна)
BROWSER = "edge"  # Указываем Edge вместо Chrome
DRIVER_PATH = "./msedgedriver.exe"  # Путь к msedgedriver.exe (если не в PATH)

# Селекторы элементов UI (CSS-селекторы или XPath)
SELECTORS = {
    "balance_field": "css selector here",  # Пример: ".balance"
    "reserved_field": "css selector here",  # Пример: ".reserved"
    "transfer_button": "css selector here",  # Кнопка «Перевести»
    "card_input": "css selector here",  # Поле для ввода номера карты
    "amount_input": "css selector here",  # Поле для суммы перевода
    "error_message": "css selector here",  # Элемент с сообщением об ошибке
    "success_message": "css selector here"  # Элемент с сообщением об успехе
}

# Режимы работы
ENVIRONMENT = "local"  # local, test, staging, prod
LOG_LEVEL = "INFO"  # Уровень логирования: DEBUG, INFO, WARNING, ERROR

# Параметры для тестов с платежами
MIN_TRANSFER_AMOUNT = 1  # Минимальная сумма перевода
MAX_TRANSFER_AMOUNT = 100000  # Максимальная сумма перевода
VALID_CARD_NUMBER = "1111222233334444"  # Валидный номер карты для тестов

# Строки ожидаемых сообщений (для валидации)
EXPECTED_SUCCESS_MESSAGE = "Перевод выполнен успешно"
EXPECTED_ERROR_MESSAGE = "Недостаточно средств"

# Дополнительные настройки
RETRY_COUNT = 3  # Количество повторных попыток при ошибке
POLLING_INTERVAL = 0.5  # Интервал опроса элементов (в секундах)