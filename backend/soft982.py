from playwright.sync_api import sync_playwright
from jelo_profiler import Profiler
t = Profiler()

def open_browser():
    p = sync_playwright().start()
    Browser = p.chromium.launch(headless=False)
    content = Browser.new_context()
    page = content.new_page()
    page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["stylesheet","font","images","media"] else route.continue_())
    t.step("load page")
    
    return Browser , page , p

def search_in_site(page, query: str):
    page.goto("https://soft98.ir/?do=search", wait_until="domcontentloaded")
    page.fill("#searchinput",query)
    page.keyboard.press("Enter")
    page.wait_for_selector(".cbddtl", state="visible")
    search_items = page.locator("a.cbddtl")
    t.step("process")
    return search_items

def extract_results (search_items):
    results = []
    for i in range(search_items.count()):

        item = search_items.nth(i)

        title = item.inner_text()

        url = item.get_attribute("href")

        results.append(
            {
                "title": title,
                "url": url
            }
        )

    return results

    
def main():
    query = input("Enter app name: ")
    Browser , page , p = open_browser()
    search_items = search_in_site(page, query)
    
    try:
        print("Search finished — page loaded")
        page.wait_for_timeout(3000)
        results = extract_results(search_items)
        for result in results:
            print(result)

    finally:
        Browser.close()
        p.stop()
        
main()
    

