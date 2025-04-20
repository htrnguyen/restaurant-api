import os
import signal
import subprocess
import sys
import time
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
        # Khởi động các microservices
        for service, port in services:
            service_dir = os.path.join(root_dir, "services", service)
            os.chdir(service_dir)  # Di chuyển vào thư mục service
            cmd = f"uvicorn app.main:app --reload --port {port}"
            process = subprocess.Popen(cmd, shell=True)
            processes.append(process)
            print(f"Started {service} on port {port}")
            os.chdir(root_dir)  # Trở về thư mục gốc
            time.sleep(1)  # Đợi 1 giây giữa việc khởi động các service

        # Khởi động API Documentation server
        print("\nStarting API Documentation server...")
        os.chdir(root_dir)
        api_docs_cmd = "uvicorn api_docs:app --reload --port 8000"
        api_docs_process = subprocess.Popen(api_docs_cmd, shell=True)
        processes.append(api_docs_process)
        print("Started API Documentation server on port 8000")
        print("\nYou can now access:")
        print("- API Documentation: http://localhost:8000")
        print("- Swagger UI for each service:")
        for service, port in services:
            print(f"  - {service}: http://localhost:{port}/docs")

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
    print("All services stopped successfully")
    sys.exit(0)


if __name__ == "__main__":
    print("Starting Restaurant Management System...")
    print("Press Ctrl+C to stop all services\n")
    run_services()
