import re
from datetime import date, timedelta


def resolve_templates(obj: object, base_date: date) -> object:
    if isinstance(obj, dict):
        return {key: resolve_templates(value, base_date) for key, value in obj.items()}

    if isinstance(obj, list):
        return [resolve_templates(item, base_date) for item in obj]

    if isinstance(obj, str):
        return resolve_templates_in_string(obj, base_date)

    return obj


def resolve_templates_in_string(value: str, base_date: date) -> str:
    pattern = re.compile(r"\{date(?P<spec>[^{}]*)\}")

    def replacer(match: re.Match) -> str:
        spec = (match.group("spec") or "").strip()
        if spec.startswith(";"):
            spec = spec[1:]
        return resolve_date_template(spec, base_date)

    return pattern.sub(replacer, value)


def resolve_date_template(spec: str, base_date: date) -> str:
    fmt = "yyyy-mm-dd"
    add_days = 0

    if spec:
        parts = [part.strip() for part in spec.split(";") if part.strip()]
        for part in parts:
            if "=" not in part:
                continue
            key, raw_value = part.split("=", 1)
            key = key.strip().lower()
            raw_value = raw_value.strip()

            if key == "format":
                fmt = raw_value
            elif key == "add":
                add_days = int(raw_value)

    resolved_date = base_date + timedelta(days=add_days)
    return format_date(resolved_date, fmt)


def format_date(value: date, fmt: str) -> str:
    month_abbr = [
        "",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    out: list[str] = []
    i = 0
    while i < len(fmt):
        remaining = fmt[i:]
        remaining_lower = remaining.lower()

        if remaining_lower.startswith("yyyy"):
            out.append(f"{value.year:04d}")
            i += 4
            continue

        if remaining_lower.startswith("yy"):
            out.append(f"{value.year % 100:02d}")
            i += 2
            continue

        if remaining_lower.startswith("mmm"):
            out.append(month_abbr[value.month])
            i += 3
            continue

        if remaining_lower.startswith("mm"):
            out.append(f"{value.month:02d}")
            i += 2
            continue

        if remaining_lower.startswith("m"):
            out.append(str(value.month))
            i += 1
            continue

        if remaining_lower.startswith("dd"):
            out.append(f"{value.day:02d}")
            i += 2
            continue

        if remaining_lower.startswith("d"):
            out.append(str(value.day))
            i += 1
            continue

        out.append(fmt[i])
        i += 1

    return "".join(out)
