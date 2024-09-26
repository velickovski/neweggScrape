import time
from selenium import webdriver
from bs4 import BeautifulSoup
import csv

base_url = "https://www.newegg.com/p/pl?N=100006676&page="
page = 1
products = []

#Nova funkcija poradi problemi so Captcha
def get_description_and_seller(itemURL):
    driver = webdriver.Chrome()
    driver.get(itemURL)
    time.sleep(10)

    product_page_source = driver.page_source
    soup = BeautifulSoup(product_page_source, 'html.parser')

    description = soup.find('div', class_='product-bullets').text.strip()

    #Problemi so loadiranje na strana pa mora da se proveruva postepeno baranje na STRONG atribut "spor render na strana"
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
    time.sleep(5)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    product_list = soup.find_all('div', class_='item-cell')

    for product in product_list:
        if len(products) >= 500:
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

while len(products) < 500:
    scrape_page(base_url + str(page))
    page += 1

csv_file = "products.csv"
csv_columns = ['title', 'description', 'price', 'rating', 'seller', 'image_url']

with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for product in products[:500]:
        writer.writerow(product)

print("Scraping successful")

# Za testiranje na tocnost i preciznost na aplikacijata napravete gi slednite cekori:
# 1. namalete go brojot za len(products) da se dvizi pomegju 5 - 20
# 2. row 74 - products[:5-20?]
# 3. driver = webdriver.Chrome() -> dokolku koristite Windows mozebi bi imale potreba od stavanje na pateka kade se naogja Chrome instalacija, na Linux nema problem