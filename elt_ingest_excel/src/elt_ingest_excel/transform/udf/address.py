from typing import TYPE_CHECKING
import re
import duckdb
import requests
from duckdb.typing import VARCHAR

if TYPE_CHECKING:
    import duckdb as duckdb_types

_DISALLOWED = re.compile(r'["`<>|;{}]')
_WS = re.compile(r"\s+")

_PAT_GB = re.compile(r"\b[A-PR-UWYZ][A-HK-Y]?\d[A-Z\d]?\s?\d[ABD-HJLNP-UW-Z]{2}\b", re.IGNORECASE)
_PAT_US = re.compile(r"\b\d{5}(?:-\d{4})?\b")
_PAT_DE = re.compile(r"\b\d{5}\b")
_PAT_FR = re.compile(r"\b\d{5}\b")
_PAT_NL = re.compile(r"\b\d{4}\s?[A-Z]{2}\b", re.IGNORECASE)
_PAT_IE = re.compile(r"\b[A-Z0-9]{7}\b", re.IGNORECASE)

_CACHE_POSTCODES: dict[str, dict] = {}
_CACHE_ZIP: dict[str, dict] = {}
_CACHE_GEOCODE: dict[str, dict] = {}


def _clean(s: str | None) -> str | None:
    if s is None:
        return None
    t = _DISALLOWED.sub("", s)
    t = _WS.sub(" ", t).strip()
    return t if t else None


def _first(*vals: str | None) -> str | None:
    for v in vals:
        if v is not None and str(v).strip():
            return v
    return None


def _find_postcode(text: str, cc_hint: str | None) -> tuple[str | None, str | None]:
    m = _PAT_GB.search(text)
    if m:
        return _WS.sub("", m.group(0)).upper(), "GB"
    m = _PAT_NL.search(text)
    if m:
        g = m.group(0).upper().replace(" ", "")
        return g, "NL"
    m = _PAT_US.search(text)
    if m:
        return m.group(0), "US"
    m = _PAT_IE.search(text)
    if m:
        return m.group(0).upper(), "IE"
    m = _PAT_DE.search(text)
    if m:
        return m.group(0), "DE"
    m = _PAT_FR.search(text)
    if m:
        return m.group(0), "FR"
    return None, cc_hint


def _libpostal_parse(address: str) -> dict | None:
    try:
        from postal.parser import parse_address
    except Exception:
        return None
    try:
        parts = parse_address(address)
        out: dict[str, str] = {}
        for value, label in parts:
            out[label] = value
        return out
    except Exception:
        return None


def _lookup_gb(postcode: str) -> dict | None:
    key = postcode.upper()
    if key in _CACHE_POSTCODES:
        return _CACHE_POSTCODES[key]
    try:
        r = requests.get(f"https://api.postcodes.io/postcodes/{key}", timeout=3)
        if r.status_code == 200:
            data = r.json().get("result") or {}
            _CACHE_POSTCODES[key] = data
            return data
    except Exception:
        pass
    return None


def _lookup_us(zipcode: str) -> dict | None:
    key = zipcode
    if key in _CACHE_ZIP:
        return _CACHE_ZIP[key]
    try:
        r = requests.get(f"https://api.zippopotam.us/us/{key}", timeout=3)
        if r.status_code == 200:
            data = r.json()
            _CACHE_ZIP[key] = data
            return data
    except Exception:
        pass
    return None


def _geocode(address: str, cc_hint: str | None) -> dict | None:
    key = (address + "|" + (cc_hint or "")).lower()
    if key in _CACHE_GEOCODE:
        return _CACHE_GEOCODE[key]
    params = {
        "q": address,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 1,
    }
    if cc_hint:
        params["countrycodes"] = cc_hint.lower()
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search", params=params, timeout=4, headers={"User-Agent": "elt-ingest-excel"})
        if r.status_code == 200:
            arr = r.json()
            if isinstance(arr, list) and arr:
                res = arr[0]
                _CACHE_GEOCODE[key] = res
                return res
    except Exception:
        pass
    return None


