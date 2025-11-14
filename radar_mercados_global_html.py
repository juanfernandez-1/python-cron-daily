import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ==========================
# 1. Configuración
# ==========================

TICKERS = {
    "^GSPC": "S&P 500 (USA)",
    "^NDX": "Nasdaq 100 (USA)",
    "^DJI": "Dow Jones (USA)",
    "^STOXX50E": "EuroStoxx 50 (EU)",
    "^GDAXI": "DAX (Alemania)",
    "^FCHI": "CAC 40 (Francia)",
    "^FTSE": "FTSE 100 (UK)",
    "^N225": "Nikkei 225 (Japón)",
    "^HSI": "Hang Seng (Hong Kong)",
    "SPY": "SPY (ETF S&P 500)",
    "QQQ": "QQQ (ETF Nasdaq 100)",
    "EEM": "EEM (Emerging Markets ETF)",
}

MAX_DAYS = 260  # ~ 1 año de sesiones

PERIODOS = {
    "1Y": 252,
    "6M": 126,
    "3M": 63,
    "1M": 21,
    "1W": 5,
    "1D": 1,
}

# ==========================
# 2. Descarga de datos
# ==========================

end = datetime.today()
start = end - timedelta(days=MAX_DAYS * 2)  # margen extra por festivos

data = yf.download(
    tickers=list(TICKERS.keys()),
    start=start.strftime("%Y-%m-%d"),
    end=end.strftime("%Y-%m-%d"),
    auto_adjust=True
)

# Precio de cierre
if isinstance(data.columns, pd.MultiIndex):
    prices = data["Close"]
else:
    prices = data

prices = prices.dropna(axis=1, how="all")

# ==========================
# 3. Funciones auxiliares
# ==========================

def calc_return(series: pd.Series, bars: int):
    series = series.dropna()
    if len(series) < bars + 1:
        return np.nan
    end_price = series.iloc[-1]
    start_price = series.iloc[-bars - 1]
    return (end_price / start_price) - 1.0

def calc_volatility(series: pd.Series, bars: int = 252):
    series = series.dropna()
    if len(series) < 2:
        return np.nan
    returns = series.pct_change().dropna()
    if len(returns) < bars:
        std = returns.std()
    else:
        std = returns.iloc[-bars:].std()
    return std * np.sqrt(252)

def calc_moving_average(series: pd.Series, window: int):
    series = series.dropna()
    if len(series) < window:
        return np.nan
    return series.iloc[-window:].mean()

# ==========================
# 4. Cálculo de KPIs por ticker
# ==========================

rows = []

for ticker, name in TICKERS.items():
    if ticker not in prices.columns:
        continue

    s = prices[ticker].dropna()
    if s.empty:
        continue

    last_price = s.iloc[-1]

    # Rentabilidades
    returns = {}
    for label, bars in PERIODOS.items():
        returns[label] = calc_return(s, bars)

    vol = calc_volatility(s, 252)
    ma50 = calc_moving_average(s, 50)
    ma200 = calc_moving_average(s, 200)

    trend_score = 0
    if not np.isnan(ma200) and last_price > ma200:
        trend_score += 1
    if not np.isnan(ma50) and last_price > ma50:
        trend_score += 1
    if not np.isnan(returns["1M"]) and returns["1M"] > 0:
        trend_score += 1

    row = {
        "Ticker": ticker,
        "Nombre": name,
        "Precio": last_price,
        "Ret_1Y_%": returns["1Y"] * 100 if not np.isnan(returns["1Y"]) else np.nan,
        "Ret_6M_%": returns["6M"] * 100,
        "Ret_3M_%": returns["3M"] * 100,
        "Ret_1M_%": returns["1M"] * 100,
        "Ret_1W_%": returns["1W"] * 100,
        "Ret_1D_%": returns["1D"] * 100,
        "Vol_Anual_%": vol * 100 if not np.isnan(vol) else np.nan,
        "MA50": ma50,
        "MA200": ma200,
        "Trend_Score_0_3": trend_score,
    }

    rows.append(row)

df = pd.DataFrame(rows)

# Orden por fuerza a 3 meses
df = df.sort_values("Ret_3M_%", ascending=False)

# Redondeos
cols_pct = [c for c in df.columns if c.endswith("_%")]
df[cols_pct] = df[cols_pct].round(2)
df["Precio"] = df["Precio"].round(2)
df["MA50"] = df["MA50"].round(2)
df["MA200"] = df["MA200"].round(2)

# ==========================
# 5. Salida en consola (opcional)
# ==========================

pd.set_option("display.max_rows", None)
print("\n=== Radar global de mercados ===\n")
print(df.to_string(index=False))

# ==========================
# 6. Generar HTML bonito (menos decimales)
# ==========================

def color_ret(val):
    """
    Devuelve estilo CSS para colorear retornos:
    verde si >0, rojo si <0.
    """
    if pd.isna(val):
        return ""
    try:
        if val > 0:
            return "color: green; font-weight: 500;"
        elif val < 0:
            return "color: red; font-weight: 500;"
        else:
            return ""
    except:
        return ""

# Columnas que queremos con 2 decimales
cols_dos_decimales = ["Precio", "MA50", "MA200"] + cols_pct

styled = (
    df.style
      .map(color_ret, subset=cols_pct)  # colores verde/rojo
      .format("{:.2f}", subset=cols_dos_decimales)  # 🔹 aquí forzamos 2 decimales
      .set_table_styles([
          dict(selector="th", props=[("background-color", "#222"),
                                     ("color", "white"),
                                     ("padding", "8px"),
                                     ("text-align", "center")]),
          dict(selector="td", props=[("padding", "6px")]),
          dict(selector="tbody tr:nth-child(even)", props=[("background-color", "#f5f5f5")]),
      ])
      .set_properties(**{"text-align": "center"}, subset=["Ticker", "Nombre", "Trend_Score_0_3"])
      .set_properties(**{"text-align": "right"}, subset=cols_dos_decimales)
      .hide(axis="index")
)

tabla_html = styled.to_html()

fecha_str = datetime.today().strftime("%d/%m/%Y")

html_page = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Informe mercados – {fecha_str}</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            padding: 24px 28px 32px 28px;
        }}
        h1 {{
            margin-top: 0;
            margin-bottom: 0.2rem;
        }}
        h2 {{
            margin-top: 1.6rem;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 1.2rem;
        }}
        .badge {{
            display: inline-block;
            background-color: #222;
            color: #fff;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}
        .legend {{
            font-size: 0.9rem;
            color: #555;
            margin-top: 0.4rem;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 0.9rem;
        }}
        caption {{
            caption-side: top;
            text-align: left;
            font-weight: bold;
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <span class="badge">Radar de mercados</span>
        <h1>Informe global de mercados</h1>
        <div class="subtitle">Fecha: {fecha_str}</div>

        <p class="legend">
            <strong>Trend_Score_0_3</strong> suma puntos si:<br/>
            • Precio &gt; MA200 (largo plazo) &nbsp;• Precio &gt; MA50 (medio plazo) &nbsp;• Rentabilidad 1M &gt; 0.<br/>
            Valores más altos indican una tendencia más alcista.
        </p>

        <h2>Resumen por índices y ETFs</h2>
        {tabla_html}
    </div>
</body>
</html>
"""

output_file = "informe_mercados.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_page)

print(f"\nInforme HTML generado: {output_file}")

