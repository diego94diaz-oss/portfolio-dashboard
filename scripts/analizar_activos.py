#!/usr/bin/env python3
"""
Analizador de activos v2
Flujo: memory.md → yfinance → analisis_activos.md + index.html
Si yfinance no tiene datos, indica los tickers que necesitan PrecioWEB (fallback manual).
"""

import yfinance as yf
from datetime import datetime
import os
import re
import sys

# Forzar UTF-8 en stdout (Windows usa cp1252 por defecto y rompe con emojis/flechas)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(ROOT, "memory.md")
MD_FILE     = os.path.join(ROOT, "analysis", "analisis_activos.md")
HTML_FILE   = os.path.join(ROOT, "index.html")

MAX_PCT = 0.25  # tope de concentración por posición


# ── PARSEAR MEMORY.MD ─────────────────────────────────────────────────────────

def parse_memory():
    """Extrae portafolio y valor total de memory.md."""
    with open(MEMORY_FILE, encoding="utf-8") as f:
        content = f.read()

    total_match = re.search(r"\*\*Valor total del portafolio:\s*\$([0-9,\.]+)\*\*", content)
    total = float(total_match.group(1).replace(",", "")) if total_match else 0.0

    portfolio = {}
    # Formato de tabla: | TICKER | Nombre | Acciones | $compra | $actual | $valor | X.X% | +/-X.X% |
    row_re = re.compile(
        r"\|\s*([A-Z0-9\-]+)\s*\|\s*([^|]+?)\s*\|\s*([\d,\.]+)\s*\|\s*\$([0-9,\.]+)\s*\|\s*\$([0-9,\.]+)\s*\|\s*\$([0-9,\.]+)\s*\|\s*([\d\.]+)%[^|]*\|\s*([+\-][\d\.]+)%"
    )
    for m in row_re.finditer(content):
        ticker    = m.group(1).strip()
        name      = m.group(2).strip()
        shares    = float(m.group(3).replace(",", ""))
        buy_price = float(m.group(4).replace(",", ""))
        price     = float(m.group(5).replace(",", ""))
        value     = float(m.group(6).replace(",", ""))
        pct       = float(m.group(7))
        ret       = float(m.group(8))
        portfolio[ticker] = {
            "name": name, "shares": shares, "buyPrice": buy_price,
            "price": price, "value": value, "pct": pct, "ret": ret,
            "alert": pct >= 20.0,
        }

    return portfolio, total


# ── YFINANCE ──────────────────────────────────────────────────────────────────

def fetch_ticker(symbol):
    """Precio actual y objetivo desde yfinance. None si faltan datos clave."""
    try:
        info = yf.Ticker(symbol).info
        precio_actual  = info.get("currentPrice") or info.get("regularMarketPrice")
        precio_objetivo = info.get("targetMeanPrice")
        if not precio_actual or not precio_objetivo:
            return None
        return {
            "nombre":        info.get("shortName", symbol),
            "precio_actual": precio_actual,
            "precio_objetivo": precio_objetivo,
            "precio_min":    info.get("targetLowPrice"),
            "precio_max":    info.get("targetHighPrice"),
            "num_analistas": info.get("numberOfAnalystOpinions"),
        }
    except Exception as e:
        print(f"  [!] Error yfinance {symbol}: {e}")
        return None


# ── ANÁLISIS COMPLETO ─────────────────────────────────────────────────────────

def get_recomendacion(upside):
    if upside > 30:   return "COMPRAR MÁS"
    elif upside >= 0: return "MANTENER"
    else:             return "VENDER"


def analizar(symbol, portfolio, total_value):
    """Combina yfinance + memory.md. Retorna None si yfinance no tiene datos."""
    data = fetch_ticker(symbol)
    if not data:
        return None

    upside = (data["precio_objetivo"] - data["precio_actual"]) / data["precio_actual"] * 100
    rec    = get_recomendacion(upside)

    mem       = portfolio.get(symbol, {})
    buy_price = mem.get("buyPrice")
    shares    = mem.get("shares", 0)
    value     = mem.get("value", data["precio_actual"] * shares)
    pct       = mem.get("pct") or (value / total_value * 100 if total_value else 0)
    pl_pct    = ((data["precio_actual"] - buy_price) / buy_price * 100) if buy_price else None

    sugerencia = None
    if rec == "COMPRAR MÁS" and total_value and data["precio_actual"]:
        room       = max(0, total_value * MAX_PCT - value)
        add_shares = room / data["precio_actual"]
        add_pct    = room / total_value * 100
        sugerencia = {"add_shares": add_shares, "add_pct": add_pct}

    return {
        "symbol":          symbol.upper(),
        "nombre":          data["nombre"],
        "precio_actual":   data["precio_actual"],
        "precio_objetivo": data["precio_objetivo"],
        "precio_min":      data["precio_min"],
        "precio_max":      data["precio_max"],
        "num_analistas":   data["num_analistas"],
        "upside":          upside,
        "recomendacion":   rec,
        "buy_price":       buy_price,
        "shares":          shares,
        "value":           value,
        "pct":             pct,
        "pl_pct":          pl_pct,
        "sugerencia":      sugerencia,
        "alert":           pct > 20,
    }


