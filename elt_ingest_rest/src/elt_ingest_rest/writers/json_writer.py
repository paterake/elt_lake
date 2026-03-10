import json
from pathlib import Path


def save_json_single(*, filepath: Path, data: list[dict]) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def save_json_batches(
    *,
    output_dir: Path,
    base_filename: str,
    data: list[dict],
    batch_size: int,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    base_filename = base_filename.replace(".json", "")

    for i in range(0, len(data), batch_size):
        batch = data[i : i + batch_size]
        batch_num = i // batch_size + 1
        filename = f"{base_filename}_batch_{batch_num:04d}.json"
        filepath = output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(batch, f, indent=2, ensure_ascii=False)

    return output_dir
