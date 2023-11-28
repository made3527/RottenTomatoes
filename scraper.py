# Load libraries
import json, datetime, time, os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Download and install the Chrome driver
chrome_service = ChromeService(ChromeDriverManager().install())

# Set up options to run the driver in "headless" mode (no window) and with minimal logging
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--log-level=3")

# Record the current time
current_timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

# Hard-code in the URL we want
# TODO: Soften this so we can get the information about any movie
movie_url = 'https://www.rottentomatoes.com/m/the_marvels'

def rotten_tomatoes_soup(url):
    """
    A function for retrieving a website and converting its content into BeautifulSoup.

    Takes `url` as a string and returns a Soup object.
    """
    # Launch the driver
    driver = webdriver.Chrome(options = chrome_options, service=chrome_service)
    
    # Make the request
    driver.get(url)

    # Wait a few seconds for the page to load completely
    time.sleep(3)
    
    # Get source
    raw = driver.page_source.encode('utf-8')
    
    # Convert to Soup
    soup = BeautifulSoup(raw,features='html.parser')
    
    # Quit the driver
    driver.quit()

    return soup

def parse_data(soup,tag,ts):
    """
    A function for converting parsing the Soup of a Rotten Tomatoes page into a dictionary.

      soup - A BeautifulSoup object, typically created by `rotten_tomatoes_soup`
      tag - A string identifying a tag to be searched in the Soup
      ts - A string with the ISO-8601 timestamp

    Returns a dictionary with "timestamp", "average_rating", "liked_count", "not_liked_count",
      "rating_count", "review_count", and "value" keys.
    """
    details = soup.find(tag)
    
    details_d = {}
    details_d['timestamp'] = ts
    details_d['average_rating'] = float(details['averagerating'])
    details_d['liked_count'] = int(details['likedcount'])
    details_d['not_liked_count'] = int(details['notlikedcount'])
    details_d['rating_count'] = int(details['ratingcount'])
    details_d['review_count'] = int(details['reviewcount'])
    details_d['value'] = int(details['value'])

    return details_d

def update_data(filename,data):
    """
    A function for appending a dictionary to a list of dictionaries in a JSON file.

      filename - The name of the file to create/update
      data - The dictionary to be appended to the file
    """
    if filename in os.listdir():

        with open(filename,'r',encoding='utf-8') as f:
            data_list = json.load(f)

        data_list.append(data)

        with open(filename,'w',encoding='utf-8') as f:
            json.dump(data_list,f)

    else:
        with open(filename,'w',encoding='utf-8') as f:
            json.dump([data],f)


def main():
    """
    Retrieve the content from the page, parse the data into critics and audience responses,
      and create/update the JSON files for critics and audience.
    """
    soup = rotten_tomatoes_soup(movie_url)
    critics_data = parse_data(soup=soup,tag='score-details-critics-deprecated',ts=current_timestamp)
    audience_data = parse_data(soup=soup,tag='score-details-audience-deprecated',ts=current_timestamp)
    
    update_data('critics.json',critics_data)
    update_data('audience.json',audience_data)

if __name__ == "__main__":
    main()