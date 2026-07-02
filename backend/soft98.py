from urllib.parse import quote_plus
from jelo_profiler import Profiler
from playwright.sync_api import sync_playwright

# ========================
# Colors & Theme (Orange Theme Setup)
# ========================
# Rang haye CLI baraye khoshgel sazi (orange theme)
ORANGE = "\033[38;5;208m"
LIGHT_ORANGE = "\033[38;5;214m"
RESET = "\033[0m"
BOLD = "\033[1m"
GRAY = "\033[90m"
GREEN = "\033[32m"
RED = "\033[31m"

def print_banner():
    # Ye banner sade va ghashang ba rang haye narenji
    print(f"{ORANGE}{BOLD}┌────────────────────────────────────────────────────────┐{RESET}")
    print(f"{ORANGE}{BOLD}│                ORBIT PLAYWRIGHT SEARCHER               │{RESET}")
    print(f"{ORANGE}{BOLD}└────────────────────────────────────────────────────────┘{RESET}")

def print_step(message):
    print(f"{ORANGE}[+]{RESET} {message}")

def print_success(message):
    print(f"{GREEN}[✔]{RESET} {message}")

def print_error(message):
    print(f"{RED}[✗]{RESET} {message}")

# ========================
# Values
# ========================

t = Profiler()

# in resource ha ro block mikonim ta ham bandwidth kamtar masraf she ham speed bere bala
BLOCKED = {  
    "image",
    "font",
    "media",
    "stylesheet",
    "texttrack",
    "object",
    "beacon",
    "imageset",
}

# in host haye ezafi va tabliqi ro ham block mikonim
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
    # host haye analytics o tabliq ro block mikonim ke speed up beshe
    if any(host in route.request.url for host in BLOCK_HOSTS):
        return route.abort()

    if route.request.resource_type in BLOCKED:
        return route.abort()

    return route.continue_()


def open_browser():
    p = sync_playwright().start()

    t.iteration("Setup")
    t.step("make browser")

    # browser ro ba tanzimate sabok baz mikonim ke CPU va RAM kamtar masraf kone
    Browser = p.chromium.launch(
        headless=True,  # bayad true bashe baraye production o speede bishtar
        args=[
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
            "--blink-settings=imagesEnabled=false",
        ],
    )
    t.step("launch browser")

    page = Browser.new_page()

    # timeout default 30s e, kamesh mikonim ke age moshkeli pish oomad alaki moatal nashi
    page.set_default_timeout(5000)
    t.step("load page")

    # rooting baraye block kardane chizaye ezafi active mishe
    page.route("**/*", block)
    t.step("route block")

    return Browser, page, p


def search_in_site(page, query: str):
    # az commit estefade mikonim chon az domcontentloaded sari tare va montazere load ezafe nemimoone
    encoded_query = quote_plus(query)
    direct_url = f"https://soft98.ir/?do=search&subaction=search&story={encoded_query}"

    page.goto(direct_url, wait_until="commit")
    t.step("goto search page")

    # montazer mimoonim ta elemente morede nazar be DOM vasl she
    page.wait_for_selector(".cbddtl", state="attached")
    t.step("wait for results")

    search_items = page.locator("a.cbddtl")
    t.step("process")

    return search_items


def extract_results(search_items):
    # be jaye inke tak tak element ha ro bekhunim, yeja ba JS evaluate hame ro migirim (RPC kamtar = speed bishtar)
    results = search_items.evaluate_all("""
    els => els.map(e => ({
        title: e.innerText,
        url: e.href
    }))
    """)
    t.step("extract results")

    print(f"\n{ORANGE}{BOLD}--- Results Found: ---{RESET}")
    for i, item in enumerate(results, start=1):
        print(f"  {LIGHT_ORANGE}{i}.{RESET} {item['title']}")
    print(f"{ORANGE}----------------------{RESET}\n")

    return results


def select_app(results):
    # baraye inke typinge user tooye mohasebe ye time kharabkari nakone:
    # daryofte input az karbar:
    choice_input = input(f"{ORANGE}{BOLD}👉 Choose app (number): {RESET}")
    
    # hamin ke input gerefte shod, ye step baraye jelo_profiler mizanim ta time delay karbar injoori track o hazf beshe
    t.step("user_selection_wait_ignored")
    
    choice = int(choice_input)
    selected = results[choice - 1]
    t.step(f"user picked: {selected['title']}")
    return selected


def open_app_page(page, selected_app):
    page.goto(
        selected_app["url"],
        wait_until="commit",
    )
    t.step("open app page")


# ========================
# Main Loop Running
# ========================


def main():
    print_banner()
    Browser, page, p = open_browser()

    try:
        while True:
            # daryofte query az karbar
            query_input = input(f"\n{LIGHT_ORANGE}🔍 Enter app name (or type 'exit' to quit): {RESET}")
            
            # hazfe asare time e ke karbar baraye type kardan gozashte
            t.step("user_query_input_wait_ignored")

            if not query_input or query_input.strip().lower() == "exit":
                break

            query = query_input.strip()
            t.iteration(f"Query: '{query}'")

            try:
                print_step(f"Searching for '{query}'...")
                search_items = search_in_site(page, query)
                print_success("Search finished!")

                results = extract_results(search_items)
                selected_app = select_app(results)

                print(f"\n{ORANGE}{BOLD}Selected App Details:{RESET}")
                print(f"  {GRAY}Title:{RESET} {selected_app['title']}")
                print(f"  {GRAY}URL  :{RESET} {selected_app['url']}")

                open_app_page(page, selected_app)

                if page.url == selected_app["url"]:
                    print_success("App page loaded successfully!")

            except Exception as e:
                print_error(f"An error occurred during search: {e}")

    finally:
        print_step("Closing browser and saving performance logs...")
        Browser.close()
        p.stop()
        t.finish()


if __name__ == "__main__":
    main()