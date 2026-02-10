#!/usr/bin/env python3
"""
Port Scanner - Starter Template for Students
Assignment 2: Network Security

This is a STARTER TEMPLATE to help you get started.
You should expand and improve upon this basic implementation.

TODO for students:
1. Implement multi-threading for faster scans
2. Add banner grabbing to detect services
3. Add support for CIDR notation (e.g., 192.168.1.0/24)
4. Add different scan types (SYN scan, UDP scan, etc.)
5. Add output formatting (JSON, CSV, etc.)
6. Implement timeout and error handling
7. Add progress indicators
8. Add service fingerprinting
"""

import socket
import sys
import time
import threading


def scan_port(target, port, timeout=1.0):
    """
    Scan a single port on the target host

    Args:
        target (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        bool: True if port is open, False otherwise
    """
    # Track time it takes to connect
    start_time = time.perf_counter()
    read_data = "NONE"
    try:
        # TODO: Create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO: Set timeout
        s.settimeout(timeout)
        # TODO: Try to connect to target:port
        s.connect((target,port))
        # Send a get request (some ports will not send something on their own)
        s.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        # Read bytes to see a service banner
        read_data = (s.recv(1024)).decode(errors="ignore")
        # TODO: Close the socket
        s.close()
        # TODO: Return True if connection successful
        # Calculate connection time
        total_time = time.perf_counter() - start_time
        # Return true if the connection was successful
        # Also return the total time it took to connect
        # Also return the data read from the connection
        return True, total_time, read_data
        

    except (socket.timeout, ConnectionRefusedError, OSError):
        # Calculate connection time
        # Return false if connection failed
        total_time = time.perf_counter() - start_time
        return False, total_time, read_data


def scan_range(target, start_port, end_port):
    """
    Scan a range of ports on the target host

    Args:
        target (str): IP address or hostname to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of open ports
    """
    # Lists that will be returned and printed later
    open_ports = []
    total_times = []
    read_datas = []
    print(f"[*] Scanning {target} from port {start_port} to {end_port}")
    print(f"[*] This may take a while...")

    # Lock threads so that they don't access things at the same time
    lock = threading.Lock()

    # Use threads to scan many ports
    def thread_work(port):
        # Scan each port
        scan_result, total_time, read_data = scan_port(target, port)
        # if connection was successful, add open ports to the list
        if (scan_result == True):
            with lock:
                open_ports.append(port)
                total_times.append(total_time)
                read_datas.append(read_data)
    threads = []

    for port in range(start_port, end_port + 1):
        # Create thread
        t = threading.Thread(target= thread_work, args=(port,))
        # Start thread
        t.start()
        # Keep track of threads in a list
        threads.append(t)
    
    # Main program waits until other threads are done
    for t in threads:
        t.join()

    return open_ports, total_times, read_datas


def main():
    """Main function"""

    # Example usage (you should improve this):
    if len(sys.argv) < 2:
        print("Usage 1: python3 -m port_scanner --target <target> --ports <port>-<portX>")
        print("Example 1: python3 -m port_scanner --target 172.20.0.11 --ports 0-10000")
        print("Usage 2: python3 -m port_scanner --target <target.XX>-<target.XX> --ports <port>-<portX>")
        print("(The last part of the IP address can be changed, so that a range can be scanned)")
        print("Example 2: python3 -m port_scanner --target 172.20.0.0-172.20.0.30 --ports 0-10000")
        sys.exit(1)

    # If there is a range of hosts, parse start and end of the range
    target = sys.argv[2]
    if ('-' in target):
        h_range = sys.argv[2].split("-")
        start_host = (h_range[0])
        end_host = (h_range[1])
    else:
        start_host = target
        end_host = target

    # Parse the start and end of the range of ports
    p_range = sys.argv[4].split("-")
    start_port = int(p_range[0])
    end_port = int(p_range[1])

    # Separate the end of the address (eg. 172.20.0.21 -> 172.20.0. and 21)
   
    host_tail_start_string = start_host.split('.')[-1]
    host_tail_start= int(start_host.split('.')[-1])
    host_tail_end = int(end_host.split('.')[-1])
    tail_length = len(host_tail_start_string)
    host_base = (start_host)[0:-tail_length]
    # Loop through the range hosts
    # Check if port is open and print results
    for i in range(host_tail_start,host_tail_end + 1):
        host_string = host_base + str(i)
        print(f"[*] Starting port scan on {host_string}")
        open_ports, total_times, read_datas = scan_range(host_string, start_port, end_port)

        print(f"\n[+] Scan complete!")
        print(f"[+] Found {len(open_ports)} open ports:")

        for i in range(0,len(open_ports)):
            print(f"    Port {open_ports[i]}: OPEN")
            print(f"    {total_times[i]:3f}s")
            print(f"    {read_datas[i]}")
   


if __name__ == "__main__":
    main()
