import pytest
from conftest import browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_successful_transfer_1000(browser):
    """
    Успешный перевод 1 000 ₽ на корректную карту
    """
    browser.get("http://localhost:8000/?balance=30000&reserved=20001")

    # Нажимаем на блок «Рубли»
    rubles_block = browser.find_element("css", ".account-block[data-currency='RUB']")
    rubles_block.click()


    # Вводим корректный номер карты
    card_input = browser.find_element("id", "card_number")
    card_input.send_keys("1111222233334444")

    # Вводим сумму перевода
    amount_input = browser.find_element("id", "amount")
    amount_input.clear()
    amount_input.send_keys("1000")

    # Нажимаем кнопку «Перевести»
    transfer_button = browser.find_element("id", "transfer_button")
    transfer_button.click()

    # Ждём и проверяем сообщение об успешном переводе
    wait = WebDriverWait(browser, 5)
    try:
        success_message = wait.until(
            EC.visibility_of_element_located(("css", ".success-message"))
        ).text
        assert "Перевод выполнен успешно" in success_message, "Ошибка: нет сообщения об успешном переводе"
    except:
        pytest.fail("Ошибка: сообщение об успешном переводе не появилось")


def test_commission_calculation_correct(browser):
    """
    Корректный расчёт комиссии (10 % от суммы)
    """
    browser.get("http://localhost:8000/?balance=30000&reserved=20001")

    rubles_block = browser.find_element("css", ".account-block[data-currency='RUB']")
    rubles_block.click()

    card_input = browser.find_element("id", "card_number")
    card_input.send_keys("1111222233334444")

    amount_input = browser.find_element("id", "amount")
    amount_input.clear()
    amount_input.send_keys("500")

    # Ждём появления элемента с комиссией
    wait = WebDriverWait(browser, 5)
    try:
        commission_element = wait.until(
            EC.visibility_of_element_located(("id", "commission"))
        )
        commission = float(commission_element.text.replace(" ₽", ""))

        expected_commission = 50.0  # 10 % от 500 ₽
        assert abs(commission - expected_commission) < 0.01, \
            f"Ошибка: комиссия рассчитана неверно. Ожидалось {expected_commission} ₽, получено {commission} ₽"
    except:
        pytest.fail("Ошибка: элемент с комиссией не появился")

def test_transfer_maximum_available_amount(browser):
    """
    TC‑007: Перевод суммы, равной максимальной доступной
    """
    browser.get("http://localhost:8000/?balance=30000&reserved=20001")

    rubles_block = browser.find_element("css", ".account-block[data-currency='RUB']")
    rubles_block.click()

    card_input = browser.find_element("id", "card_number")
    card_input.send_keys("1111222233334444")

    amount_input = browser.find_element("id", "amount")
    amount_input.clear()
    amount_input.send_keys("9999")  # Максимальная доступная сумма

    # Проверяем расчёт комиссии
    wait = WebDriverWait(browser, 5)
    commission_element = wait.until(
        EC.visibility_of_element_located(("id", "commission"))
    )
    commission = float(commission_element.text.replace(" ₽", ""))
    expected_commission = 999.0  # 10 % от 9 999 ₽

    assert abs(commission - expected_commission) < 0.01, \
        f"Ошибка: комиссия рассчитана неверно. Ожидалось {expected_commission} ₽, получено {commission} ₽"


    # Нажимаем кнопку «Перевести»
    transfer_button = browser.find_element("id", "transfer_button")
    transfer_button.click()

    # Проверяем успешное завершение
    success_message = wait.until(
        EC.visibility_of_element_located(("css", ".success-message"))
    ).text
    assert "Перевод выполнен успешно" in success_message

def test_attempt_transfer_over_limit(browser):
    """
    TC‑008: Попытка перевода сверх доступной суммы
    """
    browser.get("http://localhost:8000/?balance=30000&reserved=20001")

    rubles_block = browser.find_element("css", ".account-block[data-currency='RUB']")
    rubles_block.click()

    card_input = browser.find_element("id", "card_number")
    card_input.send_keys("1111222233334444")

    amount_input = browser.find_element("id", "amount")
    amount_input.clear()
    amount_input.send_keys("10000")  # Превышает доступную сумму

    transfer_button = browser.find_element("id", "transfer_button")

    # Проверяем, что кнопка неактивна
    assert not transfer_button.is_enabled(), "Ошибка: кнопка «Перевести» активна при превышении лимита"

    if transfer_button.is_enabled():
        transfer_button.click()
        error_message = browser.find_element("css", ".error-message").text
        assert "Недостаточно средств" in error_message, "Ошибка: нет сообщения о недостатке средств"

def test_valid_card_number_validation(browser):
    """
    TC‑009: Валидация корректного 16‑значного номера карты
    """
    browser.get("http://localhost:8000/?balance=30000&reserved=20001")

    rubles_block = browser.find_element("css", ".account-block[data-currency='RUB']")
    rubles_block.click()

    card_input = browser.find_element("id", "card_number")
    card_input.send_keys("1111222233334444")


    # Проверяем отсутствие ошибок валидации
    try:
        error_element = browser.find_element("css", ".card-error")
        assert False, "Ошибка: появилось сообщение об ошибке валидации карты"
    except:
        pass  # Ошибок нет — это ожидаемое поведение

    # Проверяем активность кнопки перевода
    transfer_button = browser.find_element("id", "transfer_button")
    assert transfer_button.is_enabled(), "Ошибка: кнопка «Перевести» неактивна с корректным номером карты"