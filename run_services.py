import os
import signal
import subprocess
import sys
from typing import List


def run_services():
    # Thư mục gốc của project
    root_dir = os.path.dirname(os.path.abspath(__file__))

    services = [
        ("user-service", 8001),
        ("table-service", 8002),
        ("menu-service", 8003),
        ("order-service", 8004),
        ("kitchen-service", 8005),
        ("payment-service", 8006),
    ]

    processes: List[subprocess.Popen] = []

    try:
        for service, port in services:
            service_dir = os.path.join(root_dir, "services", service)
            os.chdir(service_dir)  # Di chuyển vào thư mục service
            cmd = f"uvicorn app.main:app --reload --port {port}"
            process = subprocess.Popen(cmd, shell=True)
            processes.append(process)
            print(f"Started {service} on port {port}")
            os.chdir(root_dir)  # Trở về thư mục gốc

        # Chờ cho đến khi có tín hiệu dừng
        signal.signal(signal.SIGINT, lambda s, f: stop_services(processes))
        signal.signal(signal.SIGTERM, lambda s, f: stop_services(processes))

        # Giữ script chạy
        for process in processes:
            process.wait()

    except Exception as e:
        print(f"Error starting services: {e}")
        stop_services(processes)


def stop_services(processes: List[subprocess.Popen]):
    print("\nStopping all services...")
    for process in processes:
        if process.poll() is None:  # Nếu process vẫn đang chạy
            process.terminate()
            process.wait()
    sys.exit(0)


if __name__ == "__main__":
    run_services()
