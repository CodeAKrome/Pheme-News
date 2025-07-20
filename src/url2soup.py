#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys

"""
Fetch HTML from a URL and parse it using BeautifulSoup.
This script fetches HTML content from a specified URL and applies a BeautifulSoup filter using the find_all method.
It prints the number of elements found and their content.
"""

def jpost(url, find_all_string):
    try:
        # Fetch the HTML content
        print(f"Fetching HTML from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Find the main article container
        article_body = soup.find('section', itemprop='articleBody')

        if not article_body:
            print("No article body found.")
            return
        print(f"Found article body: {article_body}")

        # 2. Find all <p> and <h3> tags within the container
        text_elements = article_body.find_all(['p'])

        # 3. Extract and print the text from each element
        for element in text_elements:
            # use .get_text() to extract text from child tags (like <a>)
            # and strip=True to remove leading/trailing whitespace
            print(element.get_text(strip=True))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"Error parsing HTML: {e}")


def fetch_and_parse(url, find_all_string):
    """
    Fetch HTML from URL and apply BeautifulSoup find_all filter

    Args:
        url (str): The URL to fetch HTML from
        find_all_string (str): The tag/selector to search for with find_all
    """
    try:
        # Fetch the HTML content
        print(f"Fetching HTML from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Apply find_all filter
        print(f"\nApplying find_all('{find_all_string}')...")
        results = soup.find_all(find_all_string)

        # Print results
        print(f"\nFound {len(results)} elements:")
        print("-" * 50)

        for i, element in enumerate(results, 1):
            print(f"Element {i}:")
            print(element)
            print("-" * 30)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"Error parsing HTML: {e}")


def main():
    # Get URL and find_all string from command line arguments or user input
    if len(sys.argv) == 3:
        url = sys.argv[1]
        find_all_string = sys.argv[2]
    else:
        url = input("Enter URL: ")
        find_all_string = input("Enter find_all string (e.g., 'a', 'div', 'p'): ")

    # fetch_and_parse(url, find_all_string)
    jpost(url, find_all_string)


if __name__ == "__main__":
    main()
