import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup

email = ""
pwd = ""

BASE_URL="https://frutafeia.pt"
LOGIN_URL=f"{BASE_URL}/user"


async def login(client, captcha_values):
    async with client.post(
        LOGIN_URL,
        data = {
            "name": email,
            "pass": pwd,
            "form_id": "user_login",
            "form_build_id": captcha_values["form_build_id"],
            "captcha_sid": captcha_values["captcha_sid"],
            "captcha_token": captcha_values["captcha_token"],
            "captcha_response": "",
            "op": "Entrar",
        }) as resp:
        assert resp.status == 200

        soup_menu = BeautifulSoup(await resp.text(), 'html.parser')

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

        return json.dumps(result)

async def get_captcha(client):
    async with client.get(LOGIN_URL) as resp:
        assert resp.status == 200

        soup = BeautifulSoup(await resp.text(), 'html.parser')
        captcha_values = {
            "captcha_sid": soup.find("input", {"name": "captcha_sid"}).attrs["value"],
            "captcha_token": soup.find("input", {"name": "captcha_token"}).attrs["value"],
            "form_build_id": soup.find("input", {"name": "form_build_id"}).attrs["value"],
        }
        return captcha_values

async def main():
    async with aiohttp.ClientSession() as client:
        captcha_values = await get_captcha(client)
        values = await login(client, captcha_values)
        print(values)
        return values

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
