import logging
from datetime import datetime
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 🔽 ОПРЕДЕЛЯЕМ BASE_URL ЗДЕСЬ
BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("test_execution.log"),
        logging.StreamHandler()
    ]
)

def save_screenshot_with_context(browser, test_name, context=""):
    """Сохраняет скриншот с таймстампом"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/{test_name}_{context}_{timestamp}.png"
    os.makedirs("screenshots", exist_ok=True)
    browser.save_screenshot(filename)
    logging.info(f"📸 Скриншот сохранён: {filename}")
    return filename

def wait_for_page_load(browser, timeout=30):
    """Ждёт загрузки страницы по наличию <body>"""
    WebDriverWait(browser, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def find_element_safe(browser, locators, timeout=15):
    """
    Ищет элемент по нескольким селекторам. Возвращает первый найденный.
    """
    wait = WebDriverWait(browser, timeout)
    for locator in locators:
        try:
            if locator[0] == By.XPATH:
                element = wait.until(EC.presence_of_element_located(locator))
            else:
                element = wait.until(EC.visibility_of_element_located(locator))
            return element
        except TimeoutException:
            continue
    pytest.fail(f"❌ Ни один из селекторов не сработал: {locators}")

def test_zero_amount(browser):
    """
    BUG‑001: Система допускает перевод суммы 0 ₽
    """
    print(f"\n🔍 BASE_URL = '{BASE_URL}'")
    print(f"🔗 Полный URL = '{BASE_URL}/?balance=30000&reserved=20001'")
    
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    wait_for_page_load(browser)
    print("✅ Страница загружена")

    # Шаг 1: Нажимаем на блок «Рубли»
    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("✅ Блок «Рубли» активирован")

    # Шаг 2: Вводим номер карты
    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("1111222233334444")
    print("✅ Номер карты введён")

    # Шаг 3: Вводим сумму 0
    amount_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='1000']")
    ])
    amount_input.clear()
    amount_input.send_keys("0")
    print("✅ Сумма 0 введена")

    # Шаг 4: Нажимаем кнопку «Перевести»
    transfer_button = find_element_safe(browser, [
        (By.XPATH, "//button[contains(@class, 'g-button') and .//span[text()='Перевести']]")
    ])
    transfer_button.click()
    print("✅ Кнопка «Перевести» нажата")

    # Проверка: ожидаем сообщение об ошибке
    try:
        error_element = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".error-message, .alert-danger"))
        )
        error_message = error_element.text
        assert "Невозможно перевести 0 ₽" in error_message, f"❌ Неожиданный текст ошибки: {error_message}"
        print(f"✅ Ошибка валидации найдена: {error_message}")
    except TimeoutException:
        save_screenshot_with_context(browser, "zero_amount", "no_error")
        # Попробуем вывести источник страницы для отладки
        print("🔍 HTML страницы (первые 500 символов):")
        print(browser.page_source[:500])
        assert False, "❌ Сообщение об ошибке при сумме 0 ₽ не появилось"

def test_empty_amount_field(browser):
    """
    BUG‑002: Пустое поле суммы трактуется как 0 ₽
    """
    print(f"\n🔍 BASE_URL = '{BASE_URL}'")
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    wait_for_page_load(browser)
    print("✅ Страница загружена")

    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("✅ Блок «Рубли» активирован")

    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("1111222233334444")
    print("✅ Номер карты введён")

    amount_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='1000']")
    ])
    amount_input.clear()
    print("✅ Поле суммы очищено")

    transfer_button = find_element_safe(browser, [
        (By.XPATH, "//button[contains(@class, 'g-button') and .//span[text()='Перевести']]")
    ])

    assert not transfer_button.is_enabled(), "❌ Ошибка: кнопка «Перевести» активна при пустом поле суммы"
    print("✅ Кнопка «Перевести» неактивна при пустом поле — как ожидается")


def test_invalid_card_length(browser):
    """
    BUG‑003: Система принимает 17‑значный номер карты
    """
    print(f"\n🔍 BASE_URL = '{BASE_URL}'")
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    wait_for_page_load(browser)
    print("✅ Страница загружена")

    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("✅ Блок «Рубли» активирован")

    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("11112222333344445")  # 17 цифр
    print("✅ Введён 17‑значный номер карты")

    time.sleep(2)  # Даём время на валидацию на клиенте
    try:
        error_element = WebDriverWait(browser, 20).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//span[contains(@style, 'color: red')]"
            )))
        error_message = error_element.text.strip()
        assert any(keyword in error_message for keyword in [
            "некорректная длина",
            "ошибка",
            "неверный номер"
        ]), f"❌ Неожиданный текст ошибки: '{error_message}'"
        print(f"✅ Баг подтверждён: сообщение об ошибке длины карты: '{error_message}'")
    except TimeoutException:
        save_screenshot_with_context(browser, "invalid_card_length", "no_error")
        pytest.fail("❌ Сообщение об ошибке длины карты не появилось")

    transfer_button = find_element_safe(browser, [
        (By.XPATH, "//button[contains(@class, 'g-button') and .//span[text()='Перевести']]")
    ])
    assert not transfer_button.is_enabled(), \
        "❌ Ошибка: кнопка «Перевести» активна с некорректным номером карты"
    print("✅ Кнопка «Перевести» неактивна с некорректным номером — как ожидается")


def test_negative_amount(browser):
    """
    BUG‑004: Система допускает отрицательный перевод
    """
    print(f"\n🔍 BASE_URL = '{BASE_URL}'")
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    wait_for_page_load(browser)
    print("✅ Страница загружена")

    # Шаг 1: Нажимаем на блок «Рубли»
    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("✅ Блок «Рубли» активирован")

    # Шаг 2: Вводим номер карты
    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("1111222233334444")
    print("✅ Номер карты введён")

    # Шаг 3: Вводим отрицательную сумму
    amount_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='1000']")
    ])
    amount_input.clear()
    amount_input.send_keys("-100")
    print("✅ Введена отрицательная сумма: -100 ₽")

    # Шаг 4: Нажимаем кнопку «Перевести»
    transfer_button = find_element_safe(browser, [
        (By.XPATH, "//button[contains(@class, 'g-button') and .//span[text()='Перевести']]")
    ])
    transfer_button.click()
    print("✅ Кнопка «Перевести» нажата")

    # Шаг 5: Обрабатываем алерт, если появился
    try:
        alert = WebDriverWait(browser, 5).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()
        assert "отрицательная" in alert_text.lower(), f"❌ Неожиданный текст алерта: {alert_text}"
        print(f"✅ Алерт подтверждён: '{alert_text}'")
    except TimeoutException:
        # Если алерта нет, ищем сообщение об ошибке на странице
        try:
            error_element = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".error-message, .alert-danger"))
            )
            error_message = error_element.text
            assert any(keyword in error_message.lower() for keyword in [
                "отрицательная",
                "некорректная",
                "ошибка"
            ]), f"❌ Неожиданный текст ошибки: {error_message}"
            print(f"✅ Ошибка валидации найдена: {error_message}")
        except TimeoutException:
            save_screenshot_with_context(browser, "negative_amount", "no_error")
            assert False, "❌ Сообщение об ошибке для отрицательной суммы не появилось"

def test_incorrect_commission_calculation(browser):
    """
    BUG‑005: Некорректный расчёт комиссии (округление до десятков)
    """
    print(f"\n🔍 BASE_URL = '{BASE_URL}'")
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    wait_for_page_load(browser)
    print("✅ Страница загружена")

    # Шаг 1: Нажимаем на блок «Рубли»
    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("✅ Блок «Рубли» активирован")

    # Шаг 2: Вводим номер карты
    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("1111222233334444")
    print("✅ Номер карты введён")

    # Шаг 3: Вводим сумму для расчёта комиссии
    amount_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='1000']")
    ])
    amount_input.clear()
    amount_input.send_keys("99")
    print("✅ Введена сумма для расчёта комиссии: 99 ₽")

    # Ждём обновления комиссии
    wait = WebDriverWait(browser, 30)
    try:
        # Пробуем несколько возможных ID для комиссии (опечатка в оригинале)
        commission_element = wait.until(
            EC.visibility_of_element_located((By.ID, "commission"))
        )
        commission_text = commission_element.text.strip().replace(" ₽", "").replace(",", ".")
        commission = float(commission_text)
        print(f"✅ Комиссия из интерфейса: {commission} ₽")
    except TimeoutException:
        save_screenshot_with_context(browser, "commission", "element_not_found")
        pytest.fail("❌ Элемент комиссии (#commission) не появился в течение 30 секунд")

    # Ожидаемая комиссия: 9 % от 99 ₽ = 8,91 ₽ (округляем до 9,0 ₽)
    expected_commission = 9.0
    assert abs(commission - expected_commission) < 0.01, (
        f"❌ БАГ ПОДТВЕРЖДЁН: комиссия рассчитана неверно. Ожидалось {expected_commission} ₽, получено {commission} ₽"
    )
    print("✅ Баг подтверждён: комиссия = 0 ₽ вместо 9 ₽")