# ── FORMATO DE PROPUESTA ──────────────────────────────────────────────────────

def formatear_propuesta(d):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    rango = ""
    if d["precio_min"] and d["precio_max"]:
        rango = f" (rango: ${d['precio_min']:.2f} – ${d['precio_max']:.2f}"
        if d["num_analistas"]:
            rango += f", {d['num_analistas']} analistas"
        rango += ")"

    buy_line = ""
    if d["buy_price"] and d["pl_pct"] is not None:
        sign = "+" if d["pl_pct"] >= 0 else ""
        buy_line = f"\nPrecio compra (promedio):   ${d['buy_price']:.2f} | P&L actual: {sign}{d['pl_pct']:.1f}%"

    sug_line   = ""
    alert_line = ""
    if d["recomendacion"] == "COMPRAR MÁS" and d["sugerencia"]:
        s = d["sugerencia"]
        sug_line = f"\n  → Sugerencia de posición:  Agregar ~{s['add_shares']:.1f} acciones (+{s['add_pct']:.1f}% portafolio). Tope: no superar 25%."
    if d["alert"]:
        alert_line = f"\n  → Alerta concentración:    ⚠️ Posición actual en {d['pct']:.1f}% del portafolio."

    return f"""
---

### {fecha} — {d['symbol']} ({d['nombre']})

```
Ticker:                     {d['symbol']}
Precio actual:              ${d['precio_actual']:.2f}{buy_line}
Precio objetivo (consenso): ${d['precio_objetivo']:.2f}{rango} | Upside: {d['upside']:+.1f}%
Recomendación:              {d['recomendacion']}{sug_line}{alert_line}
Fundamento:                 Upside de {d['upside']:.1f}% respecto al precio objetivo de consenso de analistas.
Riesgo principal a vigilar: Revisar si el precio objetivo fue actualizado recientemente.
```
"""


# ── TABLA RESUMEN EN ANALISIS_ACTIVOS.MD ─────────────────────────────────────

SUMMARY_START = "<!-- SUMMARY_TABLE_START -->"
SUMMARY_END   = "<!-- SUMMARY_TABLE_END -->"

SIGNAL_ICON = {"COMPRAR MÁS": "🟢", "MANTENER": "🔵", "VENDER": "🔴"}


def _parse_existing_summary(content):
    """Extrae filas existentes del resumen como dict { ticker: row_string }."""
    existing = {}
    if SUMMARY_START not in content or SUMMARY_END not in content:
        return existing
    block = re.search(re.escape(SUMMARY_START) + r"(.*?)" + re.escape(SUMMARY_END), content, re.DOTALL)
    if not block:
        return existing
    # Filas con formato: | TICKER | $X | $X | +X% | señal | P&L | fecha |
    # Excluir header y separador (|---|---|...)
    for line in block.group(1).splitlines():
        m = re.match(r"\|\s*([A-Z][A-Z0-9\-]*)\s*\|.*\|\s*[+\-][\d\.]+%\s*\|", line)
        if m and m.group(1) != "Ticker":
            existing[m.group(1)] = line
    return existing


def update_summary_table(analisis_list):
    with open(MD_FILE, encoding="utf-8") as f:
        content = f.read()

    # Cargar entradas previas y sobreescribir solo las actualizadas
    existing = _parse_existing_summary(content)
    today    = datetime.now().strftime("%Y-%m-%d")

    for d in analisis_list:
        icon   = SIGNAL_ICON.get(d["recomendacion"], "⚠️")
        upside = f"{d['upside']:+.1f}%"
        pl     = f"{d['pl_pct']:+.1f}%" if d["pl_pct"] is not None else "—"
        existing[d["symbol"]] = (
            f"| {d['symbol']} | ${d['precio_actual']:.2f} | ${d['precio_objetivo']:.2f} "
            f"| {upside} | {icon} {d['recomendacion']} | {pl} | {today} |"
        )

    # Ordenar: upside descendente (extraer valor numérico de la fila)
    def row_upside(row):
        m = re.search(r"\|\s*([+\-][\d\.]+)%\s*\|", row)
        return float(m.group(1)) if m else 0

    sorted_rows = sorted(existing.values(), key=row_upside, reverse=True)

    table = (
        f"{SUMMARY_START}\n"
        f"## Resumen — Última recomendación por ticker\n\n"
        f"| Ticker | Precio actual | Precio objetivo | Upside | Señal | P&L posición | Fecha |\n"
        f"|--------|--------------|----------------|--------|-------|-------------|-------|\n"
        + "\n".join(sorted_rows)
        + f"\n\n*Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        f"{SUMMARY_END}"
    )

    if SUMMARY_START in content and SUMMARY_END in content:
        pattern = re.escape(SUMMARY_START) + r".*?" + re.escape(SUMMARY_END)
        content = re.sub(pattern, table, content, flags=re.DOTALL)
    else:
        content = content.replace("## Propuestas", table + "\n\n---\n\n## Propuestas")

    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Tabla resumen actualizada en analisis_activos.md ({len(existing)} tickers)")


