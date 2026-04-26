import pytest
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

@pytest.fixture(scope="session")
def browser():
    # Опции для Edge (если нужно указать путь к браузеру)
    edge_options = Options()
    service = Service("C:\\Users\\ru-szlobina\\Desktop\\Личное\\F-Bank\\msedgedriver.exe")

    driver = webdriver.Edge(service=service, options=edge_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
