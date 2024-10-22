import hashlib
from loguru import logger

def hash_file(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def monitor_devices():
    while True:
        devices = [disk.device for disk in psutil.disk_partitions()]
        for device in devices:
            if "roboRIO" in device or "/media" in device:
                logger.info(f"Device connected: {device}")

        time.sleep(10)


if __name__ == "__main__":
    monitor_devices()