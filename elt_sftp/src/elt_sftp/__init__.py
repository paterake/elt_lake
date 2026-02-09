"""ELT module for SFTP file transfer operations (push and pull)."""

from .models import SftpConfig, AuthMethod, TransferResult
from .parsers import SftpConfigParser
from .sftp_client import SftpClient
from .reporting import SftpReporter

__all__ = [
    # Models
    "SftpConfig",
    "AuthMethod",
    "TransferResult",
    # Parsers
    "SftpConfigParser",
    # Client
    "SftpClient",
    # Reporting
    "SftpReporter",
]

__version__ = "0.1.0"
