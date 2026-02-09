"""Example: Pull files from the FA Hyve Managed SFTP service."""

from pathlib import Path

from elt_sftp import SftpClient, SftpConfigParser


def main():
    config_base = Path(__file__).resolve().parent.parent / "config"
    config = SftpConfigParser.from_json(config_base / "sftp" / "fa_hyve.json")

    with SftpClient(config) as client:
        results = client.pull(
            remote_path="/",
            local_path="~/Documents/__data/sftp/fa_hyve",
        )


if __name__ == "__main__":
    main()
