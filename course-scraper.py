import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

driver = webdriver.Chrome()
parse = False

def main():
    page = 0
    try:
        # Navigate to the initial page
        url = 'https://www.mastersportal.com/rankings/4/best-global-universities-rankings-us-news-world-report.html'
        driver.get(url)

        while True:
            # Wait for the page to load and locate the data elements
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button')))

            # Get the page source after the dynamic content has loaded
            page_source = driver.page_source
            page += 1

            time.sleep(5)  
            seeCollege(page_source, page) # Get the list of colleges from each page

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract the data you need using BeautifulSoup
            data_elements = soup.select('button')
            for item in data_elements:
                print(item.text)

            # Find the "Next" button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'button.NextPage.TextNav')
                next_button.click()

                # Wait for the new page to load (adjust this as necessary for your use case)
                WebDriverWait(driver, 10).until(EC.staleness_of(next_button))
                time.sleep(2)  # Additional wait time if necessary
            except:
                print("No more pages or unable to find the 'Next' button.")
                break
    finally:
        driver.quit()

def seeCollege(src, page):
    doc = BeautifulSoup(src, 'html.parser')
    #print(doc)
    s = doc.find('tbody', class_='ZebraStyle')
    rows = s.find_all(lambda tag: tag.name=='tr' and tag.get('data-id')==str(page))
    #print(rows)
    for row in rows:
        td = row.find('td')
        if td:
            a = td.find('a')
            if a:
                href = a.get('href')
                print(f"href: {href}")
                scrapeUniv(href)

def scrapeUniv(url):
    try:
        courses = []
        content = fetchData(url)
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.find('div', {'class': 'OrganisationTitle'}).text
        divs = soup.findAll('div', {'class': 'FoldContent Hidden'})

        for course in divs:
            a = course.findAll('a')
            for p in a:
                courses.append(p.get('title'))
        print(courses)
        addToJSON(title, courses)
    except:
        print("Exception occurred, skipping university")

def fetchData(url):
    tempDriver = webdriver.Chrome()
    tempDriver.get(url)
    return tempDriver.page_source

def addToJSON(title, courses):
    with open('courses.json', 'r') as file:
        data = json.load(file)
        newEntry={
            'University': title,
            'Masters' : courses
        }
        data.append(newEntry)
    with open('courses.json', 'w') as file:
        json.dump(data, file, indent=4)
    #print(json.dumps(data, indent=4))


main()

