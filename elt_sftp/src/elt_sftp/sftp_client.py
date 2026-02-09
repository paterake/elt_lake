import os
from pathlib import Path

import paramiko

from .models import SftpConfig, AuthMethod, TransferResult
from .reporting import SftpReporter


class SftpClient:

    def __init__(self, config: SftpConfig, reporter: SftpReporter | None = None):
        self._config = config
        self._reporter = reporter or SftpReporter()
        self._transport: paramiko.Transport | None = None
        self._sftp: paramiko.SFTPClient | None = None

    def connect(self) -> None:
        self._reporter.connecting(self._config.name, self._config.host, self._config.port)

        self._transport = paramiko.Transport((self._config.host, self._config.port))

        if self._config.authentication == AuthMethod.SSH_KEY:
            key_path = os.path.expanduser(self._config.ssh_key_path)
            private_key = paramiko.RSAKey.from_private_key_file(key_path)
            self._transport.connect(username=self._config.username, pkey=private_key)
        else:
            self._transport.connect(
                username=self._config.username,
                password=self._config.password,
            )

        self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        self._reporter.connected(self._config.name)

    def disconnect(self) -> None:
        if self._sftp:
            self._sftp.close()
        if self._transport:
            self._transport.close()
        self._reporter.disconnected(self._config.name)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False

    def pull(
        self,
        remote_path: str,
        local_path: str,
        file_name: str = "*",
    ) -> list[TransferResult]:
        local_path = os.path.expanduser(local_path)
        os.makedirs(local_path, exist_ok=True)

        results: list[TransferResult] = []

        if file_name == "*":
            files = self._list_files(remote_path)
        else:
            files = [file_name]

        self._reporter.pull_started(remote_path, len(files))

        for fname in files:
            result = self._pull_file(remote_path, local_path, fname)
            results.append(result)
            self._reporter.file_transferred(result, direction="pull")

        self._reporter.transfer_summary(results, direction="pull")
        return results

    def push(
        self,
        local_path: str,
        remote_path: str,
        file_name: str = "*",
    ) -> list[TransferResult]:
        local_path = os.path.expanduser(local_path)

        results: list[TransferResult] = []

        if file_name == "*":
            files = [f for f in os.listdir(local_path) if os.path.isfile(os.path.join(local_path, f))]
        else:
            files = [file_name]

        self._reporter.push_started(remote_path, len(files))

        for fname in files:
            result = self._push_file(local_path, remote_path, fname)
            results.append(result)
            self._reporter.file_transferred(result, direction="push")

        self._reporter.transfer_summary(results, direction="push")
        return results

    def list_remote(self, remote_path: str) -> list[str]:
        return self._list_files(remote_path)

    def _list_files(self, remote_path: str) -> list[str]:
        entries = self._sftp.listdir_attr(remote_path)
        return [
            entry.filename
            for entry in entries
            if not stat_is_directory(entry.st_mode)
        ]

    def _pull_file(self, remote_path: str, local_path: str, file_name: str) -> TransferResult:
        remote_file = f"{remote_path.rstrip('/')}/{file_name}"
        local_file = os.path.join(local_path, file_name)

        try:
            self._sftp.get(remote_file, local_file)
            size = os.path.getsize(local_file)
            return TransferResult(
                local_path=local_path,
                remote_path=remote_path,
                file_name=file_name,
                size_bytes=size,
                success=True,
            )
        except Exception as e:
            return TransferResult(
                local_path=local_path,
                remote_path=remote_path,
                file_name=file_name,
                size_bytes=0,
                success=False,
                error=str(e),
            )

    def _push_file(self, local_path: str, remote_path: str, file_name: str) -> TransferResult:
        local_file = os.path.join(local_path, file_name)
        remote_file = f"{remote_path.rstrip('/')}/{file_name}"

        try:
            size = os.path.getsize(local_file)
            self._sftp.put(local_file, remote_file)
            return TransferResult(
                local_path=local_path,
                remote_path=remote_path,
                file_name=file_name,
                size_bytes=size,
                success=True,
            )
        except Exception as e:
            return TransferResult(
                local_path=local_path,
                remote_path=remote_path,
                file_name=file_name,
                size_bytes=0,
                success=False,
                error=str(e),
            )


def stat_is_directory(mode: int | None) -> bool:
    if mode is None:
        return False
    import stat
    return stat.S_ISDIR(mode)
