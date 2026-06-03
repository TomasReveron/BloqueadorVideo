import socket
import select
from PyQt6.QtCore import QThread, pyqtSignal

class DiscoveryServer(QThread):
    device_found = pyqtSignal(str, str)  # Emits (hostname, ip)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.broadcast_port = 50005
        self.listen_port = 50006
        self.sock = None
        self.broadcast_sock = None

    def run(self):
        # Socket to listen for Guest response packets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(('', self.listen_port))
        except Exception as e:
            print(f"[NETWORK] Error binding discovery listener on port {self.listen_port}: {e}")
            return

        # Socket to broadcast discovery signals to clients
        self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        print(f"[NETWORK] Host Discovery Server active. Listening on UDP port {self.listen_port}...")

        # Immediate first discovery ping
        self.send_ping()

        counter = 0
        while self.running:
            # Check for incoming data (non-blocking, select timeout of 1.0 sec)
            r, _, _ = select.select([self.sock], [], [], 1.0)
            if r:
                try:
                    data, addr = self.sock.recvfrom(1024)
                    msg = data.decode('utf-8')
                    if msg.startswith("VIDEO_BLOCKER_GUEST_ACK:"):
                        hostname = msg.split(":", 1)[1]
                        ip = addr[0]
                        self.device_found.emit(hostname, ip)
                except Exception as e:
                    if self.running:
                        print(f"[NETWORK] Error receiving response: {e}")

            # Send discovery broadcast every 4 seconds
            counter += 1
            if counter >= 4:
                self.send_ping()
                counter = 0

        self.close_sockets()

    def send_ping(self):
        if not self.running:
            return
        try:
            print(f"[NETWORK] Broadcasting DISCOVER to 255.255.255.255:{self.broadcast_port}...")
            self.broadcast_sock.sendto(
                b"VIDEO_BLOCKER_DISCOVER", 
                ('255.255.255.255', self.broadcast_port)
            )
        except Exception as e:
            print(f"[NETWORK] Broadcast send failed: {e}")

    def close_sockets(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        if self.broadcast_sock:
            try:
                self.broadcast_sock.close()
            except:
                pass

    def stop(self):
        self.running = False
        self.close_sockets()
        self.wait() # Wait for thread to finish cleanly


class DiscoveryClient(QThread):
    def __init__(self, host_ip=None, parent=None):
        super().__init__(parent)
        self.running = True
        self.host_ip = host_ip  # Optional direct Host IP address
        self.listen_port = 50005
        self.response_port = 50006
        self.sock = None

    def run(self):
        import time
        
        # Socket to listen for Host discovery broadcasts
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        has_binded = False
        try:
            self.sock.bind(('', self.listen_port))
            has_binded = True
            print(f"[NETWORK] Guest Discovery Client active. Listening on UDP port {self.listen_port}...")
        except Exception as e:
            print(f"[NETWORK] Guest listener socket failed to bind: {e}")
            if self.host_ip:
                print("[NETWORK] Continuing in Unicast-Only mode.")
            else:
                return

        if self.host_ip:
            print(f"[NETWORK] Unicast ping enabled to targeted Host IP: {self.host_ip}")

        counter = 0
        while self.running:
            # 1. Listen for broadcasts (select timeout of 1.0 sec)
            if has_binded:
                r, _, _ = select.select([self.sock], [], [], 1.0)
                if r:
                    try:
                        data, addr = self.sock.recvfrom(1024)
                        msg = data.decode('utf-8')
                        if msg == "VIDEO_BLOCKER_DISCOVER":
                            self.send_ack(addr[0])
                    except Exception as e:
                        if self.running:
                            print(f"[NETWORK] Guest socket receive error: {e}")
            else:
                # If socket binding failed, sleep 1.0s to simulate select timeout
                time.sleep(1.0)

            # 2. Periodically send active unicast ping to targeted Host IP
            if self.host_ip:
                counter += 1
                if counter >= 3:  # Send ping every 3 seconds
                    self.send_ack(self.host_ip)
                    counter = 0

        self.close_sockets()

    def send_ack(self, target_ip):
        try:
            hostname = socket.gethostname()
            response = f"VIDEO_BLOCKER_GUEST_ACK:{hostname}"
            
            # Create a temporary socket to send unicast response
            reply_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            reply_sock.sendto(response.encode('utf-8'), (target_ip, self.response_port))
            reply_sock.close()
            print(f"[NETWORK] Sent ACK to Host at {target_ip} ({hostname})")
        except Exception as e:
            print(f"[NETWORK] Failed sending ACK to {target_ip}: {e}")

    def close_sockets(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass

    def stop(self):
        self.running = False
        self.close_sockets()
        self.wait()
