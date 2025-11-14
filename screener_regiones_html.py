import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ==========================
# 1. Configuración de regiones y tickers
# ==========================

REGIONS = {
    "USA": {
        "AAPL":  "Apple (USA)",
        "MSFT":  "Microsoft (USA)",
        "GOOGL": "Alphabet Class A (USA)",
        "AMZN":  "Amazon.com (USA)",
        "NVDA":  "NVIDIA (USA)",
        "META":  "Meta Platforms (USA)",
        "BRK-B": "Berkshire Hathaway B (USA)",
        "JPM":   "JPMorgan Chase (USA)",
        "V":     "Visa (USA)",
        "MA":    "Mastercard (USA)",
        "UNH":   "UnitedHealth Group (USA)",
        "HD":    "Home Depot (USA)",
        "PG":    "Procter & Gamble (USA)",
        "DIS":   "Walt Disney (USA)",
        "ADBE":  "Adobe (USA)",
        "NFLX":  "Netflix (USA)",
        "TSLA":  "Tesla (USA)",
        "XOM":   "Exxon Mobil (USA)",
        "PFE":   "Pfizer (USA)",
        "CSCO":  "Cisco Systems (USA)",
    },

    "ESPANA": {
        "SAN.MC":  "Banco Santander (España)",
        "BBVA.MC": "BBVA (España)",
        "IBE.MC":  "Iberdrola (España)",
        "ITX.MC":  "Inditex (España)",
        "TEF.MC":  "Telefónica (España)",
        "REP.MC":  "Repsol (España)",
        "FER.MC":  "Ferrovial (España)",
        "ACS.MC":  "ACS (España)",
        "GRF.MC":  "Grifols (España)",
        "MEL.MC":  "Meliá Hotels (España)",
        "CLNX.MC": "Cellnex (España)",
        "AENA.MC": "Aena (España)",
        "MAP.MC":  "Mapfre (España)",
        "AMS.MC":  "Amadeus (España)",
        "VIS.MC":  "Viscofan (España)",
        "ENG.MC":  "Enagás (España)",
        "ELE.MC":  "Endesa (España)",
        "BKT.MC":  "Bankinter (España)",
        "CABK.MC": "CaixaBank (España)",
        "COL.MC":  "Inmobiliaria Colonial (España)",
    },

    "FRANCIA": {
        "MC.PA":   "LVMH (Francia)",
        "OR.PA":   "L'Oréal (Francia)",
        "SAN.PA":  "Sanofi (Francia)",
        "AIR.PA":  "Airbus (Francia)",
        "AI.PA":   "Air Liquide (Francia)",
        "BNP.PA":  "BNP Paribas (Francia)",
        "ENGI.PA": "Engie (Francia)",
        "DG.PA":   "Vinci (Francia)",
        "SU.PA":   "Schneider Electric (Francia)",
        "CAP.PA":  "Capgemini (Francia)",
        "DSY.PA":  "Dassault Systèmes (Francia)",
        "RI.PA":   "Pernod Ricard (Francia)",
        "GLE.PA":  "Société Générale (Francia)",
        "SGO.PA":  "Saint-Gobain (Francia)",
        "VIV.PA":  "Vivendi (Francia)",
        "ML.PA":   "Michelin (Francia)",
        "RNO.PA":  "Renault (Francia)",
        "ORA.PA":  "Orange (Francia)",
        "HO.PA":   "Thales (Francia)",
        "UL.PA":   "Unibail-Rodamco-Westfield (Francia)",
    },

    "ALEMANIA": {
        "SAP.DE":   "SAP (Alemania)",
        "SIE.DE":   "Siemens (Alemania)",
        "ALV.DE":   "Allianz (Alemania)",
        "DTE.DE":   "Deutsche Telekom (Alemania)",
        "BAS.DE":   "BASF (Alemania)",
        "BMW.DE":   "BMW (Alemania)",
        "VOW3.DE":  "Volkswagen (Alemania)",
        "BAYN.DE":  "Bayer (Alemania)",
        "DBK.DE":   "Deutsche Bank (Alemania)",
        "RWE.DE":   "RWE (Alemania)",
        "LHA.DE":   "Lufthansa (Alemania)",
        "MUV2.DE":  "Munich Re (Alemania)",
        "FRE.DE":   "Fresenius (Alemania)",
        "FME.DE":   "Fresenius Medical Care (Alemania)",
        "IFX.DE":   "Infineon (Alemania)",
        "HEI.DE":   "Heidelberg Materials (Alemania)",
        "HEN3.DE":  "Henkel (Alemania)",
        "BEI.DE":   "Beiersdorf (Alemania)",
        "MRK.DE":   "Merck KGaA (Alemania)",
        "LIN.DE":   "Linde (Alemania)",
    },

    "EUROPA_CONTINENTAL": {
        "ASML.AS":   "ASML (Países Bajos)",
        "PHIA.AS":   "Philips (Países Bajos)",
        "AD.AS":     "Ahold Delhaize (Países Bajos)",
        "NOVN.SW":   "Novartis (Suiza)",
        "ROG.SW":    "Roche (Suiza)",
        "NESN.SW":   "Nestlé (Suiza)",
        "ENEL.MI":   "Enel (Italia)",
        "ENI.MI":    "ENI (Italia)",
        "ISP.MI":    "Intesa Sanpaolo (Italia)",
        "UCG.MI":    "UniCredit (Italia)",
        "VWS.CO":    "Vestas (Dinamarca)",
        "NOVO-B.CO": "Novo Nordisk B (Dinamarca)",
        "TELIA.ST":  "Telia (Suecia)",
        "ERIC-B.ST": "Ericsson B (Suecia)",
        "NOKIA.HE":  "Nokia (Finlandia)",
        "SWEDA.ST":  "Swedbank (Suecia)",
        "ATCO-A.ST": "Atlas Copco A (Suecia)",
        "VOLV-B.ST": "Volvo B (Suecia)",
        "HEXA-B.ST": "Hexagon B (Suecia)",
        "FING-B.ST": "Nordea (Nordic)",
    },

    "ASIA": {
        "7203.T":     "Toyota (Japón)",
        "6758.T":     "Sony (Japón)",
        "9984.T":     "SoftBank (Japón)",
        "8306.T":     "Mitsubishi UFJ (Japón)",
        "9432.T":     "Nippon Telegraph & Tel. (Japón)",
        "005930.KS":  "Samsung Electronics (Corea)",
        "000660.KS":  "SK Hynix (Corea)",
        "035420.KS":  "Naver (Corea)",
        "TSM":        "TSMC (Taiwán, ADR)",
        "2303.TW":    "United Microelectronics (Taiwán)",
        "0700.HK":    "Tencent (Hong Kong)",
        "0939.HK":    "China Construction Bank (HK)",
        "2318.HK":    "Ping An Insurance (HK)",
        "1299.HK":    "AIA Group (HK)",
        "3988.HK":    "Bank of China (HK)",
        "BABA":       "Alibaba (USA, China)",
        "JD":         "JD.com (USA, China)",
        "NTES":       "NetEase (USA, China)",
        "HMC":        "Honda (Japón, USA)",
        "TM":         "Toyota (USA ADR)",
    },

    "EMERGENTES": {
        "RELIANCE.NS": "Reliance Industries (India)",
        "INFY.NS":     "Infosys (India)",
        "TCS.NS":      "Tata Consultancy Services (India)",
        "HDFCBANK.NS": "HDFC Bank (India)",
        "ICICIBANK.NS":"ICICI Bank (India)",
        "VALE":        "Vale (Brasil)",
        "PETR4.SA":    "Petrobras PN (Brasil)",
        "ITUB":        "Itaú Unibanco (Brasil)",
        "BBD":         "Bradesco (Brasil)",
        "MELI":        "MercadoLibre (LatAm, USA)",
        "YPF":         "YPF (Argentina)",
        "GGAL":        "Grupo Financiero Galicia (Argentina)",
        "PDD":         "PDD Holdings (China)",
        "NIO":         "NIO (China)",
        "EDU":         "New Oriental (China)",
        "SID":         "CSN (Brasil)",
        "GGB":         "Gerdau (Brasil)",
        "SBS":         "Sabesp (Brasil)",
        "EC":          "Ecopetrol (Colombia)",
        "SSL":         "Sasol (Sudáfrica)",
    },
}

