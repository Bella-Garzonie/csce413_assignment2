#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import threading
import time
import subprocess

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0

lock = threading.Lock()
knock_times = {}
prog = {}

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def open_protected_port(protected_port):
    """Open the protected port using firewall rules."""
    # TODO: Use iptables/nftables to allow access to protected_port.
    # Open the protected port by accepting incoming traffic (iptables -A INPUT -p tcp --dport (protected port) -j ACCEPT)
    subprocess.run(["iptables", "-I", "INPUT","1", "-p", "tcp", "--dport", str(protected_port), "-j", "ACCEPT"], check = True)


def close_protected_port(protected_port):
    """Close the protected port using firewall rules.""" 
    # TODO: Remove firewall rules for protected_port.
    # Close the port by dropping all incoming traffic (iptables -A INPUT -p tcp --dport (protected port) -j DROP)
    subprocess.run(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(protected_port), "-j", "DROP"], check = True)
    
def port_listen(port,window,sequence, protected_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Listen on all IPs since specific one was not given, so bind to 0.0.0.0
    s.bind(("0.0.0.0",port))
    s.listen()
    while True:
        # Accept incoming requests (listen for knocks)
        connect, addr = s.accept()
        # Keep track of time the knock happened 
        knock_time = time.time()
        # Get IP address of knock
        ip = addr[0]
        print(f"Knock on {port} on IP {ip}")
        
        # Only one thread can change important values at a time
        with lock:
            # Get the progess in the sequence for the IP
            iter = prog.get(ip,0)
            # Check if port matches the steps in the sequence
            if port == sequence[iter]:
                # Separate knock times by IP address
                if ip not in knock_times:
                    knock_times[ip]=[]
                knock_times[ip].append(knock_time)
                # Calculate duration of sequence so far
                duration = knock_time - knock_times[ip][0]
                # Make sure the duration of knocks does not exceed window
                if duration < window:
                    # Since port matched, increase progress iterator by one
                    prog[ip] = iter + 1
                    # If iter == len(sequence), then the sequence is over
                    if  prog[ip]==len(sequence):
                        # On correct sequence, call open_protected_port().
                        open_protected_port(protected_port)
                        print(f"PROTECTED PORT {protected_port} OPEN! ")
                        time.sleep(10)
                        print(f"PROTECTED PORT {protected_port} CLOSED! ")
                        close_protected_port(protected_port)
                        # Reset progress
                        prog[ip] = 0
                        knock_times[ip].clear()
                else:
                    # Duration too long, reset progress
                    prog[ip] = 0
                    knock_times[ip].clear()
                    print("TIME EXPIRED")
            else:
                # Sequence is wrong, reset progress
                prog[ip] = 0
                knock_times[ip].clear()
                print("WRONG SEQUENCE")
            
        connect.close()
    

def listen_for_knocks(sequence, window_seconds, protected_port):
    close_protected_port(protected_port)
    threads = []
    """Listen for knock sequence and open the protected port."""
    logger = logging.getLogger("KnockServer")
    logger.info("Listening for knocks: %s", sequence)
    logger.info("Protected port: %s", protected_port)
    # Create a listener for each thread in the correct sequence
    # Create threads to listen to different ports simultaneously
    for port in sequence:
        if port in sequence:
            # Each thread runs port_listen
            new_thread = threading.Thread(target=port_listen,args=(port,window_seconds, sequence, protected_port))
            # Kill thread if program exits
            new_thread.daemon = True
            # start thread
            new_thread.start()
            # Add thread to list
            threads.append(new_thread)

    while True:
        time.sleep(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server starter")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")
    listen_for_knocks(sequence, args.window, args.protected_port)


if __name__ == "__main__":

    main()
