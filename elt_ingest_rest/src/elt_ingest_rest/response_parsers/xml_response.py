from typing import Any
from xml.etree import ElementTree

from ..models import IngestConfig


def parse_xml(xml_text: str, config: IngestConfig) -> list[dict]:
    def local_name(tag: str) -> str:
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag

    def element_to_record(element: ElementTree.Element) -> dict:
        record: dict[str, Any] = dict(element.attrib)

        for child in list(element):
            child_key = local_name(child.tag)
            child_text = (child.text or "").strip()

            if child_text:
                if child_key in record:
                    existing = record[child_key]
                    if isinstance(existing, list):
                        existing.append(child_text)
                    else:
                        record[child_key] = [existing, child_text]
                else:
                    record[child_key] = child_text
            elif child.attrib:
                for attr_key, attr_value in child.attrib.items():
                    record[f"{child_key}.{attr_key}"] = attr_value

        return record

    root = ElementTree.fromstring(xml_text)

    boe_series = [
        element
        for element in root.iter()
        if local_name(element.tag) == "Cube" and "SCODE" in element.attrib
    ]
    if boe_series:
        records: list[dict] = []
        for series_element in boe_series:
            series_code = series_element.attrib.get("SCODE")
            series_description = series_element.attrib.get("DESC")

            for cube in series_element:
                if local_name(cube.tag) != "Cube":
                    continue
                if "TIME" not in cube.attrib or "OBS_VALUE" not in cube.attrib:
                    continue

                record: dict[str, Any] = {
                    "series_code": series_code,
                    "series_description": series_description,
                    "time": cube.attrib.get("TIME"),
                    "value": cube.attrib.get("OBS_VALUE"),
                }
                if "OBS_CONF" in cube.attrib:
                    record["obs_conf"] = cube.attrib.get("OBS_CONF")
                if "LAST_UPDATED" in cube.attrib:
                    record["last_updated"] = cube.attrib.get("LAST_UPDATED")

                records.append(record)

        return records

    record_tag = config.xml_record_tag.strip()
    if record_tag:
        elements = [
            element for element in root.iter() if local_name(element.tag) == record_tag
        ]
        return [element_to_record(element) for element in elements]

    children = list(root)
    if not children:
        return [element_to_record(root)]

    return [element_to_record(child) for child in children]
