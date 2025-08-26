from __future__ import annotations
import re
from pathlib import Path
from typing import List
import pandas as pd

RENAME_MAP = {
    "Tema - subtema": "tema",
    "Fecha Sentencia": "fecha",
    "Providencia": "providencia",
    "sintesis": "sintesis",
    "resuelve": "resuelve",
}

TEXT_COLS = ["tema", "sintesis", "resuelve"]
META_COLS = ["providencia", "fecha"]


def _strip_and_fix(s: str) -> str:
    if not isinstance(s, str):
        s = "" if pd.isna(s) else str(s)
    s = s.replace("\r", " ").replace("\n", " ").strip()
    s = re.sub(r"\s{2,}", " ", s)
    return s

def _to_iso_date(s: str) -> str:
    """(YYYY-MM-DD)"""
    s = _strip_and_fix(s)
    try:
        return pd.to_datetime(s, errors="coerce").date().isoformat()
    except Exception:
        return s
    
def load_cases(xlsx_path: str | Path) -> pd.DataFrame:
    xlsx_path = Path(xlsx_path)
    if not xlsx_path.exists():
        raise FileNotFoundError(f"File not found: {xlsx_path}")

    df = pd.read_excel(xlsx_path)

    # Renombrar columnas clave
    df = df.rename(columns=RENAME_MAP)

    # Asegurar columnas necesarias
    for c in ["tema", "fecha", "providencia", "sintesis", "resuelve"]:
        if c not in df.columns:
            df[c] = ""

    # Normalizaciones
    df["providencia"] = df["providencia"].map(_strip_and_fix)
    df["fecha"] = df["fecha"].map(_to_iso_date)
    for c in TEXT_COLS:
        df[c] = df[c].fillna("").map(_strip_and_fix)

    # Elimina duplicados obvios por (providencia + fecha + sintesis)
    df = df.drop_duplicates(subset=["providencia", "fecha", "sintesis"]).reset_index(drop=True)

    def _build_doc(r: pd.Series) -> str:
        return (
            f"PROVIDENCIA: {r.get('providencia','')}\n"
            f"FECHA: {r.get('fecha','')}\n"
            f"TEMA: {r.get('tema','')}\n\n"
            f"SINTESIS:\n{r.get('sintesis','')}\n\n"
            f"RESUELVE:\n{r.get('resuelve','')}"
        )

    df["doc"] = df.apply(_build_doc, axis=1)

    # Flags útiles para debug/consultas específicas del enunciado
    def _has(word: str, cols: List[str]) -> pd.Series:
        pat = re.compile(re.escape(word), flags=re.I)
        return df[cols].apply(lambda s: s.str.contains(pat) if s.dtype == "object" else False).any(axis=1)

    df["flag_redes_sociales"] = _has("redes sociales", ["tema", "sintesis", "resuelve"])
    df["flag_acoso_escolar"] = _has("acoso escolar", ["tema", "sintesis", "resuelve"])
    df["flag_piar"] = _has("PIAR", ["tema", "sintesis", "resuelve"])

    return df

def save_clean_outputs(df: pd.DataFrame, out_dir: str | Path = ".") -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Exportaciones útiles para inspección manual
    df.to_csv(out_dir / "cases_clean.csv", index=False)
    df.to_json(out_dir / "cases_clean.json", orient="records", force_ascii=False)


if __name__ == "__main__":
    # Ejecuta:  python app/etl.py
    path = Path("data/sentencias_pasadas.xlsx")
    df = load_cases(path)
    print("Filas:", len(df))
    print("Cols :", list(df.columns))
    print("\nMuestras:")
    print(df[["providencia","fecha","tema"]].head(5).to_string(index=False))

    # Conteos rápidos de las banderas clave del enunciado
    print("\nConteos por palabra clave:")
    for col in ["flag_redes_sociales", "flag_acoso_escolar", "flag_piar"]:
        print(f"  {col}: {int(df[col].sum())}")

    # Guardar versiones limpias (útil para revisar con Excel/VSCode)
    save_clean_outputs(df, out_dir="data")
    print("\nGuardado: data/cases_clean.csv y data/cases_clean.json")