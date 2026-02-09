"""Connectivity test: push a test file, list it, pull it back, then clean up."""

import os
import tempfile
from datetime import datetime
from pathlib import Path

from elt_sftp import SftpClient, SftpConfigParser


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "sftp" / "fa_hyve.json"


def test_push_and_pull():
    config = SftpConfigParser.from_json(CONFIG_PATH)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_file_name = f"elt_sftp_test_{timestamp}.txt"

    with tempfile.TemporaryDirectory() as tmp_dir:
        local_push_dir = os.path.join(tmp_dir, "push")
        local_pull_dir = os.path.join(tmp_dir, "pull")
        os.makedirs(local_push_dir)
        os.makedirs(local_pull_dir)

        test_content = f"elt_sftp connectivity test - {datetime.now().isoformat()}\n"
        test_file_path = os.path.join(local_push_dir, test_file_name)
        with open(test_file_path, "w") as f:
            f.write(test_content)

        with SftpClient(config) as client:
            # 1. push the test file
            push_results = client.push(
                local_path=local_push_dir,
                remote_path=config.remote_path,
                file_name=test_file_name,
            )
            assert len(push_results) == 1
            assert push_results[0].success, f"Push failed: {push_results[0].error}"

            # 2. list remote and confirm the file is there
            remote_files = client.list_remote(config.remote_path)
            assert test_file_name in remote_files, (
                f"{test_file_name} not found in remote listing: {remote_files}"
            )

            # 3. pull the file back
            pull_results = client.pull(
                remote_path=config.remote_path,
                local_path=local_pull_dir,
                file_name=test_file_name,
            )
            assert len(pull_results) == 1
            assert pull_results[0].success, f"Pull failed: {pull_results[0].error}"

            # 4. verify content matches
            pulled_file = os.path.join(local_pull_dir, test_file_name)
            with open(pulled_file) as f:
                pulled_content = f.read()
            assert pulled_content == test_content, "Pulled file content does not match"

            # 5. clean up remote test file (may fail if delete not permitted)
            remote_file = f"{config.remote_path.rstrip('/')}/{test_file_name}"
            try:
                client._sftp.remove(remote_file)
                print(f"\n  Cleanup: removed {remote_file}")
            except PermissionError:
                print(f"\n  Cleanup: delete not permitted - {remote_file} left on server")

    print("\nConnectivity test PASSED: push, list, pull all succeeded.")


def test_directory_create_and_delete():
    config = SftpConfigParser.from_json(CONFIG_PATH)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir_name = f"elt_sftp_testdir_{timestamp}"
    test_file_name = f"elt_sftp_test_{timestamp}.txt"
    remote_base = config.remote_path.rstrip("/")
    remote_dir = f"{remote_base}/{test_dir_name}"
    remote_file = f"{remote_dir}/{test_file_name}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        # create a local test file to push
        test_content = f"directory permission test - {datetime.now().isoformat()}\n"
        test_file_path = os.path.join(tmp_dir, test_file_name)
        with open(test_file_path, "w") as f:
            f.write(test_content)

        with SftpClient(config) as client:
            # 1. create a remote directory
            client._sftp.mkdir(remote_dir)
            print(f"\n  [OK] mkdir {remote_dir}")

            # 2. push a file into the new directory
            push_results = client.push(
                local_path=tmp_dir,
                remote_path=remote_dir,
                file_name=test_file_name,
            )
            assert len(push_results) == 1
            assert push_results[0].success, f"Push failed: {push_results[0].error}"

            # 3. confirm the file is listed in the new directory
            remote_files = client.list_remote(remote_dir)
            assert test_file_name in remote_files, (
                f"{test_file_name} not found in {remote_dir}: {remote_files}"
            )
            print(f"  [OK] file listed in {remote_dir}")

            # 4. delete the remote file
            client._sftp.remove(remote_file)
            print(f"  [OK] removed {remote_file}")

            # 5. confirm the directory is now empty
            remaining = client.list_remote(remote_dir)
            assert len(remaining) == 0, f"Directory not empty after delete: {remaining}"
            print(f"  [OK] directory is empty")

            # 6. remove the remote directory
            client._sftp.rmdir(remote_dir)
            print(f"  [OK] rmdir {remote_dir}")

            # 7. confirm the directory no longer exists
            parent_entries = client._sftp.listdir(remote_base)
            assert test_dir_name not in parent_entries, (
                f"{test_dir_name} still exists after rmdir"
            )
            print(f"  [OK] directory removed from listing")

    print("\nDirectory permissions test PASSED: mkdir, push, delete file, rmdir all succeeded.")