def register(conn: "duckdb.DuckDBPyConnection") -> None:
    def udf_normalize_address(
        address_1: str | None,
        address_2: str | None,
        address_3: str | None,
        address_4: str | None,
        city: str | None,
        region: str | None,
        postal_code: str | None,
        country_code: str | None,
    ) -> dict[str, str | None]:
        a1 = _clean(address_1)
        a2 = _clean(address_2)
        a3 = _clean(address_3)
        a4 = _clean(address_4)
        c0 = _clean(city)
        r0 = _clean(region)
        p0 = _clean(postal_code)
        cc0 = (country_code or "").upper() or None
        text = " ".join([x for x in [a1, a2, a3, a4, c0, r0, p0] if x])
        p1, cc1 = _find_postcode(text, cc0)
        p = p0 or p1
        cc = cc1 or cc0
        norm_city = c0
        norm_region = r0
        norm_cc = cc
        norm_postcode = p
        if p and (cc or "").upper() == "GB":
            gb = _lookup_gb(p)
            if gb:
                norm_postcode = gb.get("postcode") or p
                post_town = gb.get("post_town")
                admin_county = gb.get("admin_county")
                region_name = gb.get("region")
                country_name = gb.get("country")
                norm_city = _clean(_first(post_town, norm_city))
                norm_region = _clean(_first(admin_county, region_name, norm_region))
                norm_cc = "GB"
        elif p and (cc or "").upper() == "US":
            us = _lookup_us(p)
            if us and "places" in us and us["places"]:
                place = us["places"][0]
                norm_city = _clean(_first(place.get("place name"), norm_city))
                norm_region = _clean(_first(place.get("state"), norm_region))
                norm_cc = "US"
                norm_postcode = p
        if not norm_city or not norm_region or not norm_postcode or not norm_cc:
            q = " ".join([x for x in [a1, a2, a3, a4, c0, r0] if x])
            lp = _libpostal_parse(q)
            if lp:
                norm_postcode = _clean(_first(lp.get("postcode"), norm_postcode))
                norm_city = _clean(_first(lp.get("city"), lp.get("suburb"), norm_city))
                norm_region = _clean(_first(lp.get("state"), lp.get("county"), lp.get("region"), norm_region))
                cc_guess = lp.get("country_code") or None
                if not cc_guess:
                    country_name = lp.get("country") or ""
                    cc_guess = country_name.strip().upper() if len(country_name.strip()) == 2 else None
                norm_cc = _first(cc_guess, norm_cc)
        if not norm_city or not norm_region or not norm_postcode or not norm_cc:
            q = " ".join([x for x in [a1, a2, a3, a4, c0, r0] if x])
            g = _geocode(q, cc)
            if g and isinstance(g, dict):
                addr = g.get("address") or {}
                norm_postcode = _clean(_first(addr.get("postcode"), norm_postcode))
                norm_cc = (addr.get("country_code") or norm_cc or "").upper() or None
                norm_city = _clean(
                    _first(
                        addr.get("city"),
                        addr.get("town"),
                        addr.get("village"),
                        addr.get("hamlet"),
                        norm_city,
                    )
                )
                norm_region = _clean(
                    _first(
                        addr.get("state"),
                        addr.get("county"),
                        addr.get("region"),
                        norm_region,
                    )
                )
        toks = {x.lower() for x in [norm_city or "", norm_region or ""] if x}
        b1 = None if a1 and a1.lower() in toks else a1
        b2 = None if a2 and a2.lower() in toks else a2
        b3 = None if a3 and a3.lower() in toks else a3
        b4 = None if a4 and a4.lower() in toks else a4
        return {
            "address_line_1": b1,
            "address_line_2": b2,
            "address_line_3": b3,
            "address_line_4": b4,
            "city": norm_city,
            "region": norm_region,
            "postal_code": norm_postcode,
            "country_code": norm_cc,
        }

    conn.create_function(
        "udf_normalize_address",
        udf_normalize_address,
        [VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR],
        duckdb.struct_type(
            {
                "address_line_1": "VARCHAR",
                "address_line_2": "VARCHAR",
                "address_line_3": "VARCHAR",
                "address_line_4": "VARCHAR",
                "city": "VARCHAR",
                "region": "VARCHAR",
                "postal_code": "VARCHAR",
                "country_code": "VARCHAR",
            }
        ),
        null_handling="special",
    )
