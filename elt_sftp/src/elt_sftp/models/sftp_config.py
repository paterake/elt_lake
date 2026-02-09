from dataclasses import dataclass
from enum import Enum


class AuthMethod(Enum):
    SSH_KEY = "ssh_key"
    PASSWORD = "password"


@dataclass
class SftpConfig:
    name: str
    server_name: str
    host: str
    port: int
    authentication: AuthMethod
    username: str
    remote_path: str
    internal_ip: str = ""
    ssh_key_path: str = ""
    password: str = ""
