import time
import psutil
from rich.live import Live
from rich.table import Table
import wmi
import os
import sys
import ctypes


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

    cpu = get_cpu()
    cpu_temp = get_cpu_temperature()
    ram = get_ram()
    disk = get_disk_usage()
    net_sent, net_recv = get_network_speed()

    cpu_color = "[red]" if cpu > 80 else "[yellow]" if cpu > 50 else "[green]"
    ram_color = "[red]" if ram > 80 else "[yellow]" if ram > 50 else "[green]"
    disk_color = "[red]" if disk > 90 else "[yellow]" if disk > 70 else "[green]"

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