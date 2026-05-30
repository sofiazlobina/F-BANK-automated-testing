import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options

@pytest.fixture(scope="session")
def browser():
    edge_options = Options()
    edge_options.add_argument("--headless")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Edge(options=edge_options)
    yield driver
    driver.quit()
