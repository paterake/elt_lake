from ..models import TransferResult


class SftpReporter:

    def connecting(self, name: str, host: str, port: int) -> None:
        print(f"\n{'=' * 60}")
        print(f"  SFTP: Connecting to {name}")
        print(f"  Host: {host}:{port}")
        print(f"{'=' * 60}")

    def connected(self, name: str) -> None:
        print(f"  Connected to {name}")

    def disconnected(self, name: str) -> None:
        print(f"  Disconnected from {name}")

    def pull_started(self, remote_path: str, file_count: int) -> None:
        print(f"\n  Pull: {file_count} file(s) from {remote_path}")
        print(f"  {'-' * 50}")

    def push_started(self, remote_path: str, file_count: int) -> None:
        print(f"\n  Push: {file_count} file(s) to {remote_path}")
        print(f"  {'-' * 50}")

    def file_transferred(self, result: TransferResult, direction: str) -> None:
        status = "OK" if result.success else "FAIL"
        size = _format_size(result.size_bytes) if result.success else "---"
        print(f"  [{status}] {result.file_name:<40} {size:>10}")
        if not result.success:
            print(f"         Error: {result.error}")

    def transfer_summary(self, results: list[TransferResult], direction: str) -> None:
        succeeded = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        total_bytes = sum(r.size_bytes for r in results if r.success)

        print(f"  {'-' * 50}")
        print(f"  {direction.capitalize()} complete: {succeeded} succeeded, {failed} failed, {_format_size(total_bytes)} total")
        print()


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
