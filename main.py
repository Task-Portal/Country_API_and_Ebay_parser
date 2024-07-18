# https://www.work.ua/jobs/5733831/

# 1) Потрібно реалізувати клас який буде взаємодіяти зі стороннім API: API (https://restcountries.com)
# Клас повинен отримувати дані від API то повертати в консоль в табличній формі, а саме такі дані:
#     назва країни, назва столиці та посилання на зображення прапору в форматі png.
import re
from bs4 import BeautifulSoup
import requests
from texttable import Texttable
import json


class Country:
    def __init__(self, name) -> None:

        self.getCountryInfo(name)

    def getCountryInfo(self, name):
        data = requests.get(f"https://restcountries.com/v3.1/name/{name}")

        try:
            data.raise_for_status()
            if data.status_code == 200:
                data = json.loads(data.text)
                country_name = data[0]['name']['official']
                capital = data[0]['capital'][0]
                flag = data[0]['flags']['png']
                t = Texttable()
                t.add_rows([['Country_name', 'Capital', "Flag_png_url"], [
                           country_name, capital, flag], ])
                print(t.draw())
        except Exception as e:
            print("Exception: ", e)


# c = Country("Ukraine")

#  Потрібно створити клас який буде збирати дані за посиланням на Ebay сторінку товару,
#  формат даних в якому повинні повертатись дані json в тестовому завданні
#  можна просто виводити в консоль, або зберігати в файл.
#  Обов’язкові дані це назва, посилання на фото, саме посилання на товар, ціна,
#  продавець, ціна доставки.


class Ebay:
    def __init__(self, url) -> None:
        
        self.item = None
        self.soup = None
        self.url = url
        self.get_soup()
        if self.soup:
            self.get_item_info_by_url()

    def get_soup(self):
        try:
            page = requests.get(self.url)
            soup = BeautifulSoup(page.text, 'html.parser')
            self.soup = soup
        except Exception as e:
            print("Error: ", e)

    def get_item_info_by_url(self):

        price = self.soup.select_one('.x-price-primary span.ux-textspans').text
        name = self.soup.select_one("h1.x-item-title__mainTitle span").text
        # takes first picture to increase it 160>500 or more
        photo_url = self.soup.select_one("#PicturePanel img").attrs['src']
        seller = self.soup.select_one(
            ".x-sellercard-atf__info span.ux-textspans--BOLD").text
        self.item = {"name": name, "photo_url": photo_url,
                     "seller": seller, "item_url": self.url, "price": price}
        self.get_price()
        self.get_shipping_details()
        self.write_to_json_file()

    def get_price(self):
        label_html_elements = self.soup.select('.ux-labels-values__labels')

        for label_html_element in label_html_elements:

            if 'Shipping:' in label_html_element.text:

                shipping_price_html_element = label_html_element.next_sibling.select_one(
                    '.ux-textspans--BOLD')

                if shipping_price_html_element is not None:

                    shipping_price = re.findall(
                        "\d+[.,]\d+", shipping_price_html_element.text)[0]
                    self.item["shipping_price"] = shipping_price

                break

        # product detail scraping logic

        section_title_elements = self.soup.select('.section-title')

        for section_title_element in section_title_elements:

            if 'Item specifics' in section_title_element.text or 'About this product' in section_title_element.text:

                section_element = section_title_element.parent

                for section_col in section_element.select('.ux-layout-section-evo__col'):

                    print(section_col.text)

                    col_label = section_col.select_one(
                        '.ux-labels-values__labels')

                    col_value = section_col.select_one(
                        '.ux-labels-values__values')

                    if col_label is not None and col_value is not None:

                        self.item[col_label.text] = col_value.text

    def get_shipping_details(self):
        # shipping details
        section_shipping_elements = self.soup.select(
            ".ux-layout-section.ux-layout-section--shipping")
        for section_title_element in section_shipping_elements:
            text = section_title_element.text
            if text:
                index = text.find(":")
                label = text[0:index]
                description = text[index+1:]
                self.item[label] = description

    # export the scraped data to a JSON file

    def write_to_json_file(self):
        with open('product_info.json', 'w') as file:
            json.dump(self.item, file, indent=4)
        print(self.item)
        print("Done.")


Ebay("https://www.ebay.co.uk/itm/125547765972")