# Región activa: CAMBIA ESTO para elegir mercado o usar ALL
# Opciones: "USA", "ESPANA", "FRANCIA", "ALEMANIA",
#           "EUROPA_CONTINENTAL", "ASIA", "EMERGENTES",
#           "EUROPA_OCCIDENTAL", "ALL"
ACTIVE_REGION = "ALL"

# Número de acciones que consideramos "principales" para el HTML
TOP_N = 30


# ==========================
# SEGUIMIENTO DE MI CARTERA
# ==========================
# Formato:
# "TICKER": {"nombre": "...", "precio_compra": ..., "cantidad": ...}

MI_CARTERA = {
    "BKT.MC": {
        "nombre": "Bankinter (España)",
        "precio_compra": 13.50,
        "cantidad": 300 / 13.50   # convertir 300€ a nº acciones
    }
}





# ==========================
# 2. Construir lista de tickers según región
# ==========================

def merge_regions(region_names):
    merged = {}
    for r in region_names:
        merged.update(REGIONS[r])
    return merged

if ACTIVE_REGION == "EUROPA_OCCIDENTAL":
    STOCKS = merge_regions(["ESPANA", "FRANCIA", "ALEMANIA", "EUROPA_CONTINENTAL"])
elif ACTIVE_REGION == "ALL":
    STOCKS = merge_regions(list(REGIONS.keys()))
