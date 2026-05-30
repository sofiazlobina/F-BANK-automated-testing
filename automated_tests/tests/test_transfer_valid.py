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

# 🔽 Импортируем BASE_URL из conftest.py (вместо локального определения)
from .conftest import BASE_URL

# Константы для тестирования
VALID_CARD = "1111222233334444"
# 🔽 Удалено: BASE_URL = "http://localhost:8000/..." — теперь импортируется из conftest
COMMISSION_RATE = 0.1  # 10 %

def save_screenshot_with_context(browser, test_name, context=""):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/{test_name}_{context}_{timestamp}.png"
    os.makedirs("screenshots", exist_ok=True)
    browser.save_screenshot(filename)
    logging.info(f"Скриншот сохранён: {filename}")
    return filename

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
    pytest.fail(f"Ни один из селекторов не сработал: {locators}")

def test_valid_card_number_validation(browser):
    """
    TC‑009: Валидация корректного 16‑значного номера карты
    """
    # 🔽 Заменено: localhost → BASE_URL
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    print("Страница загружена")

    # Шаг 1: Нажимаем на блок «Рубли»
    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("Блок «Рубли» активирован")

    # Шаг 2: Вводим корректный номер карты
    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("1111222233334444")
    print("Введён корректный 16‑значный номер карты")

    # Шаг 3: Проверяем отсутствие ошибок валидации
    try:
        error_element = WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//span[contains(@style, 'color: red')]"
            ))
        )
        error_message = error_element.text.strip()
        assert False, f"Ошибка: появилось сообщение об ошибке валидации: '{error_message}'"
    except TimeoutException:
        print("✓ Ошибок валидации нет — номер карты корректен")

    # Шаг 4: Проверяем активность кнопки перевода
    transfer_button = find_element_safe(browser, [
        (By.XPATH, "//button[contains(@class, 'g-button') and .//span[text()='Перевести']]")
    ])
    assert transfer_button.is_enabled(), "Ошибка: кнопка «Перевести» неактивна с корректным номером карты"
    print("Кнопка «Перевести» активна — тест пройден")


def test_transfer_maximum_available_amount(browser):
    """
    TC‑007: Перевод суммы, равной максимальной доступной
    """
    # 🔽 Заменено: localhost → BASE_URL
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    print("Страница загружена")

    # Шаг 1: Нажимаем на блок «Рубли»
    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("Блок «Рубли» активирован")

    # Шаг 2: Вводим номер карты
    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("1111222233334444")
    print("Номер карты введён")

    # Шаг 3: Вводим максимальную доступную сумму
    amount_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='1000']")
    ])
    amount_input.clear()
    amount_input.send_keys("9999")  # Максимальная доступная сумма
    print("Введена максимальная сумма: 9 999 ₽")

    # Шаг 4: Проверяем расчёт комиссии
    wait = WebDriverWait(browser, 30)
    try:
        commission_element = wait.until(
            EC.visibility_of_element_located((By.ID, "commission"))
        )
        commission_text = commission_element.text.replace(" ₽", "").strip()
        commission = float(commission_text)
        print(f"Комиссия из интерфейса: {commission} ₽")
    except TimeoutException:
        browser.save_screenshot("commission_element_not_found.png")
        pytest.fail("Элемент комиссии (#commission) не появился в течение 30 секунд")

    expected_commission = 999.0  # 10 % от 9 999 ₽
    assert abs(commission - expected_commission) < 0.01, (
        f"Ошибка: комиссия рассчитана неверно. Ожидалось {expected_commission} ₽, получено {commission} ₽"
    )
    print("Комиссия рассчитана корректно")

    # Шаг 5: Нажимаем кнопку «Перевести»
    transfer_button = find_element_safe(browser, [
        (By.XPATH, "//button[contains(@class, 'g-button') and .//span[text()='Перевести']]")
    ])
    transfer_button.click()
    print("Кнопка «Перевести» нажата")

    # Шаг 6: Проверяем успешное завершение
    try:
        success_message = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".success-message"))
        ).text
        assert "Перевод выполнен успешно" in success_message, "Ошибка: нет сообщения об успешном переводе"
        print(f"✓ Успешное сообщение: {success_message}")
    except TimeoutException:
        save_screenshot_with_context(browser, "transfer_max_amount", "no_success_message")
        pytest.fail("Сообщение об успешном переводе не появилось")

def test_attempt_transfer_over_limit(browser):
    """
    TC‑008: Попытка перевода сверх доступной суммы
    """
    # 🔽 Заменено: localhost → BASE_URL
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    print("Страница загружена")

    # Шаг 1: Нажимаем на блок «Рубли»
    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("Блок «Рубли» активирован")

    # Шаг 2: Вводим номер карты
    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("1111222233334444")
    print("Номер карты введён")

    # Шаг 3: Вводим сумму, превышающую доступный лимит
    amount_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='1000']")
    ])
    amount_input.clear()
    amount_input.send_keys("10000")  # Превышает доступную сумму
    print("Введена сумма, превышающая лимит: 10 000 ₽")

    # Шаг 4: Проверяем, что кнопка неактивна
    transfer_button = find_element_safe(browser, [
        (By.XPATH, "//button[contains(@class, 'g-button') and .//span[text()='Перевести']]")
    ])
    assert not transfer_button.is_enabled(), "Ошибка: кнопка «Перевести» активна при превышении лимита"
    print("Кнопка «Перевести» неактивна — как ожидается")

    if transfer_button.is_enabled():
        transfer_button.click()
        # Шаг 5: Проверяем сообщение об ошибке
        try:
            error_element = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".error-message, .alert-danger"))
            )
            error_message = error_element.text
            assert "Недостаточно средств" in error_message, f"Ошибка: нет сообщения о недостатке средств. Получено: '{error_message}'"
            print(f"✓ Сообщение об ошибке: {error_message}")
        except TimeoutException:
            save_screenshot_with_context(browser, "transfer_over_limit", "no_error_message")
            pytest.fail("Сообщение об ошибке не появилось")
    else:
        print("Тест пройден: кнопка неактивна при превышении лимита")

