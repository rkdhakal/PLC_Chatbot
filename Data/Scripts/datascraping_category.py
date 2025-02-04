from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from selenium.webdriver.chrome.options import Options

# Configure Chrome options
chrome_options = Options()

# Specify path to chromedriver using Service
service = Service(executable_path='D:/chromedriver-win64/chromedriver-win64/chromedriver.exe')

# Initialize driver with both service and options
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to the webpage
driver.get('https://support.industry.siemens.com/cs/mdm/109742272?c=85937913867&lc=en-CA')

try:
    # Locate the table body
    table_body = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div/div[1]/div[1]/div[1]/div[3]/div/div[2]/div[4]/div/div/div[2]/div[2]/table/tbody'))
    )
    
    table_rows = table_body.find_elements(By.TAG_NAME, "tr")
    print(f"Found {len(table_rows)} rows in the table.")

    # Open CSV file
    with open("siemens_error_codes.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header row
        writer.writerow(["Category", "Error Code", "Description", "Remedy"])

        current_category = ""  # Variable to hold the category name

        for row in table_rows:
            table_data = row.find_elements(By.CSS_SELECTOR, "td,th")
            row_texts = [data.text.strip() for data in table_data]

            # If a row has only one column, assume it's a category header
            if len(row_texts) == 1 and row_texts[0]: 
                current_category = row_texts[0]  # Update category
                continue  # Skip writing this row to CSV

            # If the row has enough columns, write it along with the current category
            if len(row_texts) >= 3:
                writer.writerow([current_category] + row_texts[:3])  # Append category before data

except Exception as e:
    print("An error occurred while scraping:", e)

finally:
    driver.quit()