else:
    STOCKS = REGIONS.get(ACTIVE_REGION, {})

if not STOCKS:
    raise ValueError(f"Región {ACTIVE_REGION} no encontrada o sin tickers.")

print(f"Región activa: {ACTIVE_REGION} | Número de acciones: {len(STOCKS)}")

# ==========================
# 3. Parámetros comunes
# ==========================

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
# 4. Descarga de datos
# ==========================

tickers = list(STOCKS.keys())

end = datetime.today()
start = end - timedelta(days=MAX_DAYS * 2)

print("Descargando datos de:", ", ".join(tickers))

data = yf.download(
    tickers=tickers,
    start=start.strftime("%Y-%m-%d"),
    end=end.strftime("%Y-%m-%d"),
    auto_adjust=True
)

if isinstance(data.columns, pd.MultiIndex):
    prices = data["Close"]
    volumes = data["Volume"]
else:
    prices = data["Close"]
    volumes = data["Volume"]

prices = prices.dropna(axis=1, how="all")
volumes = volumes.dropna(axis=1, how="all")

# ==========================
# 5. Funciones auxiliares
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
# 6. Cálculo por acción
# ==========================

rows = []

for ticker, nombre in STOCKS.items():
    if ticker not in prices.columns:
        print(f"Aviso: no hay precios para {ticker}")
        continue

    s_price = prices[ticker].dropna()
    if s_price.empty:
        continue

    s_vol = volumes[ticker].dropna() if ticker in volumes.columns else pd.Series(dtype=float)

    last_price = s_price.iloc[-1]

    # Rentabilidades
    rets = {}
    for label, bars in PERIODOS.items():
        rets[label] = calc_return(s_price, bars)

    vol_anual = calc_volatility(s_price, 252)
    ma50 = calc_moving_average(s_price, 50)
    ma200 = calc_moving_average(s_price, 200)

    # Volumen: hoy vs media 20 días
    if not s_vol.empty:
        vol_hoy = s_vol.iloc[-1]
        vol_med20 = s_vol.tail(20).mean() if len(s_vol) >= 5 else np.nan
        vol_ratio = vol_hoy / vol_med20 if vol_med20 and not np.isnan(vol_med20) else np.nan
    else:
        vol_hoy = np.nan
        vol_med20 = np.nan
        vol_ratio = np.nan

    # Trend score (0 a 3)
    trend_score = 0
    if not np.isnan(ma200) and last_price > ma200:
        trend_score += 1
    if not np.isnan(ma50) and last_price > ma50:
        trend_score += 1
    if not np.isnan(rets["1M"]) and rets["1M"] > 0:
        trend_score += 1

    # Interest score (0 a 6)
    interest_score = trend_score
    if not np.isnan(rets["3M"]) and rets["3M"] > 0:
        interest_score += 1
    if not np.isnan(rets["1W"]) and rets["1W"] > 0:
        interest_score += 1
    if not np.isnan(vol_ratio) and vol_ratio > 1.5:
        interest_score += 1

    row = {
        "Ticker": ticker,
        "Nombre": nombre,
        "Precio": last_price,
        "Ret_1Y_%": rets["1Y"] * 100,
        "Ret_6M_%": rets["6M"] * 100,
        "Ret_3M_%": rets["3M"] * 100,
        "Ret_1M_%": rets["1M"] * 100,
        "Ret_1W_%": rets["1W"] * 100,
        "Ret_1D_%": rets["1D"] * 100,
        "Vol_Anual_%": vol_anual * 100 if not np.isnan(vol_anual) else np.nan,
        "Vol_Hoy": vol_hoy,
        "Vol_Med20": vol_med20,
        "Vol_Ratio": vol_ratio,
        "MA50": ma50,
        "MA200": ma200,
        "Trend_Score_0_3": trend_score,
        "Interest_Score_0_6": interest_score,
    }

    rows.append(row)

