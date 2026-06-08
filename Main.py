import psutil
from rich.table import Table
from rich.live import Live
from itertools import count
from plyer import notification
import time

warning_cpu = ""
warning_ram = ""


def get_cpu():
    cpu = psutil.cpu_percent()
    return cpu

def get_ram():
    ram = psutil.virtual_memory()[2]
    return ram

def get_disk_usage():
    disk = psutil.disk_usage('C:')
    disk = disk.percent
    return disk


def generate_table() -> Table:
    table = Table(title="System Monitor Dashboard", show_header=True, header_style="bold magenta")
    table.add_column("CPU Usage", justify="center")
    table.add_column("RAM Usage", justify="center")
    table.add_column("Disk Usage", justify="center")

    cpu = get_cpu()   
    ram = get_ram()   
    disk = get_disk_usage()

    cpu_color = "[red]" if cpu > 80 else "[yellow]" if cpu > 50 else "[green]"
    ram_color = "[red]" if ram > 80 else "[yellow]" if ram > 50 else "[green]"
    disk_color = "[red]" if disk > 90 else "[yellow]" if disk > 70 else "[green]"

    table.add_row(
        f"{cpu_color}{cpu}%", 
        f"{ram_color}{ram}%", 
        f"{disk_color}{disk}%"
    )
    
    return table


   
def main():
 with Live(generate_table(), refresh_per_second=4) as live:
    while True:
        time.sleep(0.4)  
        live.update(generate_table())

main()