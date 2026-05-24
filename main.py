from playwright.sync_api import sync_playwright
import keyboard
import time

# & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_debug_profile"
# https://sauce-demo.myshopify.com/account/register
# py main

DATA = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@email.com",
    "password": "Password123!",
    "phone": "600123456",
    "dni": "12345678Z"
}

FIELD_ALIASES = {
    "first_name": ["first", "firstname", "first_name", "nombre", "givenname", "given-name", "fname"],
    "last_name": ["last", "lastname", "last_name", "apellido", "surname", "family", "family-name", "lname"],
    "email": ["mail", "email", "e-mail", "correo"],
    "password": ["pass", "password", "contraseña", "clave", "pwd"],
    "phone": ["phone", "telefono", "teléfono", "mobile", "tlf", "tel", "celular"],
    "dni": ["dni", "nif", "nie", "documento", "identity", "national"]
}

IGNORE_NAMES = ["q", "s", "search", "buscar", "query"]
IGNORE_IDS   = ["search", "search-field", "search-input"]

def detect_field(identifier, field_type_attr=""):
    identifier = identifier.lower()
    if field_type_attr == "email":
        return "email"
    if field_type_attr == "password":
        return "password"
    if field_type_attr == "tel":
        return "phone"
    for field_type, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in identifier:
                return field_type
    return None

def get_active_page(browser):
    try:
        context = browser.contexts[0]
        for page in reversed(context.pages):
            if page.url != "about:blank":
                return page
        return context.pages[-1]
    except:
        return None

def diagnostico(page):
    print(f"\n=== DIAGNÓSTICO === URL: {page.url}\n")
    elements = page.query_selector_all("input, textarea, select")
    print(f"Total inputs en DOM: {len(elements)}\n")
    for i, el in enumerate(elements):
        try:
            print(f"[{i}] type='{el.get_attribute('type') or 'none'}' "
                  f"name='{el.get_attribute('name') or ''}' "
                  f"id='{el.get_attribute('id') or ''}'")
            print(f"     placeholder='{el.get_attribute('placeholder') or ''}' "
                  f"aria='{el.get_attribute('aria-label') or ''}' "
                  f"autocomplete='{el.get_attribute('autocomplete') or ''}'")
            print(f"     visible={el.is_visible()} disabled={el.is_disabled()}\n")
        except Exception as e:
            print(f"[{i}] Error: {e}\n")

def get_label_text(el, page, frame):
    try:
        id_attr = el.get_attribute("id") or ""
        if id_attr:
            label = frame.query_selector(f'label[for="{id_attr}"]')
            if label:
                return label.inner_text()
    except:
        pass
    try:
        return el.evaluate("""el => {
            const label = el.closest('label');
            if (label) return label.innerText;
            const prev = el.previousElementSibling;
            if (prev && prev.tagName === 'LABEL') return prev.innerText;
            const labelledby = el.getAttribute('aria-labelledby');
            if (labelledby) {
                const ref = document.getElementById(labelledby);
                if (ref) return ref.innerText;
            }
            return '';
        }""")
    except:
        return ""

def fill_element(el, page, frame, source="main"):
    try:
        type_attr = el.get_attribute("type") or ""
        if type_attr in ["checkbox", "radio", "hidden", "submit", "button", "image", "file", "reset"]:
            return

        name    = el.get_attribute("name") or ""
        id_attr = el.get_attribute("id") or ""

        if name.lower() in IGNORE_NAMES or id_attr.lower() in IGNORE_IDS:
            return
        if "search" in (name + id_attr).lower():
            return

        if not el.is_visible():
            try:
                el.scroll_into_view_if_needed(timeout=1000)
                el.wait_for(state="visible", timeout=1500)
            except:
                return

        if el.is_disabled():
            return

        placeholder  = el.get_attribute("placeholder") or ""
        aria         = el.get_attribute("aria-label") or ""
        autocomplete = el.get_attribute("autocomplete") or ""
        class_attr   = el.get_attribute("class") or ""
        label_text   = get_label_text(el, page, frame)

        identifier = f"{name} {id_attr} {placeholder} {aria} {label_text} {autocomplete} {class_attr}"
        detected = detect_field(identifier, type_attr)

        if detected and detected in DATA:
            print(f"  ✓ [{source}] [{detected}] -> '{identifier.strip()[:60]}'")
            el.click()
            el.fill(DATA[detected])
        else:
            print(f"  ✗ [{source}] Sin mapeo -> type='{type_attr}' name='{name}' id='{id_attr}' placeholder='{placeholder}'")

    except Exception as e:
        print(f"  Error en campo: {e}")

def fill_form(page):
    print("\n--- Rellenando formulario ---")
    selector = "input, textarea, select"

    for el in page.query_selector_all(selector):
        fill_element(el, page, page.main_frame, "main")

    for i, frame in enumerate(page.frames):
        if frame == page.main_frame:
            continue
        try:
            print(f"  Buscando en iframe {i}: {frame.url}")
            for el in frame.query_selector_all(selector):
                fill_element(el, page, frame, f"iframe-{i}")
        except Exception as e:
            print(f"  Error en frame {i}: {e}")

with sync_playwright() as p:
    print("Conectando al navegador...")
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    print("Conectado.")
    print("F2 = rellenar | F4 = diagnóstico\n")

    while True:
        key = keyboard.read_key()
        if key == "f2":
            try:
                page = get_active_page(browser)
                if not page:
                    print("No hay página activa.")
                    continue
                fill_form(page)
                print("Formulario completado.")
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(2)
        elif key == "f4":
            try:
                page = get_active_page(browser)
                if not page:
                    print("No hay página activa.")
                    continue
                diagnostico(page)
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(0.3)