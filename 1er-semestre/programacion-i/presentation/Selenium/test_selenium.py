from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')

try:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.google.com")
    print(f"✅ Selenium funciona! Título: {driver.title}")
    driver.quit()
except Exception as e:
    print(f"❌ Error: {e}")