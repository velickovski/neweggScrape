import time
from selenium import webdriver
from bs4 import BeautifulSoup
import csv

base_url = "https://www.newegg.com/p/pl?N=100006676&page="
page = 1
products = []

# Function to open second browser to prevent Captcha
def get_description_and_seller(itemURL):
    driver = webdriver.Chrome()
    driver.get(itemURL)
    # time.sleep(5) If needed for smaller number of products
    product_page_source = driver.page_source
    soup = BeautifulSoup(product_page_source, 'html.parser')

    description = soup.find('div', class_='product-bullets').text.strip()

    #Strong feature inside of a div may not be available (depending od time.sleep(x) period)
    seller_tag = soup.find('div', class_='product-seller-sold-by')
    if seller_tag:
        strong_tag = seller_tag.find('strong')
        seller = strong_tag.text.strip() if strong_tag else "No seller info"
    else:
        seller = "No seller info"

    driver.quit()
    return description, seller


def scrape_page(page_url):
    driver = webdriver.Chrome()
    driver.get(page_url)
    # time.sleep(5) If needed for smaller number of products
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    product_list = soup.find_all('div', class_='item-cell')

    for product in product_list:
        if len(products) >= 5:
            break

        product_data = {}
        
        product_link = product.find('a', class_='item-title')['href']
        description, seller = get_description_and_seller(product_link)

        product_data['title'] = product.find('a', class_='item-title').text.strip()
        product_data['description'] = description
        product_data['seller'] = seller
        product_data['price'] = product.find('li', class_='price-current').text.strip().split('\u00a0')[0]
        product_data['rating'] = product.find('a', class_='item-rating')['title'].replace("Rating +", "").strip()
        product_data['image_url'] = product.find('img')['src']

        print(product_data)
        products.append(product_data)

    driver.quit()

while len(products) < 5:
    scrape_page(base_url + str(page))
    page += 1

csv_file = "products.csv"
csv_columns = ['title', 'description', 'price', 'rating', 'seller', 'image_url']

with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for product in products[:5]:
        writer.writerow(product)

print("Scraping successful")

#For testing features and precision on this application do these steps:
# 1. Lower the number of len(products) to be around 5 to 20 products
# 2. row 74 - products[:5-20?]
# 3. driver = webdriver.Chrome() -> for Windows users it may appears as an error because it requires path to the the Chrome bin start, on Linux it only requires Chrome installed