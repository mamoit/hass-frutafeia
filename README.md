# Frutafeia Home Assistant Integration

A [Home Assistant](https://www.home-assistant.io/) custom integration that reads your
[Frutafeia](https://frutafeia.pt) account and exposes it as sensors: account balance,
member number, basket size, status, delegation, and the two basket lists
(not yet collected / already collected).

## Installation

### Via HACS (recommended)

1. In HACS, go to **Menu → Custom repositories** and add this repository URL.
2. Search for **Frutafeia** and click **Download**.
3. Restart Home Assistant.

### Manually

Copy the `custom_components/frutafeia` folder into your Home Assistant
`config` directory (i.e. `config/custom_components/frutafeia`), then restart
Home Assistant.

## Setup

1. In Home Assistant, go to **Settings → Devices & services → Add integration**.
2. Search for **Frutafeia**.
3. Enter your Frutafeia **email** and **password**.

Your credentials are validated against the site and stored encrypted in your
Home Assistant data store. They are never written to disk in plain text and are
not committed to this repository.

If your password changes later, Home Assistant will prompt you to re-enter it
(re-authentication flow) — no need to delete and re-add the integration.

## Sensors

| Sensor | State | Notes |
| --- | --- | --- |
| Saldo | number | Account balance, in `€` |
| Número de sócio | number | Member number |
| Tamanho | text | Basket size (e.g. "Cesta pequena") |
| Estado | text | Account status (e.g. "Com entregas activas") |
| Delegação | text | Delegation |
| Cesta não recolhida | number | Count of items not yet collected |
| Cesta recolhida | number | Count of items already collected |

The two basket sensors expose their full contents as the `items` attribute — a
list of `{product, producer}` objects — so you can use the count in automations
(e.g. "notify me when `cesta_nao_recolhida` increases") while still having the
product details available.

## Scan interval

The integration polls Frutafeia on a fixed interval, configured in **hours**
(1–24, default **6h**). You can set it during setup and change it any time via
**Settings → Devices & services → Frutafeia → Configure**. Changing it reloads
the integration so the new interval takes effect immediately.

## Development

Dependencies for local development:

```sh
pip install -r requirements.txt
```

## License

MIT — see [LICENSE](LICENSE).