df = pd.DataFrame(rows)

# ==========================
# Cálculo de cartera personal
# ==========================
cartera_rows = []

for ticker, info in MI_CARTERA.items():
    if ticker not in df["Ticker"].values:
        continue
    
    fila = df[df["Ticker"] == ticker].iloc[0]

    precio_actual = fila["Precio"]
    precio_compra = info["precio_compra"]
    cantidad = info["cantidad"]

    valor_actual = precio_actual * cantidad
    valor_inicial = precio_compra * cantidad

    rentabilidad_pct = ((precio_actual / precio_compra) - 1) * 100
    ganancia = valor_actual - valor_inicial

    cartera_rows.append({
        "Ticker": ticker,
        "Nombre": info["nombre"],
        "Precio_compra": precio_compra,
        "Precio_actual": round(precio_actual, 2),
        "Cantidad": round(cantidad, 4),
        "Inversion_inicial": round(valor_inicial, 2),
        "Valor_actual": round(valor_actual, 2),
        "Ganancia_€": round(ganancia, 2),
        "Rentabilidad_%": round(rentabilidad_pct, 2)
    })

df_cartera = pd.DataFrame(cartera_rows)


if df.empty:
    print("No se han podido calcular métricas. Revisa los tickers de la región.")
    raise SystemExit

# ==========================
# 7. Ordenar por “interés” y seleccionar principales
# ==========================

df = df.sort_values(
    ["Interest_Score_0_6", "Ret_3M_%"],
    ascending=[False, False]
)

df_top = df.head(TOP_N).copy()

# Redondeos
cols_pct = [c for c in df.columns if c.endswith("_%")]
df[cols_pct] = df[cols_pct].round(2)
df_top[cols_pct] = df_top[cols_pct].round(2)

for col in ["Precio", "MA50", "MA200", "Vol_Anual_%", "Vol_Ratio"]:
    if col in df.columns:
        df[col] = df[col].round(2)
        df_top[col] = df_top[col].round(2)

if "Vol_Hoy" in df.columns:
    df["Vol_Hoy"] = df["Vol_Hoy"].round(0)
    df_top["Vol_Hoy"] = df_top["Vol_Hoy"].round(0)
if "Vol_Med20" in df.columns:
    df["Vol_Med20"] = df["Vol_Med20"].round(0)
    df_top["Vol_Med20"] = df_top["Vol_Med20"].round(0)



# ==========================
# 8. Salida en consola (opcional)
# ==========================

pd.set_option("display.max_rows", None)
print(f"\n=== Screener de acciones | Región: {ACTIVE_REGION} (más interesantes arriba) ===\n")
cols_show = [
    "Ticker", "Nombre", "Precio",
    "Ret_1Y_%", "Ret_6M_%", "Ret_3M_%", "Ret_1M_%", "Ret_1W_%",
    "Vol_Anual_%", "Vol_Ratio",
    "Trend_Score_0_3", "Interest_Score_0_6"
]
print(df[cols_show].to_string(index=False))







# ==========================
# 9. Generar HTML de las principales (sin Styler)
# ==========================

