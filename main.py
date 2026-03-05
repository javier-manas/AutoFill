from playwright.sync_api import sync_playwright
import keyboard
import time
import random

# & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_debug_profile"
# https://sauce-demo.myshopify.com/account/register

from playwright.sync_api import sync_playwright
import keyboard
import time
import random

DATA = {
    "first": "John",
    "last": "Doe",
    "name": "John Doe",
    "email": "john@email.com",
    "password": "Password123!"
}


def guess_value(identifier):

    identifier = identifier.lower()

    if "first" in identifier:
        return DATA["first"]

    if "last" in identifier:
        return DATA["last"]

    if "name" in identifier:
        return DATA["name"]

    if "mail" in identifier:
        return DATA["email"]

    if "pass" in identifier:
        return DATA["password"]

    return None


def human_fill(el, text):

    el.click()

    for c in text:
        el.type(c)
        time.sleep(random.uniform(0.05, 0.12))


def get_active_page(browser):

    context = browser.contexts[0]

    pages = context.pages

    if len(pages) == 0:
        return None

    return pages[-1]


def wait_page_ready(page):

    try:
        page.wait_for_load_state("domcontentloaded", timeout=5000)
    except:
        pass


def fill_form(page):

    wait_page_ready(page)

    elements = page.query_selector_all("input, textarea")

    for el in elements:

        try:

            field_type = el.get_attribute("type") or ""

            if field_type in ["hidden", "submit", "button", "checkbox", "radio"]:
                continue

            name = el.get_attribute("name") or ""
            id_attr = el.get_attribute("id") or ""
            placeholder = el.get_attribute("placeholder") or ""

            identifier = f"{name} {id_attr} {placeholder}"

            value = guess_value(identifier)

            if value:

                print(f"Rellenando {identifier} -> {value}")

                human_fill(el, value)

        except:
            pass


with sync_playwright() as p:

    print("Conectando al navegador...")

    browser = p.chromium.connect_over_cdp("http://localhost:9222")

    print("Conectado.")

    page = get_active_page(browser)

    print("Página cargada.")
    print("Pulsa F1 para rellenar el formulario.")

    while True:

        keyboard.wait("F2")

        try:

            page = get_active_page(browser)

            if page is None:
                print("No hay página activa.")
                continue

            print("F2 detectado. Buscando campos...")

            fill_form(page)

        except Exception as e:

            print("Error detectado:", e)
            print("Intentando continuar...")
            time.sleep(2)