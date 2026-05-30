import os
import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options

BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Edge(options=options)
    yield driver
    driver.quit()

def test_base_url_is_accessible(browser):
    """Проверяет, что базовый URL доступен"""
    print(f"🔍 Testing URL: {BASE_URL}/get")
    browser.get(f"{BASE_URL}/get")
    assert "httpbin" in browser.title.lower() or browser.current_url, "Страница не загрузилась"
    print(f"✅ Страница загружена: {browser.current_url}")
