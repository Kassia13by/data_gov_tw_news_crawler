from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

if __name__ == '__main__':
    # Set up the Chrome WebDriver using Service
    chrome_driver_path = 'YOUR CHORME WEBDRIVER PATH'
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    # Open the target website
    driver.get("https://data.gov.tw/en/news")

    # Set up WebDriverWait for handling page loading
    wait = WebDriverWait(driver, 10)

    # List to store the collected news meta data
    news_data = []

    while True:
        try:
            # Wait for the news table to load
            wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__nuxt"]/div/div/main/div[2]/section/div[1]/div[1]/div[3]/div/div[1]/div/table/tbody/tr')))
            
            # Get all news rows on the page
            news_rows = driver.find_elements(By.XPATH, '//*[@id="__nuxt"]/div/div/main/div[2]/section/div[1]/div[1]/div[3]/div/div[1]/div/table/tbody/tr')
            
            # Extract publish date, title, and href for each news item
            for row in news_rows:
                publish_date = row.find_element(By.XPATH, './td[1]/div').text
                title = row.find_element(By.XPATH, './td[2]/div/a').text
                href = row.find_element(By.XPATH, './td[2]/div/a').get_attribute('href')

                # Append news data to the list
                news_data.append({
                    "publish_date": publish_date,
                    "title": title,
                    "href": href
                })
            
            print(f"Collected {len(news_rows)} news items from current page.")

            # Find and click the "Next Page" button
            next_page_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__nuxt"]/div/div[1]/main/div[2]/section/div[2]/button[2]')))
            next_page_button.click()

            # Wait for the next page to load
            time.sleep(5) # Set the suitable time by yourself
        
        except Exception as e:
            # Handle when the "Next Page" button is not clickable or the last page is reached
            print(f"Reached the last page or encountered an error: {e}")
            break

    # Process the detailed news content
    news_data_dict = []
    for news in news_data:
        driver.get(news['href'])
        time.sleep(15)  # Wait for the page to load

        try:
            # Locate the main content of the news article
            main_content = driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div/div[1]/main/div[2]/article/section/div/div[2]/div[2]')
            
            # Extract all <p> elements inside the main content
            paragraphs = main_content.find_elements(By.TAG_NAME, 'p')
            content = []
            sources = set()  # To avoid duplicate sources

            for paragraph in paragraphs:
                text = paragraph.text.strip()

                if text:
                    # Check for source text and avoid duplicates
                    if "Source :" in text:
                        if text not in sources:
                            content.append(text)
                            sources.add(text)
                    else:
                        content.append(text)
            
            # Combine all paragraph texts into a single string
            full_content = "\n".join(content)

            # Store detailed news data in the dictionary
            news_data_dict.append({
                'publish_date': news['publish_date'],
                'title': news['title'],
                'href': news['href'],
                'content': full_content
            })

        except Exception as e:
            print(f"Error loading detailed content for {news['title']}: {e}")

    # Close the WebDriver once done
    driver.quit()

    # Save the collected data to a JSON file
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news_data_dict, f, ensure_ascii=False, indent=4)

    print(f"Data has been saved to 'news_data.json'. Total items collected: {len(news_data_dict)}")
