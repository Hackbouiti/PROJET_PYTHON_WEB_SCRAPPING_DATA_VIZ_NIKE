import time
import json
import os
from rich import print
from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
from dataclasses import dataclass, field

# liens pour les différentes catégories
categories = {
    "Men Lifestyle": 'https://www.nike.com/fr/w/hommes-lifestyle-chaussures-13jrmznik1zy7ok',
    "Men Jordan": 'https://www.nike.com/fr/w/hommes-jordan-chaussures-37eefznik1zy7ok',
    "Men Running": 'https://www.nike.com/fr/w/hommes-running-chaussures-37v7jznik1zy7ok',
    "Men Football": 'https://www.nike.com/fr/w/hommes-football-chaussures-1gdj0znik1zy7ok',
    "Men Training et Fitness": 'https://www.nike.com/fr/w/hommes-training-chaussures-58jtoznik1zy7ok',
    "Men Basketball" : "https://www.nike.com/fr/w/hommes-basketball-chaussures-3glsmznik1zy7ok",
    "Men skateboard" : "https://www.nike.com/fr/w/hommes-skateboard-chaussures-8mfrfznik1zy7ok",
    "Women Lifestyle": 'https://www.nike.com/fr/w/femmes-lifestyle-chaussures-13jrmz5e1x6zy7ok',
    "Women Jordan": 'https://www.nike.com/fr/w/femmes-jordan-chaussures-37eefz5e1x6zy7ok',
    "Women Running": 'https://www.nike.com/fr/w/femmes-running-chaussures-37v7jz5e1x6zy7ok',
    "Women Football": 'https://www.nike.com/fr/w/femmes-football-chaussures-1gdj0z5e1x6zy7ok',
    "Women Training et Fitness": 'https://www.nike.com/fr/w/femmes-training-chaussures-58jtoz5e1x6zy7ok'
}

extracted_data_object = []
data_file_template = 'Data/Nike_Shoes_{category}.json'

def save_data(category):
    # Code pour s'assurer que le chemin d'accès existe
    os.makedirs(os.path.dirname(data_file_template.format(category=category)), exist_ok=True)

    json_object = json.dumps([item.__dict__ for item in extracted_data_object], indent=4)

    with open(data_file_template.format(category=category), 'w') as outfile:
        outfile.write(json_object)

@dataclass
class DataRaw:
    title: str
    color_num: str = field(default="")
    price: str = field(default="")
    url: str = field(default="")
    image_url: str = field(default="")  # Nouveau champ pour le lien de l'image

def parse_data(node):
    raw = DataRaw(
        title=node.css_first('div.product-card__title').text(),
        color_num=node.css_first('div.product-card__product-count').text().split(" ")[0],
        url=node.css_first('a').attributes['href'],
        image_url=node.css_first('img.product-card__hero-image').attributes['src']  # Extraction de l'URL de l'image
    )

    try:
        raw.price = node.css_first('div.product-price.is--current-price').text() or node.css_first('div.product-price.fr__styling.is--current-price').text()
    except:
        raw.price = "Prix non disponible"

    extracted_data_object.append(raw)
    print(raw)

def get_data(category, url):  

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=False, slow_mo=50)
            page = browser.new_page()
            page.goto(url, timeout=720000)

            time.sleep(4)

            # Automatise le clique sur le bouton "accepter les cookies" s'il existe
            try:
                if page.is_visible('span#hf_cookie_text_cookieAccept'):
                    page.click('span#hf_cookie_text_cookieAccept')
                    print("Cookie accept button clicked.")
                else:
                    print("Cookie accept button not present.")
            except Exception as e:
                print("Error handling cookie accept button:", e)

            for x in range(1, 50):
                page.keyboard.press('End')
                time.sleep(2)
                # Vérifie si du nouveau contenu est chargé
                if len(page.content()) == len(page.content()):
                    print("No new content loaded, moving to next category.")
                    break

            # Data slicing
            html = page.inner_html('div#skip-to-products')

            tree = HTMLParser(html)

            nodes = tree.css('div.product-card__body')

            if not nodes:
                print(f"No data found for category {category}. Moving to next.")
                return

            for i in range(len(nodes)):
                print(i)
                parse_data(nodes[i])

            print(f"Category '{category}': {len(nodes)} products found.")

        except Exception as e:
            print(f"Error scraping category '{category}': {e}")
        finally:
            browser.close()

for category, url in categories.items():
    print(f"Scraping category: {category}")
    extracted_data_object = []  # Reset data for each category
    get_data(category, url)
    save_data(category)
    print(f"Finished scraping category: {category}")