def test_invalid_card_number_length_validation(browser):
    """
    TC‑009: Валидация номера карты с некорректной длиной
    """
    # 🔽 Заменено: localhost → BASE_URL
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    print("Страница загружена")

    # Шаг 1: Нажимаем на блок «Рубли»
    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("Блок «Рубли» активирован")

    # Шаг 2: Вводим номер карты длиной 15 символов (некорректный)
    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("111122223333444")  # 15 цифр вместо 16
    print("Введён номер карты некорректной длины (15 цифр)")

    # Шаг 3: Проверяем появление сообщения об ошибке валидации
    try:
        error_element = WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//span[contains(@style, 'color: red')]"
            ))
        )
        error_message = error_element.text.strip()
        assert any(keyword in error_message.lower() for keyword in [
            "некорректная длина",
            "ошибка",
            "неверный номер",
            "16 цифр"
        ]), f"Неожиданный текст ошибки: '{error_message}'"
        print(f"✓ Сообщение об ошибке валидации: '{error_message}'")
    except TimeoutException:
        save_screenshot_with_context(browser, "invalid_card_length", "no_error")
        pytest.fail("Сообщение об ошибке валидации не появилось")

    # Шаг 4: Проверяем, что кнопка перевода неактивна
    transfer_button = find_element_safe(browser, [
        (By.XPATH, "//button[contains(@class, 'g-button') and .//span[text()='Перевести']]")
    ])
    assert not transfer_button.is_enabled(), \
        "Ошибка: кнопка «Перевести» активна при некорректном номере карты"
    print("Кнопка «Перевести» неактивна с некорректным номером — тест пройден")

def test_empty_amount_transfer_validation(browser):
    """
    TC‑010: Проверка обработки пустой суммы перевода
    """
    # 🔽 Заменено: localhost → BASE_URL
    browser.get(f"{BASE_URL}/?balance=30000&reserved=20001")
    print("Страница загружена")

    # Шаг 1: Нажимаем на блок «Рубли»
    rubles_block = find_element_safe(browser, [
        (By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
    ])
    rubles_block.click()
    print("Блок «Рубли» активирован")

    # Шаг 2: Вводим номер карты
    card_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    ])
    card_input.clear()
    card_input.send_keys("1111222233334444")
    print("Номер карты введён")

    # Шаг 3: Очищаем поле суммы (оставляем пустым)
    amount_input = find_element_safe(browser, [
        (By.XPATH, "//input[@placeholder='1000']")
    ])
    amount_input.clear()
    print("Поле суммы очищено")

    # Шаг 4: Проверяем, что кнопка перевода неактивна
    transfer_button = find_element_safe(browser, [
        (By.XPATH, "//button[contains(@class, 'g-button') and .//span[text()='Перевести']]")
    ])
    assert not transfer_button.is_enabled(), \
        "Ошибка: кнопка «Перевести» активна при пустой сумме"
    print("Кнопка «Перевести» неактивна при пустом поле суммы — как ожидается")

    # Шаг 5: Вводим пробел вместо суммы
    amount_input.send_keys(" ")
    print("Введён пробел в поле суммы")

    # Шаг 6: Проверяем сообщение об ошибке для пустой/некорректной суммы
    try:
        error_element = WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".amount-error, .error-message"))
        )
        error_message = error_element.text
        assert any(keyword in error_message.lower() for keyword in [
            "сумма перевода не может быть пустой",
            "введите сумму перевода",
            "ошибка суммы",
            "некорректная сумма"
        ]), f"Неожиданный текст ошибки: '{error_message}'"
        print(f"✓ Сообщение об ошибке: '{error_message}'")
    except TimeoutException:
        save_screenshot_with_context(browser, "empty_amount", "no_error_message")
        pytest.fail("Сообщение об ошибке для пустой суммы не появилось")

    # Шаг 7: Проверяем, что комиссия не рассчитывается для пустой суммы
    try:
        commission_element = browser.find_element(By.ID, "commission")
        commission_text = commission_element.text.replace(" ₽", "").strip()
        # Если элемент комиссии есть, он должен показывать 0 ₽ или быть пустым
        if commission_text:
            commission = float(commission_text)
            assert commission == 0.0, \
                f"Ошибка: комиссия рассчитывается для пустой суммы: {commission} ₽"
    except NoSuchElementException:
        pass  # Элемент комиссии отсутствует — это ожидаемое поведение

    print("Тест пройден: система корректно обрабатывает пустую сумму перевода")
