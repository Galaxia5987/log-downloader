import os
import time
import hashlib
import subprocess
import psutil
from git import Repo
import shutil
from loguru import logger

LOGS_DIRECTORY = os.getenv('LOGS_DIRECTORY', '/path')
ALL_LOGS_FLAG = os.getenv('ALL_LOGS', 'false').lower() == 'true'
GIT_REPO_PATH = '/path'
REMOTE_REPO = 'origin'
BRANCH = 'main'
ADVANTAGE_SCOPE_PATH = '/path'


def hash_file(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def log_exists(log_name, device_path):
    new_file_path = os.path.join(device_path, log_name)
    new_file_hash = hash_file(new_file_path)

    for root, dirs, files in os.walk(LOGS_DIRECTORY):
        for file in files:
            if file == log_name:
                existing_file_path = os.path.join(root, file)
                existing_file_hash = hash_file(existing_file_path)
                if new_file_hash == existing_file_hash:
                    return True
    return False


def download_logs(device_path):
    log_files = [f for f in os.listdir(device_path) if f.endswith('.wpilog')]
    for log_file in log_files:
        src_file = os.path.join(device_path, log_file)
        dst_file = os.path.join(LOGS_DIRECTORY, log_file)

        if not log_exists(log_file, device_path) or ALL_LOGS_FLAG:
            shutil.copy2(src_file, dst_file)
            logger.info(f"Downloaded: {log_file}")
            commit_and_push_log(log_file)
            open_in_advantage_scope(dst_file)


def commit_and_push_log(log_file):
    repo = Repo(GIT_REPO_PATH)
    repo.index.add([os.path.join(LOGS_DIRECTORY, log_file)])
    repo.index.commit(f"Add log file {log_file}")
    repo.remote(REMOTE_REPO).push(BRANCH)


def open_in_advantage_scope(log_file):
    try:
        subprocess.Popen([ADVANTAGE_SCOPE_PATH, log_file])
    except Exception as e:
        logger.info(f"Failed to open AdvantageScope: {e}")


def monitor_devices():
    while True:
        devices = [disk.device for disk in psutil.disk_partitions()]
        for device in devices:
            if "roboRIO" in device or "/media" in device:
                logger.info(f"Device connected: {device}")
                download_logs(device)

        time.sleep(10)


if __name__ == "__main__":
    monitor_devices()
