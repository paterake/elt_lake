import argparse
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Iterable


def list_vba_entry_points(workbook_path: str | Path) -> list[str]:
    path = Path(workbook_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.suffix.lower() not in {".xlsm", ".xlam", ".xlsb"}:
        return []
    with zipfile.ZipFile(path) as zf:
        try:
            vba = zf.read("xl/vbaProject.bin")
        except KeyError:
            return []
    candidates: set[str] = set()
    txt = "\n".join(_iter_printable_strings(vba, min_len=3))

    for m in re.finditer(r"\b(?:Sub|Function)\s+([A-Za-z_][A-Za-z0-9_]*)\b", txt):
        n = m.group(1)
        if n:
            candidates.add(n)

    for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", txt):
        candidates.add(token)

    names: set[str] = set()
    for n in candidates:
        nl = n.lower()
        if nl in {"auto_open", "auto_close"}:
            continue
        if len(n) < 6:
            continue
        if nl in _OFFLINE_MACRO_STOPWORDS:
            continue
        if nl.startswith("worksheet_") or nl.startswith("run") or "validat" in nl:
            names.add(n)
            continue
        if nl in {"useforsuppliersettlementonly"}:
            names.add(n)

    return sorted(names, key=str.lower)


def list_macros_via_excel(workbook_path: str | Path, close: bool = True, excel_visible: bool = False) -> list[str]:
    if sys.platform != "darwin":
        raise RuntimeError("Excel macro listing is only implemented for macOS")

    path = Path(workbook_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(str(path))

    script = f"""
tell application "Microsoft Excel"
    activate
    set display alerts to false
    set visible to {"true" if excel_visible else "false"}
    open (POSIX file "{_escape_applescript_string(str(path))}")
    set wb to active workbook
    set macroNames to {{}}
    try
        set macroNames to name of every VB macro of wb
    on error errMsg number errNum
        try
            set macroNames to name of every VB macro
        on error errMsg2 number errNum2
            error ("Cannot list macros. Error 1: " & errMsg & " | Error 2: " & errMsg2)
        end try
    end try
    set AppleScript's text item delimiters to linefeed
    set macroText to macroNames as text
    set AppleScript's text item delimiters to ""
    if {"true" if close else "false"} then
        close wb saving no
    end if
    return macroText
end tell
"""
    out = _run_osascript_capture(script)
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return sorted(set(lines), key=str.lower)


def run_excel_vba_macro(
    workbook_path: str | Path,
    macro_name: str,
    unhide_sheets: Iterable[str] = ("Validation Results",),
    save: bool = True,
    close: bool = True,
    excel_visible: bool = False,
) -> None:
    if sys.platform != "darwin":
        raise RuntimeError("Excel VBA macro runner is only implemented for macOS")

    path = Path(workbook_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(str(path))

    macro = macro_name.strip()
    macro_candidates: list[str] = []
    if "!" in macro:
        macro_candidates.append(macro)
        macro = macro.split("!", 1)[1].strip()
    if not macro:
        raise ValueError("macro_name is empty")
    macro_candidates.append(macro)
    workbook_file_name = path.name
    macro_candidates.append(f"{workbook_file_name}!{macro}")

    sheet_names = [s for s in (str(x).strip() for x in unhide_sheets) if s]
    sheet_list = "{" + ",".join(f"\"{_escape_applescript_string(s)}\"" for s in sheet_names) + "}"
    macro_list = "{" + ",".join(f"\"{_escape_applescript_string(m)}\"" for m in dict.fromkeys(macro_candidates)) + "}"

    script = f"""
tell application "Microsoft Excel"
    activate
    set display alerts to false
    set visible to {"true" if excel_visible else "false"}
    open (POSIX file "{_escape_applescript_string(str(path))}")
    set macroCandidates to {macro_list}
    set macroRan to false
    repeat with m in macroCandidates
        try
            run VB macro (contents of m)
            set macroRan to true
            exit repeat
        end try
    end repeat
    if macroRan is false then
        error ("Cannot run VB macro. Tried: " & macroCandidates as string)
    end if
    repeat with sheetName in {sheet_list}
        try
            set visible of worksheet (contents of sheetName) of active workbook to true
        end try
    end repeat
    if {"true" if save else "false"} then
        save active workbook
    end if
    if {"true" if close else "false"} then
        close active workbook saving no
    end if
end tell
"""
    _run_osascript(script)


def _run_osascript(script: str) -> None:
    proc = subprocess.run(
        ["osascript", "-e", script],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        msg = "\n".join([x for x in [out, err] if x])
        raise RuntimeError(msg or f"osascript failed with code {proc.returncode}")


def _run_osascript_capture(script: str) -> str:
    proc = subprocess.run(
        ["osascript", "-e", script],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        msg = "\n".join([x for x in [out, err] if x])
        raise RuntimeError(msg or f"osascript failed with code {proc.returncode}")
    return proc.stdout or ""


def _escape_applescript_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _iter_printable_strings(data: bytes, min_len: int = 4) -> Iterable[str]:
    current: list[int] = []
    for b in data:
        if 32 <= b <= 126:
            current.append(b)
            continue
        if len(current) >= min_len:
            yield bytes(current).decode("ascii", errors="ignore")
        current = []
    if len(current) >= min_len:
        yield bytes(current).decode("ascii", errors="ignore")


_OFFLINE_MACRO_STOPWORDS: set[str] = {
    "attribute",
    "attributes",
    "call",
    "command",
    "delete",
    "header",
    "public",
    "private",
    "option",
    "explicit",
    "validation",
    "validationtype",
    "validationmanifest",
    "validations",
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workbook", required=True)
    p.add_argument("--macro")
    p.add_argument("--unhide-sheet", action="append", default=[])
    p.add_argument("--no-save", action="store_true")
    p.add_argument("--no-close", action="store_true")
    p.add_argument("--excel-visible", action="store_true")
    p.add_argument("--list-macros", action="store_true")
    p.add_argument("--list-macros-excel", action="store_true")
    args = p.parse_args()

    workbook = os.path.expanduser(args.workbook)
    if args.list_macros_excel:
        for n in list_macros_via_excel(workbook, close=not args.no_close, excel_visible=args.excel_visible):
            print(n)
        return 0
    if args.list_macros:
        for n in list_vba_entry_points(workbook):
            print(n)
        return 0

    if not args.macro:
        raise SystemExit("--macro is required unless --list-macros or --list-macros-excel is set")

    unhide = args.unhide_sheet if args.unhide_sheet else ["Validation Results"]
    run_excel_vba_macro(
        workbook_path=workbook,
        macro_name=args.macro,
        unhide_sheets=unhide,
        save=not args.no_save,
        close=not args.no_close,
        excel_visible=args.excel_visible,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
