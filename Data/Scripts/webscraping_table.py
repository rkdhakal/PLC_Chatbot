from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from selenium.webdriver.chrome.options import Options
import time

# Configure Chrome options
chrome_options = Options()

# Specify path to chromedriver using Service
service = Service(executable_path='D:/chromedriver-win64/chromedriver-win64/chromedriver.exe')

# Initialize driver with both service and options
driver = webdriver.Chrome(service=service, options=chrome_options)

# Now you can navigate
driver.get('https://support.industry.siemens.com/cs/mdm/109742272?c=85937913867&lc=en-CA')

try:
    # Use a more general XPath to locate the table body
    table_body = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div/div[1]/div[1]/div[1]/div[3]/div/div[2]/div[4]/div/div/div[2]/div[2]/table/tbody'))
    )
    
    table_rows = table_body.find_elements(By.TAG_NAME, "tr")
    print(f"Found {len(table_rows)} rows in the table.")

    # Open the CSV file with utf-8 encoding and newline="" for proper CSV formatting
    with open("siemens_error_codes.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for row in table_rows:
            table_data = row.find_elements(By.CSS_SELECTOR, "td,th")
            row_data = [data.text for data in table_data]
            writer.writerow(row_data)

except Exception as e:
    print("An error occurred while scraping:", e)
finally:
    driver.quit()
