import time
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import concurrent.futures

base_url = "https://www.newegg.com/p/pl?N=100006676&page="
products = []
MAX_THREADS = 10

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
    page_products = []

    for product in product_list:
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
        page_products.append(product_data)

    driver.quit()
    return page_products


def process_page(page):
    return scrape_page(base_url + str(page))


def scrape_all_pages():
    page = 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        while len(products) < 500:
            futures.append(executor.submit(process_page, page))
            page += 1

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if len(products) < 500:
                products.extend(result)
            if len(products) >= 500:
                break

#Ne runnuvaj ako nemash kofniguracija koja bi mozela da izdrzhu 10 threads (za start), 100 threads (najneoptimalno)
scrape_all_pages()

csv_file = "products.csv"
csv_columns = ['title', 'description', 'price', 'rating', 'seller', 'image_url']

with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for product in products[:500]:
        writer.writerow(product)
