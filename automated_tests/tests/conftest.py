import pytest
import os
from selenium import webdriver
from selenium.webdriver.edge.options import Options

BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def browser():
    edge_options = Options()
    edge_options.add_argument("--headless")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--disable-gpu") 
    
    driver = webdriver.Edge(options=edge_options)
    yield driver
    driver.quit()
