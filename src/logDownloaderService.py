import hashlib
from loguru import logger

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
