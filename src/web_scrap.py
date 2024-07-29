import logging
import time


import pandas as pd
import requests
from bs4 import BeautifulSoup


class QuoteScraper:
    def __init__(self, base_url, start_page=1, end_page=None): #max_pages=None):
        self.base_url = base_url
        self.quotes_data = []
        self.authors_data = {}
        #self.max_pages = max_pages
        self.start_page = start_page
        self.end_page = end_page
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler("scraping.log"),
                                logging.StreamHandler()
                            ])
        
        
        
    """ def clean_text(self, text):
        # Elimina espacios en blanco alrededor del texto y maneja entidades HTML sin embargo está incluido en los métodos
        text = text.strip()
        text = html.unescape(text)
        return text
    """

    def get_quotes(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status() #antes de realizar operaciones
            
            soup = BeautifulSoup(response.text, 'lxml')  # Elección de lxml sobre html.parser y html5lib

            quotes = soup.find_all("div", class_="quote")
            blockquotes = soup.find_all("blockquote")

            for quote in quotes:
                text = quote.find("span", class_="text").get_text()
                author = quote.find("small", class_="author").get_text()
                tags = [tag.get_text() for tag in quote.find_all("a", class_="tag")]
                author_url = self.base_url + quote.find("a")["href"]

                if author not in self.authors_data:
                    self.authors_data[author] = self.get_author_info(author_url)

                self.quotes_data.append({
                    "text": text,
                    "author": author,
                    "tags": tags
                })

            for blockquote in blockquotes:
                text = blockquote.get_text(strip=True)  # Elimina los espacios en blanco alrededor del texto
                # Supongamos que no hay autor ni tags en blockquote
                self.quotes_data.append({
                    "text": text,
                    "author": "Unknown",
                    "tags": []
                })
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")

    def get_author_info(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            author_bio = soup.find("div", class_="author-details")
            return author_bio.get_text(strip=True) if author_bio else ""
        except requests.RequestException as e:
            logging.error(f"Error fetching author info from {url}: {e}")
            return ""

    def scrape_all_quotes(self):
        page = self.start_page
        while True:
            #if self.max_pages and page > self.max_pages:
            if self.end_page and page > self.end_page:
                break
            url = f"{self.base_url}/page/{page}/"
            response = requests.get(url)
            if response.status_code != 200:
                break
            self.get_quotes(url)
            logging.info(f"Scraped page {page}")
            page += 1
            time.sleep(1)


    def save_to_csv(self):
        quotes_df = pd.DataFrame(self.quotes_data)
        quotes_df.to_csv("quotes_data.csv", index=False)
        logging.info("Quotes data saved to quotes_data.csv")

        authors_df = pd.DataFrame.from_dict(self.authors_data, orient='index', columns=['bio'])
        authors_df.index.name = 'author'
        authors_df.to_csv("authors_data.csv")
        logging.info("Authors data saved to authors_data.csv")
        
        print("\nQuotes Data:")
        print(quotes_df)
        print("\nAuthors Data:")
        print(authors_df)

if __name__ == "__main__":
    base_url = "https://quotes.toscrape.com"
    scraper = QuoteScraper(base_url, start_page=1, end_page=5)
    scraper.scrape_all_quotes()
    scraper.save_to_csv()