import time
import psutil
from rich.live import Live
from rich.table import Table
import wmi
import datetime
from plyer import notification
import os

DB_FILE = "logs.txt"

if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            pass


timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(DB_FILE, 'a') as f:
    f.write(f"[{timestamp}] The system has started")

last_sent, last_recv = psutil.net_io_counters()[:2]
last_time = time.time()

psutil.cpu_percent(interval=None)


def get_cpu():
    return psutil.cpu_percent(interval=None)


def get_cpu_temperature():
    try:
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        sensors = w.Sensor()
        for sensor in sensors:
            if sensor.SensorType == "Temperature" and "CPU" in sensor.Name:
                return float(sensor.Value)
        return None
    except Exception:
        return None


def get_ram():
    return psutil.virtual_memory()[2]


def get_disk_usage():
    return psutil.disk_usage("C:").percent

def get_boot_time():
    boot = psutil.boot_time()
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(boot)
    return uptime

def send_notification(title,message):
    notification.notify(
        title=title,
        message=message
    )

def get_network_speed():
    global last_sent, last_recv, last_time

    net = psutil.net_io_counters()
    current_sent = net[0]
    current_recv = net[1]
    current_time = time.time()

    dt = current_time - last_time
    if dt <= 0:
        dt = 0.01

    bytes_sent_per_sec = (current_sent - last_sent) / dt
    bytes_recv_per_sec = (current_recv - last_recv) / dt

    last_sent = current_sent
    last_recv = current_recv
    last_time = current_time

    return bytes_sent_per_sec, bytes_recv_per_sec

def format_bytes(b):
    if b >= 1_000_000:
        return f"{b/1_000_000:.1f} MB/s"
    elif b >= 1_000:
        return f"{b/1_000:.1f} KB/s"
    return f"{b:.0f} B/s"


def generate_table() -> Table:
    table = Table(
        title="System Monitor Dashboard",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("CPU Usage", justify="center")
    table.add_column("CPU Temperature", justify="center")
    table.add_column("RAM Usage", justify="center")
    table.add_column("Disk Usage", justify="center")
    table.add_column("Network (Sent/sec)", justify="center")
    table.add_column("Network (Recv/sec)", justify="center")
    table.add_column("UpTime", justify="center")


    cpu = get_cpu()
    cpu_temp = get_cpu_temperature()
    ram = get_ram()
    disk = get_disk_usage()
    net_sent, net_recv = get_network_speed()
    uptime = get_boot_time()

    cpu_color = "[red]" if cpu > 80 else "[yellow]" if cpu > 50 else "[green]"
    ram_color = "[red]" if ram > 80 else "[yellow]" if ram > 50 else "[green]"
    disk_color = "[red]" if disk > 90 else "[yellow]" if disk > 70 else "[green]"

    if cpu > 80:
        send_notification("CPU WARNING",f"Heavy CPU Usage. The CPU usage is {cpu}%")

        with open(DB_FILE,"a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Heavy CPU Usage. The CPU usage is {cpu}%")

    if ram > 80:
        send_notification("RAM WARNING",f"Heavy RAM Usage. The RAM usage is {ram}%")
        with open(DB_FILE,"a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Heavy RAM Usage. The RAM usage is {ram}%")



    net_sent_color = (
        "[red]" if net_sent > 1000000 else "[yellow]" if net_sent > 100000 else "[green]"
    )
    net_recv_color = (
        "[red]" if net_recv > 1000000 else "[yellow]" if net_recv > 100000 else "[green]"
    )

    temp_str = f"{cpu_temp:.1f}°C" if cpu_temp is not None else "N/A"

    table.add_row(
     f"{cpu_color}{cpu:.1f}%",
     temp_str,
     f"{ram_color}{ram:.1f}%",
     f"{disk_color}{disk:.1f}%",
     f"{net_sent_color}{format_bytes(net_sent)}",
     f"{net_recv_color}{format_bytes(net_recv)}",
     f"{uptime}"
 )

    return table


def main():
    with Live(generate_table(), refresh_per_second=3) as live:
        try:
            while True:
                time.sleep(0.4)
                live.update(generate_table())
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()