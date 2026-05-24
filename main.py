from playwright.sync_api import sync_playwright
import keyboard
import time


DATA = {

    "first_name": "John",
    "last_name": "Doe",
    "email": "john@email.com",
    "password": "Password123!"
}

FIELD_ALIASES = {

    "first_name": [
        "first",
        "firstname",
        "first_name",
        "nombre",
        "nombre pila",
        "givenname"
    ],

    "last_name": [
        "last",
        "lastname",
        "last_name",
        "apellido",
        "surname"
    ],

    "email": [
        "mail",
        "email",
        "correo",
        "correo electrónico"
    ],

    "password": [
        "pass",
        "password",
        "contraseña",
        "clave"
    ]
}

def detect_field(identifier):

    identifier = identifier.lower()

    for field_type, aliases in FIELD_ALIASES.items():

        for alias in aliases:

            if alias in identifier:
                return field_type

    return None

def get_active_page(browser):

    try:

        context = browser.contexts[0]

        pages = context.pages

        if len(pages) == 0:
            return None

        return pages[-1]

    except:
        return None

def wait_page_ready(page):

    try:
        page.wait_for_load_state("domcontentloaded", timeout=5000)
    except:
        pass

def fill_form(page):

    wait_page_ready(page)

    print("Buscando campos...")

    elements = page.query_selector_all(
        "input:not([type=hidden]):not([type=submit]):not([type=button]), textarea"
    )

    print(f"Campos encontrados: {len(elements)}")

    for el in elements:

        try:

            field_type = el.get_attribute("type") or ""

            if field_type in ["checkbox", "radio"]:
                continue

            name = el.get_attribute("name") or ""
            id_attr = el.get_attribute("id") or ""
            placeholder = el.get_attribute("placeholder") or ""
            aria = el.get_attribute("aria-label") or ""

            label_text = ""

            try:

                if id_attr:

                    label = page.query_selector(
                        f'label[for="{id_attr}"]'
                    )

                    if label:
                        label_text = label.inner_text()

            except:
                pass

            identifier = f"""
            {name}
            {id_attr}
            {placeholder}
            {aria}
            {label_text}
            """.lower() 

            detected = detect_field(identifier)

            if detected:

                value = DATA[detected]

                print(f"[{detected}] -> {identifier.strip()}")

                # RELLENO RÁPIDO
                el.fill(value)

        except Exception as e:

            print("Error rellenando campo:", e)




with sync_playwright() as p:

    print("Conectando al navegador Chrome...")

    browser = p.chromium.connect_over_cdp(
        "http://localhost:9222"
    )

    print("Conectado.")

    print("Pulsa F2 para rellenar formularios.")

    while True:

        keyboard.wait("F2")

        try:

            page = get_active_page(browser)

            if page is None:

                print("No hay pestaña activa.")
                continue


            print("F1 detectado.")

            fill_form(page)

            print("Formulario completado.")


        except Exception as e:

            print("Error detectado:", e)

            print("Reintentando...")

            time.sleep(2)