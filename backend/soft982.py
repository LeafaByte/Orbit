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

def search_in_site(Link, page, query: str):
    page.goto(Link, wait_until="domcontentloaded")
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
    for i, item in enumerate(results, start=1):
            print(f"{i}. {item['title']}")
    return results

def select_app(results):
    choice = int(input("Choose app: "))
    selected_app = results[choice - 1]
    return selected_app

def open_app_page(page, selected_app):
    
    page.goto(
        selected_app["url"],
        wait_until="domcontentloaded"
    )

    
def main():
    query = input("Enter app name: ")
    Browser , page , p = open_browser()
    search_items = search_in_site("https://soft98.ir/?do=search",page, query)
   
    
    try:
        print("Search finished — page loaded")
        # page.wait_for_timeout(3000)
        results = extract_results(search_items)
        selected_app = select_app(results)

        print("\nSelected App:")
        print(selected_app["title"])
        print(selected_app["url"])
        open_app_page(page, selected_app)
        if page.url == selected_app["url"]:
            print("successful!")

         
    finally:
        Browser.close()
        p.stop()
        
main()