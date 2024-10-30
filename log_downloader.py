import os
import time
import shutil
from pathlib import Path
from loguru import logger
from git import Repo
import wmi

REPO_PATH = Path(__file__).parent
DRIVERSTATION_LOGS_DIRECTORY = Path("C:/Users/Public/Documents/FRC/Log Files")
LOGS_DIR = REPO_PATH / "logs"
LOG_FILE_EXTENSION = "wpilog"
DRIVERSTATION_FILE_EXTENSION = ".dsevents"

def commit_and_push_log(repo, log_file):
    try:
        repo.index.add([str(log_file)])
        repo.index.commit(f"Add log file: {log_file.name}")
        logger.info(f"Committed {log_file.name} to repository")

        try:
            repo.remote().push()
            logger.info(f"Successfully pushed commit for {log_file.name}")
        except Exception as e:
            logger.error(f"Error pushing commit for {log_file.name}: {e}")
    except Exception as e:
        logger.exception(f"Error committing {log_file.name}: {e}")


def get_file_signature(file_path):
    return file_path.name, file_path.stat().st_size


def is_file_downloaded(log_file):
    for existing_file in LOGS_DIR.glob(f"*.{LOG_FILE_EXTENSION}"):
        if get_file_signature(existing_file) == get_file_signature(log_file):
            return True
    return False

def get_usb_drives():
    drives = set()
    c = wmi.WMI()

    for drive in c.Win32_LogicalDisk():
        if drive.DriveType == 2: # removable
            drives.add(Path(f"{drive.DeviceID}/"))

    return drives

def download_log_file(log_file, repo, dest_path):
    try:
        shutil.copy2(log_file, dest_path)
        ds_log = DRIVERSTATION_LOGS_DIRECTORY / log_file.name.split(".")[0]
        shutil.copy2(ds_log, dest_path)
    except OSError as error:
        logger.error(f"Failed to copy {log_file.name}: {error}")
        return

    logger.info(f"Copied {log_file.name} ({log_file.stat().st_size} bytes)")
    # commit_and_push_log(repo, dest_path)


def download_logs(drive_path, repo):
    try:
        for log_file in drive_path.glob(f"**/*.{LOG_FILE_EXTENSION}"):
            if is_file_downloaded(log_file):
                logger.info(f"Skipped {log_file.name} - already exists")
                continue
            dest_path = LOGS_DIR / log_file.name
            download_log_file(log_file, repo, dest_path)
    except Exception as e:
        logger.error(f"Error accessing {drive_path}: {e}")


def monitor_drives():
    logger.info(f"Monitoring for USB drives. Saving logs to {LOGS_DIR}")
    previous_drives = set()

    try:
        repo = Repo(REPO_PATH)
        logger.info("Git repository initialized")
    except Exception as e:
        logger.exception(f"Error initializing git repository: {e}")
        return

    while True:
        current_drives = get_usb_drives()

        new_drives = current_drives - previous_drives
        for drive in new_drives:
            logger.info(f"New drive detected: {drive}")
            download_logs(drive, repo)

        previous_drives = current_drives
        time.sleep(1)


if __name__ == "__main__":
    LOGS_DIR.mkdir(exist_ok=True)

    logger.add("logfile.log",
               rotation="100 MB",
               retention="1 week",
               compression="zip",
               format="{time} | {level} | {message}",
               backtrace=True,
               diagnose=True)
    monitor_drives()