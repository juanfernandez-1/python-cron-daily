import re
import io
import sys
import time
import math
import datetime as dt
from dateutil import rrule
import requests
import pandas as pd

BASE_URL = "https://www.omie.es/es/file-download?filename=marginalpdbc_{ymd}.1&parents=marginalpdbc"

def download_omie_file(d: dt.date, retries=3, backoff=3) -> bytes:
    """Descarga el fichero marginalpdbc_YYYYMMDD.1 (ES) y devuelve bytes."""
    ymd = d.strftime("%Y%m%d")
    url = BASE_URL.format(ymd=ymd)
    last_err = None
    for i in range(retries):
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            return r.content
        except Exception as e:
            last_err = e
            time.sleep(backoff * (2**i))
    raise RuntimeError(f"No se pudo descargar {ymd}: {last_err}")

def parse_marginalpdbc(content: bytes, date_hint: dt.date) -> pd.DataFrame:
    """
    Parser para ficheros tipo:
        MARGINALPDBC;
        YYYY;MM;DD;PERIODO;PRECIO_ES;PRECIO_PT;
    Soporta:
      - 96 periodos (15 min) o 24 periodos (1 hora)
      - Punto o coma decimal
      - 1 o 2 columnas de precio (ES, PT)
    Devuelve DataFrame: fecha, periodo, datetime_inicio, precio_es_eur_mwh, precio_pt_eur_mwh
    """
    import math
    text = content.decode("latin-1", errors="ignore").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # Quitar cabecera "MARGINALPDBC;" si aparece
    if lines and lines[0].upper().startswith("MARGINALPDBC"):
        lines = lines[1:]

    rows = []
    for ln in lines:
        if ';' not in ln:
            continue
        # Acepta líneas que acaban con ';' (último campo vacío)
        parts = [p.strip() for p in ln.split(';') if p.strip() != ""]
        # Esperado: YYYY;MM;DD;PERIODO;PRECIO_ES(;PRECIO_PT)?
        if len(parts) < 5:
            continue
        y, m, d = parts[0], parts[1], parts[2]
        per = parts[3]
        try:
            year = int(y); month = int(m); day = int(d)
            periodo = int(per)
        except ValueError:
            continue

        def to_float(x):
            try:
                return float(x.replace(',', '.'))
            except Exception:
                return math.nan

        precio_es = to_float(parts[4])
        precio_pt = to_float(parts[5]) if len(parts) >= 6 else math.nan

        rows.append((dt.date(year, month, day), periodo, precio_es, precio_pt))

    if not rows:
        raise ValueError("No se reconocieron registros YYYY;MM;DD;periodo;precio...")

    df = pd.DataFrame(rows, columns=["fecha", "periodo", "precio_es_eur_mwh", "precio_pt_eur_mwh"])

    # Detectar nº de periodos por día para construir el datetime de inicio del periodo
    # - Si 96 -> pasos de 15 min
    # - Si 24 -> pasos de 60 min
    # (Si otro número, aproximamos duración como 24h/num_periodos)
    by_day = df.groupby("fecha")["periodo"].max().to_dict()
    def period_to_dt(fecha, periodo, pmax):
        base = dt.datetime.combine(fecha, dt.time(0, 0))
        if pmax == 96:
            delta = dt.timedelta(minutes=15*(periodo-1))
        elif pmax == 24:
            delta = dt.timedelta(hours=periodo-1)
        else:
            # duración media del periodo
            step_minutes = int(round(24*60 / pmax))
            delta = dt.timedelta(minutes=step_minutes*(periodo-1))
        return base + delta

    df["datetime_inicio"] = [
        period_to_dt(f, p, by_day[f]) for f, p in zip(df["fecha"], df["periodo"])
    ]

    # Orden y limpieza
    df = df.sort_values(["fecha", "periodo"]).reset_index(drop=True)

    return df


def precios_omie_tabla(desde: str, hasta: str) -> pd.DataFrame:
    """
    Descarga y devuelve una tabla con:
    fecha, periodo, datetime_inicio, precio_es_eur_mwh, precio_pt_eur_mwh
    para el rango [desde, hasta], inclusive.
    """
    d0 = dt.date.fromisoformat(desde)
    d1 = dt.date.fromisoformat(hasta)
    frames = []
    for d in rrule.rrule(rrule.DAILY, dtstart=d0, until=d1):
        d = d.date()
        try:
            blob = download_omie_file(d)
            df = parse_marginalpdbc(blob, d)   # <- ahora devuelve 'periodo' y 'datetime_inicio'
            frames.append(df)
        except Exception as e:
            print(f"[AVISO] {d}: {e}", file=sys.stderr)

    if not frames:
        raise RuntimeError("No se obtuvo ningún día válido.")

    out = pd.concat(frames, ignore_index=True)
    # Orden natural por fecha y periodo (no por 'hora')
    out = out.sort_values(["fecha", "periodo"]).reset_index(drop=True)
    return out


def a_tabla_horaria(tabla_15m: pd.DataFrame, columna="precio_es_eur_mwh") -> pd.DataFrame:
    """
    Agrega 4 periodos de 15' a una hora (promedio simple).
    Devuelve: fecha, hora, precio_eur_mwh
    """
    if "hora" not in tabla_15m.columns:
        tabla_15m = tabla_15m.copy()
        tabla_15m["hora"] = tabla_15m["datetime_inicio"].dt.hour

    dfh = (tabla_15m
           .groupby(["fecha", "hora"], as_index=False)[columna]
           .mean()
           .rename(columns={columna: "precio_eur_mwh"})
           .sort_values(["fecha", "hora"])
           .reset_index(drop=True))
    return dfh




if __name__ == "__main__":
    # EJEMPLO: cambiar por el rango que quieras
    tabla = precios_omie_tabla("2025-09-30", "2025-10-02")
    print(tabla.head(30))
    # Si quieres guardarlo:
    tabla.to_csv("C:/Users/jfernandezp/Downloads/precios_omie_diario.csv", index=False)
    print("Guardado en precios_omie_diario.csv")

    # Tabla promedio horario:
    tabla = precios_omie_tabla("2025-09-30", "2025-10-02")
    tabla_horas = a_tabla_horaria(tabla, columna="precio_es_eur_mwh")  # o "precio_pt_eur_mwh"
    tabla_horas.to_csv("C:/Users/jfernandezp/Downloads/precios_omie_diario_promedio_horario.csv", index=False)
    print(tabla_horas.head(30))

