#!/usr/bin/env python3
"""
Generate warehouse JS artifacts from Warehouse_Data.xls.

Outputs:
- warehouse-stores.js: window.WAREHOUSE_STORES = [...]
- warehouse-counts.js: window.WAREHOUSE_TOTAL_COUNT, window.WAREHOUSE_COUNTS_BY_BRAND
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _norm_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip())


def _norm_brand(s: str) -> str:
    return _norm_spaces(s).upper()


def _as_str(v: Any) -> str:
    if v is None:
        return ""
    # xlrd returns numbers for "text-like" cells sometimes; keep them readable.
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def _as_float(v: Any) -> float | None:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def read_rows(xls_path: Path) -> List[Dict[str, Any]]:
    try:
        import xlrd  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit("Missing dependency 'xlrd'. Install with: pip install xlrd") from e

    book = xlrd.open_workbook(str(xls_path))
    sh = book.sheet_by_index(0)
    headers = [_as_str(sh.cell_value(0, c)) for c in range(sh.ncols)]
    rows: List[Dict[str, Any]] = []
    for r in range(1, sh.nrows):
        d: Dict[str, Any] = {}
        for c, h in enumerate(headers):
            d[h] = sh.cell_value(r, c)
        rows.append(d)
    return rows


def build_stores(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: set[Tuple[str, str]] = set()

    for r in rows:
        brand = _norm_brand(r.get("Brand", ""))
        fc_id = _norm_spaces(_as_str(r.get("fc_id", "")))
        store_name = _norm_spaces(_as_str(r.get("Store Name", "")))

        lat = _as_float(r.get("latitude"))
        lng = _as_float(r.get("longitude"))

        if not brand or not fc_id:
            continue

        # De-dup by (brand, fc_id) to avoid UI overcounting.
        key = (brand, fc_id)
        if key in seen:
            continue
        seen.add(key)

        st: Dict[str, Any] = {"brand": brand, "fc_id": fc_id, "store_name": store_name}
        if lat is not None and lng is not None:
            st["lat"] = float(lat)
            st["lng"] = float(lng)
        else:
            # Keep fields present but null to preserve downstream expectations.
            st["lat"] = None
            st["lng"] = None
        out.append(st)

    # Stable sort for deterministic diffs.
    out.sort(key=lambda x: (str(x.get("brand", "")), str(x.get("fc_id", ""))))
    return out


def write_outputs(root: Path, stores: List[Dict[str, Any]]) -> None:
    counts = Counter([s["brand"] for s in stores if s.get("brand")])
    total = len(stores)

    # Ensure JSON is compact (files are loaded on page).
    stores_js = "// Auto-generated from Warehouse_Data.xls\nwindow.WAREHOUSE_STORES = " + json.dumps(
        stores, ensure_ascii=False, separators=(",", ":")
    ) + ";\n"
    counts_js = (
        "// Auto-generated from Warehouse_Data.xls\n"
        + f"window.WAREHOUSE_TOTAL_COUNT = {total};\n"
        + "window.WAREHOUSE_COUNTS_BY_BRAND = "
        + json.dumps(dict(counts), ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )

    (root / "warehouse-stores.js").write_text(stores_js, encoding="utf-8")
    (root / "warehouse-counts.js").write_text(counts_js, encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    xls_path = root / "Warehouse_Data.xls"
    if not xls_path.exists():
        raise SystemExit(f"Missing {xls_path}")
    rows = read_rows(xls_path)
    stores = build_stores(rows)
    write_outputs(root, stores)
    print(f"Wrote {len(stores)} stores → warehouse-stores.js, warehouse-counts.js")


if __name__ == "__main__":
    main()