# ── GENERAR ARRAYS JS PARA INDEX.HTML ────────────────────────────────────────

SIGNAL_JS = {"COMPRAR MÁS": "buy", "MANTENER": "hold", "VENDER": "sell"}
SIGNAL_ORDER = {"sell": 0, "buy": 1, "hold": 2, "warn": 3}


def _escape(s):
    return str(s).replace('"', '\\"').replace('\n', ' ')


def update_dashboard(portfolio_mem, analisis_list, today):
    recs_map = {d["symbol"]: d for d in analisis_list}

    # portfolio[] sorted by value desc
    sorted_port = sorted(portfolio_mem.items(), key=lambda x: -x[1]["value"])
    port_lines  = []
    for ticker, p in sorted_port:
        sig   = SIGNAL_JS.get(recs_map.get(ticker, {}).get("recomendacion", ""), "hold")
        alert = "true" if p["alert"] else "false"
        port_lines.append(
            f'  {{ ticker:"{ticker}", name:"{_escape(p["name"])}", shares:{p["shares"]}, '
            f'buyPrice:{p["buyPrice"]}, price:{p["price"]}, value:{p["value"]}, '
            f'pct:{p["pct"]}, ret:{p["ret"]}, alert:{alert} }},'
        )

    # recommendations[] sorted: sell → buy → hold → warn
    recs_sorted = sorted(
        analisis_list,
        key=lambda d: (SIGNAL_ORDER.get(SIGNAL_JS.get(d["recomendacion"], "hold"), 3), -abs(d["upside"]))
    )
    recs_lines = []
    for d in recs_sorted:
        sig    = SIGNAL_JS.get(d["recomendacion"], "hold")
        fund   = _escape(f"Upside de {d['upside']:.1f}% respecto al precio objetivo de consenso de analistas.")
        riesgo = _escape("Revisar si el precio objetivo fue actualizado recientemente.")
        recs_lines.append(
            f'  {{ ticker:"{d["symbol"]}", upside:{d["upside"]:.1f}, signal:"{sig}", '
            f'target:{d["precio_objetivo"]:.2f}, currentPrice:{d["precio_actual"]:.2f}, '
            f'analysts:{d["num_analistas"] or 0},\n'
            f'    fundamento:"{fund}",\n'
            f'    riesgo:"{riesgo}" }},'
        )

    new_port = "const portfolio = [\n" + "\n".join(port_lines) + "\n];"
    new_recs = "const recommendations = [\n" + "\n".join(recs_lines) + "\n];"

    with open(HTML_FILE, encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r"const portfolio = \[.*?\];",      new_port, html, flags=re.DOTALL)
    html = re.sub(r"const recommendations = \[.*?\];", new_recs, html, flags=re.DOTALL)
    html = re.sub(r"Última actualización: \d{4}-\d{2}-\d{2}", f"Última actualización: {today}", html)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [OK] Dashboard actualizado en app/index.html")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=== Analizador de Activos v2 ===\n")
    portfolio_mem, total_value = parse_memory()

    if not portfolio_mem:
        print("[!] No se pudo leer el portafolio de memory.md")
        return

    print(f"Portafolio: {len(portfolio_mem)} activos | Valor total: ${total_value:,.2f}\n")

    entrada = input(
        "Tickers a analizar (separados por coma, o 'todos' para el portafolio completo):\n> "
    ).strip()

    if entrada.lower() == "todos":
        tickers = [t for t in portfolio_mem if "-VRS" not in t]
    else:
        tickers = [t.strip().upper() for t in entrada.split(",") if t.strip()]

    analisis_list = []
    needs_web     = []

    for symbol in tickers:
        print(f"\nConsultando {symbol}...")
        d = analizar(symbol, portfolio_mem, total_value)
        if d:
            propuesta = formatear_propuesta(d)
            print(propuesta)
            with open(MD_FILE, "a", encoding="utf-8") as f:
                f.write(propuesta)
            analisis_list.append(d)
        else:
            needs_web.append(symbol)
            print(f"  → Sin datos en yfinance. Usar skill PrecioWEB como fallback.")

    if needs_web:
        print(f"\n⚠️  Tickers sin datos en yfinance (requieren PrecioWEB):")
        for t in needs_web:
            print(f"   - {t}")

    if analisis_list:
        print()
        update_summary_table(analisis_list)

        resp = input("\n¿Actualizar app/index.html con los datos actuales? [s/N]: ").strip().lower()
        if resp == "s":
            today = datetime.now().strftime("%Y-%m-%d")
            update_dashboard(portfolio_mem, analisis_list, today)

    print("\nListo.")


if __name__ == "__main__":
    main()
