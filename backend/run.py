import os
import subprocess
import sys


def main():
    # Determine environment and port
    app_env = os.getenv("APP_ENV", "local").lower()
    port = os.getenv("PORT", "8000")
    reload_flag = "--reload" if app_env != "prod" else ""

    # Command to launch Uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "localhost",
        "--port", str(port)
    ]
    if reload_flag:
        cmd.append(reload_flag)

    print(f"Starting backend with APP_ENV={app_env} on port {port}...")
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
