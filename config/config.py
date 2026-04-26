# Настройки браузера (для Microsoft Edge)
HEADLESS = False
BROWSER = "edge"
DRIVER_PATH = "./msedgedriver.exe"

# Селекторы элементов UI (CSS‑селекторы или XPath)
SELECTORS = {
    "balance_field": ".balance",  # Пример: ".balance"
    "reserved_field": ".reserved",  # Пример: ".reserved"
    "transfer_button": "#transfer_button",  # Кнопка «Перевести»
    "card_input": "#card_number",  # Поле для ввода номера карты
    "amount_input": "#amount",  # Поле для суммы перевода
    "error_message": ".error-message",  # Элемент с сообщением об ошибке
    "success_message": ".success-message"  # Элемент с сообщением об успехе
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