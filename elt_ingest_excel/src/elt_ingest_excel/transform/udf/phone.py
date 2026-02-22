from typing import TYPE_CHECKING

import phonenumbers
import re
from phonenumbers.phonenumberutil import length_of_geographical_area_code

from duckdb.typing import VARCHAR

if TYPE_CHECKING:
    import duckdb


def _try_parse(phone_str: str):
    candidates = [phone_str]
    stripped = phone_str
    for _ in range(4):
        if not stripped.endswith("0"):
            break
        stripped = stripped[:-1]
        candidates.append(stripped)
    for s in candidates:
        try:
            p = phonenumbers.parse("+" + s)
            if phonenumbers.is_valid_number(p):
                return p
        except Exception:
            pass
    return None


def register(conn: "duckdb.DuckDBPyConnection") -> None:
    def get_area_code(phone_str: str) -> str | None:
        if not phone_str:
            return None
        p = _try_parse(phone_str)
        if p is None:
            digits = re.sub(r"[^0-9]", "", phone_str)
            if digits.startswith("44") and len(digits) > 5:
                nsn = digits[2:]
                if not nsn.startswith("7"):
                    return nsn[:3]
            return None
        nsn = phonenumbers.national_significant_number(p)
        ac_len = length_of_geographical_area_code(p)
        return nsn[:ac_len] if ac_len > 0 else None

    conn.create_function(
        "get_area_code",
        get_area_code,
        [VARCHAR],
        VARCHAR,
        null_handling="special",
    )

    def get_phone_type(phone_str: str) -> str | None:
        if not phone_str:
            return None
        p = _try_parse(phone_str)
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
        [VARCHAR],
        VARCHAR,
        null_handling="special",
    )
