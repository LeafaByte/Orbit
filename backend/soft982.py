from jelo_profiler import Profiler
from playwright.sync_api import sync_playwright

# ========================
# Values
# ========================

t = Profiler()

BLOCKED = {  # yekam chizaye bishtari block konim
    "image",
    "font",
    "media",
    "stylesheet",
    "texttrack",
    "object",
    "beacon",
    "imageset",
}

BLOCK_HOSTS = (
    "google-analytics",
    "googletagmanager",
    "doubleclick",
    "facebook",
    "clarity",
)


# ========================
# Funcs
# ========================

def block(route):
    # host haye analytics o tabliq ro block mikonim
    if any(host in route.request.url for host in BLOCK_HOSTS):
        return route.abort()

    if route.request.resource_type in BLOCKED:
        return route.abort()

    return route.continue_()


def open_browser():
    p = sync_playwright().start()

    t.iteration("Setup")
    t.step("make browser")

    Browser = p.chromium.launch(
        headless=True,  # bayad true bashe baraye production
        args=[
            # ina baes mishe browser feature haye ezafi disable shan
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-breakpad",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-features=TranslateUI",
            "--disable-sync",
            "--no-first-run",
            "--no-default-browser-check",
            "--mute-audio",
        ],
    )
    t.step("launch browser")

    # context cookie va storage negah midare
    # ma niaz nadarim pas mostaghim page misazim
    page = Browser.new_page()

    # timeout default 30s e, ma kamesh mikonim
    page.set_default_timeout(5000)
    t.step("load page")

    # faghat ye route lazeme
    page.route("**/*", block)
    t.step("route block")

    return Browser, page, p


def search_in_site(Link, page, query: str):
    # commit sari tar az domcontentloaded e
    page.goto(Link, wait_until="commit")
    t.step("goto search page")

    search = page.locator("#searchinput")

    # locator ye RPC kamtar mizane
    search.fill(query)
    search.press("Enter")
    t.step("fill query & submit")

    # visible lazem nist, hamin ke peyda she kafiye
    page.wait_for_selector(".cbddtl")
    t.step("wait for results")

    search_items = page.locator("a.cbddtl")
    t.step("process")

    return search_items


def extract_results(search_items):
    # hame result ha ro yeja ba JS migirim
    # bejaye inke baraye har item ye RPC bezanim
    results = search_items.evaluate_all("""
    els => els.map(e => ({
        title: e.innerText,
        url: e.href
    }))
    """)
    t.step("extract results")

    for i, item in enumerate(results, start=1):
        print(f"{i}. {item['title']}")

    return results


def select_app(results):
    choice = int(input("Choose app: "))
    selected = results[choice - 1]
    t.step(f"user picked: {selected['title']}")
    return selected


def open_app_page(page, selected_app):
    # mojadad commit az domcontentloaded sari tare
    page.goto(
        selected_app["url"],
        wait_until="commit",
    )
    t.step("open app page")


# ========================
# Main Loop Running
# ========================

def main():
    Browser, page, p = open_browser()

    try:
        while True:
            query = input("Enter app name: ")

            if not query or query.strip().lower() == "exit":
                break

            # in marker too gozaresh moshakhas mikone in step ha
            # baraye kodoom iteration o kodoom vorodi e
            t.iteration(f"Query: '{query}'")

            try:
                search_items = search_in_site(
                    "https://soft98.ir/?do=search",
                    page,
                    query,
                )
                print("Search finished!")

                results = extract_results(search_items)
                selected_app = select_app(results)

                print("\nSelected App:")
                print(selected_app["title"])
                print(selected_app["url"])

                open_app_page(page, selected_app)

                if page.url == selected_app["url"]:
                    print("Successful!")

            except Exception as e:
                print(f"An error occurred during search: {e}")

    finally:
        Browser.close()
        p.stop()
        t.step("show result")
        t.finish()


if __name__ == "__main__":
    main()