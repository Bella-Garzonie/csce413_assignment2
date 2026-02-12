## Port Knocking Starter Template

This directory is a starter template for the port knocking portion of the assignment.

### What you need to implement
- Pick a protected service/port (default is 2222).
- Define a knock sequence (e.g., 1234, 5678, 9012).
- Implement a server that listens for knocks and validates the sequence.
- Open the protected port only after a valid sequence.
- Add timing constraints and reset on incorrect sequences.
- Implement a client to send the knock sequence.

### Getting started
1. Implement your server logic in `knock_server.py`.
2. Implement your client logic in `knock_client.py`.
3. Update `demo.sh` to demonstrate your flow.
4. Run from the repo root with `docker compose up port_knocking`.

### Example usage
```bash
python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012
```
# Implementation explanation
 My implementation uses threads to listen for knocks from each port simultaneously. The knock listener in the server tracks progress by updating an iterator if the sequence is followed, and it resets the iterator if the sequence is broken. The knock listener also organizes progress for each port based on its IP address using dictionaries. This allows it to keep track of the same port number on different IP addresses. My implementation also uses a time limit: If the time between a first knock and any successive knocks in a sequence is over the time limit, the server prints a message to the screen and restarts the sequence progress. If the knocks match the specific sequence, the server will open the port using firewall rules. After a set time, the server will close the port.
