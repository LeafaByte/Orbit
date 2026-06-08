from playwright.sync_api import sync_playwright
from jelo_profiler import Profiler


with sync_playwright() as p:
  browser = p.chromium.launch(
    headless=True
  )

  context = browser.new_context()

  inputT = input("Enter name of the app: ")

  p = Profiler()
  page = context.new_page()

  page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["stylesheet","font","images","media"] else route.continue_())

  page.goto(
    "https://soft98.ir/?do=search",
    wait_until="domcontentloaded"
  )

  p.step("load page")

  page.fill("#searchinput",inputT)
  page.keyboard.press("Enter")

  p.step("process")

  page.wait_for_selector(".cbddtl")

  items = page.locator("a.cbddtl").all()

  for item in items:
    print(item.inner_text())

  p.step("show result")
  p.finish()
  