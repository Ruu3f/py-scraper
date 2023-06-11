import os, re, cfscrape, string, requests, subprocess
from urllib.parse import urljoin
from colorama import init, Fore

init()

websites = [
    url.strip()
    for url in input("Websites to scrape (use ',' for multiple websites): ").split(",")
]

subprocess.check_call(["pip", "install", "urllib3==1.25.11"])


def scrape_website(url):
    try:
        scraper = cfscrape.create_scraper()
        response = scraper.get(url)

        if response.status_code == 200:
            domain = response.url.split("//")[1].split("/")[0]
            folder_path = f"Scraped/{domain}"
            os.makedirs(folder_path, exist_ok=True)

            index_file_path = os.path.join(folder_path, "index.html")
            with open(index_file_path, "w", encoding="utf-8") as file:
                file.write(response.text)

            css_urls = re.findall(
                r'<link.*?href=["\'](.*?)["\']', response.text, flags=re.IGNORECASE
            )
            js_urls = re.findall(
                r'<script.*?src=["\'](.*?)["\']', response.text, flags=re.IGNORECASE
            )

            for css_url in css_urls:
                absolute_css_url = urljoin(url, css_url)
                css_response = scraper.get(absolute_css_url)
                css_file_name = os.path.basename(css_url)
                css_file_path = os.path.join(folder_path, css_file_name)
                with open(css_file_path, "w", encoding="utf-8") as file:
                    file.write(css_response.text)

            for js_url in js_urls:
                absolute_js_url = urljoin(url, js_url)
                js_response = scraper.get(absolute_js_url)
                js_file_name = os.path.basename(js_url)
                valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
                js_file_name = "".join(c for c in js_file_name if c in valid_chars)
                js_file_path = os.path.join(folder_path, js_file_name)
                with open(js_file_path, "w", encoding="utf-8") as file:
                    file.write(js_response.text)

            print(Fore.GREEN + f"Website {url} scraped successfully.")
        else:
            print(
                Fore.RED
                + f"Failed to scrape website {url}. Status code: {response.status_code}"
            )
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"An error occurred while scraping website {url}: {str(e)}")
    except IOError as e:
        print(Fore.RED + f"Error occurred during file operation: {str(e)}")


for website in websites:
    scrape_website(website)