# Seleccionamos columnas a mostrar en el HTML
cols_html = [
    "Ticker", "Nombre", "Precio",
    "Ret_1Y_%", "Ret_6M_%", "Ret_3M_%", "Ret_1M_%", "Ret_1W_%", "Ret_1D_%",
    "Vol_Anual_%", "Vol_Ratio",
    "Trend_Score_0_3", "Interest_Score_0_6"
]

# Nos quedamos solo con esas columnas (las que existan)
cols_html = [c for c in cols_html if c in df_top.columns]

# Aseguramos 2 decimales en números importantes
for col in ["Precio", "Vol_Anual_%", "Vol_Ratio",
            "Ret_1Y_%", "Ret_6M_%", "Ret_3M_%", "Ret_1M_%", "Ret_1W_%", "Ret_1D_%"]:
    if col in df_top.columns:
        df_top[col] = df_top[col].round(2)

# Generamos la tabla HTML simple
tabla_html = df_top[cols_html].to_html(
    index=False,
    border=0,
    classes="tabla-principal"
)
# Resumen rápido
media_3m = df["Ret_3M_%"].mean()
media_1y = df["Ret_1Y_%"].mean()
n_altos = (df["Interest_Score_0_6"] >= 4).sum()

top5 = df_top.head(5)[["Nombre", "Interest_Score_0_6", "Ret_3M_%"]]
top5_items_html = "".join(
    f"<li>{row['Nombre']}: score {int(row['Interest_Score_0_6'])}, {row['Ret_3M_%']:.2f}% en 3M</li>"
    for _, row in top5.iterrows()
)

summary_html = f"""
<div class="summary-box">
    <h2>Resumen rápido</h2>
    <p>Se han analizado <strong>{len(df)}</strong> acciones de la región <strong>{ACTIVE_REGION}</strong>.
       La rentabilidad media es de <strong>{media_3m:.2f}%</strong en 3 meses
       y de <strong>{media_1y:.2f}%</strong en el último año.</p>

    <p>Hay <strong>{n_altos}</strong> acciones con <strong>Interest_Score ≥ 4</strong> (combinan buena tendencia y/o volumen.</p>

    <p><strong>Top 5 por interés:</strong></p>
    <ul>
        {top5_items_html}
    </ul>
</div>
"""

tabla_cartera_html = df_cartera.to_html(
    index=False,
    border=0,
    classes="tabla-principal"
)


fecha_str = datetime.today().strftime("%d/%m/%Y")

html_page = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Screener acciones – {ACTIVE_REGION} – {fecha_str}</title>
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
        .summary-box {{
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
            padding: 12px 16px;
            border-radius: 10px;
            background-color: #f7f9fc;
            border: 1px solid #d0d7e2;
            font-size: 0.95rem;
        }}
        .summary-box ul {{
            margin-top: 0.4rem;
            margin-bottom: 0.8rem;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 0.9rem;
        }}
        /* === Estilos tabla principal (to_html) === */
        table.tabla-principal {{
            border-collapse: collapse;
            width: 100%;
            font-size: 0.9rem;
            margin-top: 1rem;
        }}

        table.tabla-principal th {{
            background-color: #222;
            color: #fff;
            padding: 8px;
            text-align: center;
        }}

        table.tabla-principal td {{
            padding: 6px;
            border-bottom: 1px solid #eee;
            text-align: right;
        }}

        table.tabla-principal tbody tr:nth-child(even) {{
            background-color: #f5f5f5;
        }}

        /* Primera y segunda columna alineadas a la izquierda */
        table.tabla-principal td:nth-child(1),
        table.tabla-principal td:nth-child(2) {{
            text-align: left;
        }}

    </style>
</head>
<body>
    <div class="container">
        <span class="badge">Screener de acciones</span>
        <h1>Principales acciones por interés</h1>
        <div class="subtitle">Región: {ACTIVE_REGION} &nbsp;·&nbsp; Fecha: {fecha_str}</div>

        {summary_html}

        <h2>Top {TOP_N} acciones más interesantes</h2>
        {tabla_html}
        <h2>Mi cartera (seguimiento personal)</h2>
        {tabla_cartera_html}
    </div>
</body>
</html>
"""

output_file = "screener_acciones.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_page)

print(f"\nInforme HTML generado: {output_file}")

