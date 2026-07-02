from urllib.parse import quote_plus
import httpx
from jelo_profiler import Profiler
from selectolax.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor

# ========================
# Colors & Theme (Orange Theme Setup)
# ========================
ORANGE = "\033[38;5;208m"
LIGHT_ORANGE = "\033[38;5;214m"
RESET = "\033[0m"
BOLD = "\033[1m"
GRAY = "\033[90m"
GREEN = "\033[32m"
RED = "\033[31m"

def print_banner():
    print(f"{ORANGE}{BOLD}┌────────────────────────────────────────────────────────┐{RESET}")
    print(f"{ORANGE}{BOLD}│         ORBIT HTTPX + SELECTOLAX (ULTRA-FAST)          │{RESET}")
    print(f"{ORANGE}{BOLD}└────────────────────────────────────────────────────────┘{RESET}")

def print_step(message):
    print(f"{ORANGE}[+]{RESET} {message}")

def print_success(message):
    print(f"{GREEN}[✔]{RESET} {message}")

def print_error(message):
    print(f"{RED}[✗]{RESET} {message}")

# ========================
# Global Profiler & Cache
# ========================
t = Profiler()
PAGE_CACHE = {}  # Used for instant loading via background pre-fetching

# Optimized headers requesting compressed payloads (gzip/br)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# ========================
# Functions
# ========================

def setup_client():
    t.iteration("Setup")
    # Optimize TCP pooling and enable HTTP/2 for maximum throughput
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    client = httpx.Client(
        headers=HEADERS, 
        timeout=5.0, 
        follow_redirects=True, 
        http2=True,  # Enable HTTP/2 multiplexing
        limits=limits
    )
    t.step("make client")
    return client


def search_in_site(client, query: str):
    url = f"https://soft98.ir/?do=search&subaction=search&story={quote_plus(query)}"
    response = client.get(url)
    t.step("goto search page")

    # PASS RAW BYTES (.content) instead of string (.text)
    # This avoids Python's internal UTF-8 string decode overhead completely!
    tree = HTMLParser(response.content)
    t.step("parse html via C engine")

    return tree.css("a.cbddtl")


def extract_results(search_items):
    # List comprehension is 15-25% faster in CPython than `.append()` inside a loop
    results = [
        {"title": node.text(strip=True), "url": node.attributes.get("href")}
        for node in search_items
    ]
    t.step("extract results")

    print(f"\n{ORANGE}{BOLD}--- Results Found (Lightning Fast ⚡): ---{RESET}")
    for i, item in enumerate(results, start=1):
        print(f"  {LIGHT_ORANGE}{i}.{RESET} {item['title']}")
    print(f"{ORANGE}------------------------------------------{RESET}\n")

    return results


def prefetch_worker(client, url):
    """Silently fetches and caches pages in background threads."""
    if url not in PAGE_CACHE:
        try:
            PAGE_CACHE[url] = client.get(url)
        except Exception:
            pass


def select_app(results, client):
    # ⚡ EXTREME OPTIMIZATION:
    # While the user is staring at the terminal choosing a number, CPU is idle.
    # We use this dead time to immediately download the top 5 results in background threads!
    top_urls = [r["url"] for r in results[:5] if r.get("url")]
    executor = ThreadPoolExecutor(max_workers=5)
    for url in top_urls:
        executor.submit(prefetch_worker, client, url)

    choice_input = input(f"{ORANGE}{BOLD}👉 Choose app (number): {RESET}")
    t.step("user_selection_wait_ignored")
    
    # Shutdown background worker non-blockingly
    executor.shutdown(wait=False)

    choice = int(choice_input)
    selected = results[choice - 1]
    t.step(f"user picked: {selected['title']}")
    return selected


def open_app_page(client, selected_app):
    url = selected_app["url"]
    
    # Check if our background thread already downloaded it while user was typing
    if url in PAGE_CACHE:
        response = PAGE_CACHE[url]
        t.step("open app page (INSTANT - Served from background cache ⚡)")
    else:
        response = client.get(url)
        t.step("open app page (network fetch)")
        
    return response

# ========================
# Main Loop Running
# ========================

def main():
    print_banner()
    client = setup_client()

    try:
        while True:
            PAGE_CACHE.clear() # Clear cache for new searches
            query_input = input(f"\n{LIGHT_ORANGE}🔍 Enter app name (or type 'exit' to quit): {RESET}")
            t.step("user_query_input_wait_ignored")

            if not query_input or query_input.strip().lower() == "exit":
                break

            query = query_input.strip()
            t.iteration(f"Query: '{query}'")

            try:
                print_step(f"Searching for '{query}'...")
                search_items = search_in_site(client, query)
                print_success("Search finished!")

                results = extract_results(search_items)
                if not results:
                    print_error("No results found.")
                    continue

                selected_app = select_app(results, client)

                print(f"\n{ORANGE}{BOLD}Selected App Details:{RESET}")
                print(f"  {GRAY}Title:{RESET} {selected_app['title']}")
                print(f"  {GRAY}URL  :{RESET} {selected_app['url']}")

                response = open_app_page(client, selected_app)

                if response.status_code == 200:
                    print_success("App page loaded successfully!")

            except Exception as e:
                print_error(f"An error occurred during search: {e}")

    finally:
        print_step("Closing client connection and saving performance logs...")
        client.close()
        t.finish()

if __name__ == "__main__":
    main()