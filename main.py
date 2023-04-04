import requests
from bs4 import BeautifulSoup
import json

email = ""
pwd = ""

BASE_URL="https://frutafeia.pt"
LOGIN_URL=f"{BASE_URL}/user"

r = requests.get(LOGIN_URL)
if r.status_code != 200:
    exit(1)

soup = BeautifulSoup(r.text, 'html.parser')
captcha_sid = soup.find("input", {"name": "captcha_sid"}).attrs["value"]
captcha_token = soup.find("input", {"name": "captcha_token"}).attrs["value"]
form_build_id = soup.find("input", {"name": "form_build_id"}).attrs["value"]

r = requests.post(
    LOGIN_URL,
    data = {
        "name": email,
        "pass": pwd,
        "form_id": "user_login",
        "form_build_id": form_build_id,
        "captcha_sid": captcha_sid,
        "captcha_token": captcha_token,
        "captcha_response": "",
        "op": "Entrar",
    }
)
if r.status_code != 200:
    exit(1)

soup_menu = BeautifulSoup(r.text, 'html.parser')

result = {
    "nao_recolhida": [],
    "recolhida": [],
}

# Cesta não recolhida
soup_nao_recolhida = soup_menu.select(".nao-recolhida .views-row")
for item in soup_nao_recolhida:
    result["nao_recolhida"].append([
        item.select(".views-field-field-ref-producto")[0].text.strip(),
        item.select(".views-field-field-produtor")[0].text.strip()
    ])

# Cesta recolhida
soup_recolhida = soup_menu.select(".recolhida .views-row")
for item in soup_recolhida:
    result["recolhida"].append([
        item.select(".views-field-field-ref-producto")[0].text.strip(),
        item.select(".views-field-field-produtor")[0].text.strip()
    ])

# Saldo
result["saldo"] = float(soup_menu.select(".pane-consumidor-panel .row .val")[2].text.strip().replace("€",""))

# Tamanho
result["tamanho"] = soup_menu.select(".cesta .val")[0].text.strip()

# Estado
result["estado"] = soup_menu.select(".estado-cons .val")[0].text.strip()

# Delegação
result["delegacao"] = soup_menu.select(".delelegacao-cons .val")[0].text.strip()

# Número de sócio
result["socio"] = int(soup_menu.select(".numero-socio .val")[0].text.strip())

print(json.dumps(result))
