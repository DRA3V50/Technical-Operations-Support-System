import json
import shutil
import time
from datetime import datetime, timezone


def read_cpu():
    with open("/proc/stat") as file:
        values = list(map(int, file.readline().split()[1:]))
    idle = values[3] + values[4]
    return idle, sum(values)


def cpu_usage():
    idle1, total1 = read_cpu()
    time.sleep(0.5)
    idle2, total2 = read_cpu()

    total_delta = total2 - total1
    if total_delta == 0:
        return 0.0

    return round(
        100 * (1 - (idle2 - idle1) / total_delta), 1
    )


def memory_usage():
    with open("/proc/meminfo") as file:
        values = {
            parts[0].rstrip(":"): int(parts[1])
            for line in file
            if (parts := line.split())
        }

    total = values["MemTotal"]
    available = values["MemAvailable"]

    return round(100 * (total - available) / total, 1)


def disk_usage():
    disk = shutil.disk_usage("/")
    return round(100 * disk.used / disk.total, 1)


def collect_metrics():
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "Ubuntu WSL",
        "cpu_percent": cpu_usage(),
        "memory_percent": memory_usage(),
        "disk_percent": disk_usage(),
    }


if __name__ == "__main__":
    print(json.dumps(collect_metrics(), indent=2))
