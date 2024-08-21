import json
import sys
import requests
from queue import Queue
import threading
import time
from collections import defaultdict
import logging
from bs4 import BeautifulSoup
import html
import re


from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from tqdm import tqdm

import itertools

class UserAgentCycler:
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Safari/537.3",
    ]

    def __init__(self):
        self.agent_cycle = itertools.cycle(self.USER_AGENTS)

    def get_next_agent(self):
        return next(self.agent_cycle)
    
    
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
SLEEP_TIME = 1

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Safari/537.3",
]

# Create a logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
# Create a handler that outputs to stderr
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.ERROR)
# Create a formatter and add it to the handler
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(handler)

# Test the logger
#logger.error('This is an error message.')

class QueueWorker(threading.Thread):
    def __init__(self, queue, processor):
        threading.Thread.__init__(self)
        self.queue = queue
        self.processor = processor

    def run(self):
        while True:
            item, link_field, output = self.queue.get()
            if item is None:
                break
            self.processor.fetch_and_store(item, link_field, output)
            self.queue.task_done()
            time.sleep(SLEEP_TIME)  # Add a delay to respect rate limits

class RSSFeedProcessor:
    def __init__(self):
        self.data = []
        self.queues = defaultdict(Queue)
        self.processed_data = []
        self.lock = threading.Lock()
        self.workers = []

    def read_from_stdin(self):
        for line in sys.stdin:
            try:
                item = json.loads(line.strip())
                self.data.append(item)
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON: {line.strip()}")


    def fetch_urls(self):
        # results = []
        
        good = 0
        bad = 0
        
        # Configure session with connection pooling, retries, and user-agent
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries, pool_connections=1, pool_maxsize=1)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Set a user-agent
        # session.headers.update({
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        # })
        # Create an instance of UserAgentCycler
        cycler = UserAgentCycler()
        agent = cycler.get_next_agent()
        session.headers.update({
            'User-Agent': agent
        })
        
        # for url in urls:
        for record in tqdm(self.data, desc="Pulling articles", unit="article"):
        # for record in self.data:
            try:
                response = session.get(record['link'], timeout=10)
                response.raise_for_status()
                # results.append((url, response.text))
                record['text'] = self.paragraph_text(response.text)
                good += 1
                self.processed_data.append(record)
                time.sleep(SLEEP_TIME)  # Add a delay to respect rate limits
            except requests.RequestException as e:
                bad += 1
                #self.processed_data.append((url, f"Error: {str(e)}"))
                print(f"Error: Agent: {agent}\n{str(e)}")
                time.sleep(SLEEP_TIME)  # Add a delay to respect rate limits
                # results.append((url, f"Error: {str(e)}"))
        
        session.close()
        print(f"good {good} bad {bad} {good / good + bad * 100:.2f} %")
        return (good, bad)
        # return results


    def get_article(self, link_field="link", groupby="source", output="text"):
        for item in self.data:
            group = item.get(groupby, "default")
            self.queues[group].put((item, link_field, output))

        for group, queue in self.queues.items():
            worker = QueueWorker(queue, self)
            worker.start()
            self.workers.append(worker)

        for queue in self.queues.values():
            queue.join()

        for worker in self.workers:
            queue.put((None, None, None))  # Signal the worker to stop

        for worker in self.workers:
            worker.join()

    def paragraph_text(self, doc: str) -> str:
        """Return the text content of paragraph html tags"""
        soup = BeautifulSoup(doc, "html.parser")
        paragraphs = soup.find_all("p")
        result = []
        for p in paragraphs:
            # Replace HTML entities with UTF-8 entities
            text = html.unescape(str(p))
            text = BeautifulSoup(text, "html.parser").get_text()
            text = re.sub("\n", "", text)
            # Remove any remaining HTML tags
            text = re.sub("<[^<]+?>", "", text)
            result.append(text)
        return " ".join(result)

    def fetch_and_store(self, item, link_field, output):
        url = item.get(link_field)
        if not url:
            item[output] = "Error: No URL found"
            logging.warning(f"No URL found for item: {item.get('title', 'Unknown title')}")
        else:
            try:
                response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
                # response = requests.get(url, timeout=10)
                response.raise_for_status()
                item[output] = self.paragraph_text(response.text)
                logging.info(f"Successfully fetched content for: {item.get('title', 'Unknown title')}")
            except requests.RequestException as e:
                item[output] = f"Error: {str(e)}"
                logging.error(f"Failed to fetch content for {url}: {str(e)}")

        with self.lock:
            self.processed_data.append(item)

    def output_data(self):
        for item in self.processed_data:
            # json.dump(item, sys.stdout, ensure_ascii=False)
            print(json.dumps(item))
            # print("", file=fh)
            # sys.stdout.write('\n')
            # sys.stdout.flush()

if __name__ == "__main__":
    processor = RSSFeedProcessor()
    processor.read_from_stdin()
    # processor.get_article()
    processor.fetch_urls()
    processor.output_data()
