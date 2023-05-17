import os
import requests
from bs4 import BeautifulSoup
import pdfkit
from PyPDF2 import PdfMerger
from tqdm import tqdm
import hashlib


def get_wm_hackathon_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.startswith(
            "/wiki/Special:MyLanguage/Wikimedia_Hackathon_2023"
        ):
            full_link = "https://www.mediawiki.org" + href
            if full_link not in links:
                links.append(full_link)

    return links


def get_additional_links(url, domains):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for link in soup.find_all("a"):
        href = link.get("href")
        if href and any(domain in href for domain in domains):
            if not href.startswith("http"):
                for domain in domains:
                    if domain in href:
                        href = f"https://{domain}{href}"
                        break
            if href not in links:
                links.append(href)

    return links


def save_as_pdf(url, output_directory):
    url = url.rstrip("/")  # Remove trailing slash
    filename = url.rsplit("/", 1)[-1] or hashlib.md5(url.encode()).hexdigest()
    output_filename = os.path.join(output_directory, filename + ".pdf")

    if os.path.exists(output_filename):
        print(f"File {output_filename} already exists, skipping download.")
        return output_filename

    try:
        pdfkit.from_url(url, output_filename)
        print(f"Successfully saved {url} as {output_filename}")
        return output_filename
    except Exception as e:
        print(f"Failed to save {url} as PDF. Error: {e}")
        return None


def main():
    main_url = "https://www.mediawiki.org/wiki/Wikimedia_Hackathon_2023"
    print(f"Getting linked pages from {main_url}")
    links = get_wm_hackathon_links(main_url)
    print(f"Found {len(links)} pages linked from the main page")

    output_directory = "pdfs"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    pdf_files = []
    print("Converting pages to PDF:")
    for link in tqdm(links):
        output_filename = save_as_pdf(link, output_directory)
        if output_filename and output_filename not in pdf_files:
            pdf_files.append(output_filename)

    for link in tqdm(links):
        additional_links = get_additional_links(
            link, ["wikimedia.org", "mediawiki.org"]
        )
        for additional_link in additional_links:
            output_filename = save_as_pdf(additional_link, output_directory)
            if output_filename and output_filename not in pdf_files:
                pdf_files.append(output_filename)

    print("Merging PDFs:")
    merger = PdfMerger()

    for pdf in tqdm(pdf_files):
        merger.append(pdf)

    merger.write("pdfs/merged.pdf")
    merger.close()
    print("All PDFs have been merged into pdfs/merged.pdf")


if __name__ == "__main__":
    main()
