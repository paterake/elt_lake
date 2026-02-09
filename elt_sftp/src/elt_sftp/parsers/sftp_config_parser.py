import json
from pathlib import Path

from ..models import SftpConfig, AuthMethod


class SftpConfigParser:

    @staticmethod
    def from_json(config_path: str | Path) -> SftpConfig:
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            data = json.load(f)

        return SftpConfig(
            name=data["name"],
            server_name=data["serverName"],
            host=data["host"],
            port=data.get("port", 22),
            authentication=AuthMethod(data["authentication"]),
            username=data.get("username", ""),
            remote_path=data.get("remotePath", "/"),
            internal_ip=data.get("internalIp", ""),
            ssh_key_path=data.get("sshKeyPath", ""),
            password=data.get("password", ""),
        )
