from typing import TYPE_CHECKING

import phonenumbers
import re
from phonenumbers.phonenumberutil import length_of_geographical_area_code
import duckdb

from duckdb.typing import VARCHAR

if TYPE_CHECKING:
    import duckdb as duckdb_types


def _try_parse(phone_str: str, country_code: str | None):
    raw = phone_str or ""
    digits = re.sub(r"[^0-9+]", "", raw)
    candidates: list[tuple[str, str | None]] = []
    if digits.startswith("+"):
        candidates.append((digits, None))
    if country_code:
        candidates.append((digits, country_code.upper()))
    if not digits.startswith("+"):
        if digits.startswith("0") or digits.startswith("7"):
            candidates.append((digits, "GB"))
    tried: set[tuple[str, str | None]] = set()
    for number, region in candidates:
        key = (number, region)
        if key in tried:
            continue
        tried.add(key)
        stripped = number
        for _ in range(4):
            try:
                p = phonenumbers.parse(stripped, region)
                if phonenumbers.is_valid_number(p):
                    return p
            except Exception:
                pass
            if not stripped.endswith("0"):
                break
            stripped = stripped[:-1]
    return None


def register(conn: "duckdb.DuckDBPyConnection") -> None:
    def get_area_code(phone_str: str, country_code: str | None) -> str | None:
        if not phone_str:
            return None
        p = _try_parse(phone_str, country_code)
        if p is None:
            return None
        nsn = phonenumbers.national_significant_number(p)
        ac_len = length_of_geographical_area_code(p)
        return nsn[:ac_len] if ac_len > 0 else None

    conn.create_function(
        "get_area_code",
        get_area_code,
        [VARCHAR, VARCHAR],
        VARCHAR,
        null_handling="special",
    )

    def get_phone_type(phone_str: str, country_code: str | None) -> str | None:
        if not phone_str:
            return None
        p = _try_parse(phone_str, country_code)
        if p is None:
            digits = re.sub(r"[^0-9]", "", phone_str)
            if digits.startswith("44") and len(digits) > 2:
                nsn = digits[2:]
                if nsn.startswith("7"):
                    return "Mobile"
                return "Landline"
            return None
        num_type = phonenumbers.number_type(p)
        if num_type == phonenumbers.PhoneNumberType.MOBILE:
            return "Mobile"
        if num_type in (
            phonenumbers.PhoneNumberType.FIXED_LINE,
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE,
            phonenumbers.PhoneNumberType.VOIP,
        ):
            return "Landline"
        return None

    conn.create_function(
        "get_phone_type",
        get_phone_type,
        [VARCHAR, VARCHAR],
        VARCHAR,
        null_handling="special",
    )

    def udf_parse_phone(
        international_phone_code: str | None, phone_number: str | None
    ) -> dict[str, str | None]:
        raw_intl = international_phone_code or ""
        raw_local = phone_number or ""
        intl_digits = re.sub(r"[^0-9]", "", raw_intl)
        local_digits = re.sub(r"[^0-9]", "", raw_local)
        if not intl_digits and local_digits:
            derived = ""
            if local_digits.startswith("00") and len(local_digits) > 4:
                derived = local_digits[2:]
            elif local_digits.startswith("011") and len(local_digits) > 5:
                derived = local_digits[3:]
            if derived:
                intl_from_local = derived[:3]
                rest = derived[3:]
                intl_digits = intl_from_local
                local_digits = rest or ""
        candidates: list[tuple[str, str | None]] = []
        if raw_local.strip().startswith("+"):
            candidates.append((raw_local.strip(), None))
        if intl_digits and local_digits:
            candidates.append(("+" + intl_digits + local_digits, None))
        region = None
        if intl_digits:
            try:
                cc = int(intl_digits)
                region = phonenumbers.region_code_for_country_code(cc)
            except Exception:
                region = None
        if region and local_digits:
            candidates.append((local_digits, region))
        if local_digits:
            if local_digits.startswith("0") or local_digits.startswith("7"):
                candidates.append((local_digits, "GB"))
        tried: set[tuple[str, str | None]] = set()
        parsed = None
        for number, reg in candidates:
            key = (number, reg)
            if key in tried:
                continue
            tried.add(key)
            stripped = number
            for _ in range(4):
                try:
                    p = phonenumbers.parse(stripped, reg)
                    if phonenumbers.is_valid_number(p):
                        parsed = p
                        break
                except Exception:
                    pass
                if not stripped.endswith("0"):
                    break
                stripped = stripped[:-1]
            if parsed is not None:
                break
        if parsed is None:
            fallback_digits = local_digits or intl_digits
            if intl_digits:
                fallback_intl = "+" + intl_digits
            else:
                fallback_intl = "+44"
            if not fallback_digits:
                return {
                    "international_phone_code": fallback_intl,
                    "area_code": None,
                    "phone_number": None,
                    "device_type": "Landline",
                }
            if intl_digits == "44" and len(fallback_digits) > 3:
                area = fallback_digits[:3]
                local = fallback_digits[3:]
            elif len(fallback_digits) > 1:
                area = fallback_digits[0]
                local = fallback_digits[1:]
            else:
                area = fallback_digits
                local = ""
            return {
                "international_phone_code": fallback_intl,
                "area_code": area,
                "phone_number": local,
                "device_type": "Landline",
            }
        country_code_int = parsed.country_code
        intl_out = f"+{country_code_int}" if country_code_int else None
        nsn = phonenumbers.national_significant_number(parsed)
        num_type = phonenumbers.number_type(parsed)
        ac_len = length_of_geographical_area_code(parsed)
        is_gb = country_code_int == 44
        is_us = country_code_int == 1
        if num_type == phonenumbers.PhoneNumberType.MOBILE:
            if len(nsn) > 4:
                area = nsn[:4]
                local = nsn[4:]
            else:
                area = None
                local = nsn
        elif (
            is_gb
            and len(nsn) > 3
            and nsn[0] == "8"
        ):
            area = nsn[:3]
            local = nsn[3:]
        elif (
            is_us
            and len(nsn) > 3
            and nsn[:3] in ("800", "888", "877", "866", "855", "844", "833")
        ):
            area = nsn[:3]
            local = nsn[3:]
        elif ac_len and ac_len > 0 and ac_len < len(nsn):
            area = nsn[:ac_len]
            local = nsn[ac_len:]
        else:
            area = None
            local = nsn
        if area is None and local:
            if len(local) > 3:
                area = local[:3]
                local = local[3:]
            else:
                area = local
                local = ""
        if num_type == phonenumbers.PhoneNumberType.MOBILE:
            device = "Mobile"
        elif num_type in (
            phonenumbers.PhoneNumberType.FIXED_LINE,
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE,
            phonenumbers.PhoneNumberType.VOIP,
            phonenumbers.PhoneNumberType.PREMIUM_RATE,
            phonenumbers.PhoneNumberType.TOLL_FREE,
            phonenumbers.PhoneNumberType.SHARED_COST,
            phonenumbers.PhoneNumberType.UAN,
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER,
            phonenumbers.PhoneNumberType.VOICEMAIL,
        ):
            device = "Landline"
        else:
            device = None
        return {
            "international_phone_code": intl_out,
            "area_code": area,
            "phone_number": local,
            "device_type": device,
        }

    conn.create_function(
        "udf_parse_phone",
        udf_parse_phone,
        [VARCHAR, VARCHAR],
        duckdb.struct_type(
            {
                "international_phone_code": "VARCHAR",
                "area_code": "VARCHAR",
                "phone_number": "VARCHAR",
                "device_type": "VARCHAR",
            }
        ),
        null_handling="special",
    )
