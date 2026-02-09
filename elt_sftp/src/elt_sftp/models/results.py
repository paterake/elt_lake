from dataclasses import dataclass


@dataclass
class TransferResult:
    local_path: str
    remote_path: str
    file_name: str
    size_bytes: int
    success: bool
    error: str = ""
