import socket
import select
import os
import http.server
from http.server import ThreadingHTTPServer
from PyQt6.QtCore import QThread, pyqtSignal

class MediaServerThread(QThread):
    def __init__(self, file_path, port=50007, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.port = port
        self.httpd = None

    def run(self):
        file_path = self.file_path
        
        class SingleFileRangeHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress request logs to keep terminal output clean
                pass

            def do_GET(self):
                if not os.path.exists(file_path):
                    self.send_error(404, "File Not Found")
                    return

                try:
                    file_size = os.path.getsize(file_path)
                    content_type = "video/mp4"  # Default fallback
                    if file_path.lower().endswith(".mkv"):
                        content_type = "video/x-matroska"
                    elif file_path.lower().endswith(".avi"):
                        content_type = "video/x-msvideo"
                    elif file_path.lower().endswith(".mov"):
                        content_type = "video/quicktime"
                    elif file_path.lower().endswith(".wmv"):
                        content_type = "video/x-ms-wmv"

                    start = 0
                    end = file_size - 1
                    is_partial = False

                    if "Range" in self.headers:
                        range_val = self.headers["Range"]
                        try:
                            if range_val.startswith("bytes="):
                                ranges = range_val[6:].split("-")
                                start = int(ranges[0])
                                if ranges[1]:
                                    end = int(ranges[1])
                        except Exception:
                            pass
                        is_partial = True

                    if start >= file_size or end >= file_size or start > end:
                        self.send_error(416, "Requested Range Not Satisfiable")
                        return

                    f = open(file_path, "rb")
                    f.seek(start)
                    content_length = end - start + 1

                    if is_partial:
                        self.send_response(206)
                        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    else:
                        self.send_response(200)

                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(content_length))
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()

                    # Stream content in chunks to support quick seek interrupts
                    buffer_size = 64 * 1024
                    remaining = content_length
                    while remaining > 0 and not self.server.stop_requested:
                        chunk_to_read = min(buffer_size, remaining)
                        data = f.read(chunk_to_read)
                        if not data:
                            break
                        try:
                            self.wfile.write(data)
                        except Exception:
                            # Stream aborted by player (seeking or closing stream)
                            break
                        remaining -= len(data)
                    f.close()
                except Exception as e:
                    print(f"[HTTP] Error serving file: {e}")

        # Threaded server implementation to allow concurrent requests
        class ThreadedTCPServer(ThreadingHTTPServer):
            allow_reuse_address = True
            stop_requested = False

        try:
            self.httpd = ThreadedTCPServer(('', self.port), SingleFileRangeHandler)
            print(f"[HTTP] Media Server started on port {self.port} serving {self.file_path}")
            self.httpd.serve_forever()
        except Exception as e:
            print(f"[HTTP] Media Server failed to start on port {self.port}: {e}")

    def stop(self):
        if self.httpd:
            self.httpd.stop_requested = True
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
        self.wait()


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

    def send_command(self, ip, command):
        try:
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_sock.sendto(command.encode('utf-8'), (ip, self.broadcast_port))
            temp_sock.close()
            print(f"[NETWORK] Command '{command}' sent to {ip}")
        except Exception as e:
            print(f"[NETWORK] Failed sending command '{command}' to {ip}: {e}")

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
    block_triggered = pyqtSignal(str)   # URL of video
    unblock_triggered = pyqtSignal()
    play_triggered = pyqtSignal()
    pause_triggered = pyqtSignal()
    seek_triggered = pyqtSignal(int)    # position in ms
    sync_triggered = pyqtSignal(int)    # position in ms

    def __init__(self, host_ip=None, parent=None):
        super().__init__(parent)
        self.running = True
        self.host_ip = host_ip  # Optional direct Host IP address
        self.listen_port = 50005
        self.response_port = 50006
        self.sock = None

    def run(self):
        import time
        
        # Socket to listen for Host commands and broadcasts
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
            # 1. Listen for signals (select timeout of 1.0 sec)
            if has_binded:
                r, _, _ = select.select([self.sock], [], [], 1.0)
                if r:
                    try:
                        data, addr = self.sock.recvfrom(1024)
                        msg = data.decode('utf-8')
                        if msg == "VIDEO_BLOCKER_DISCOVER":
                            self.send_ack(addr[0])
                        elif msg.startswith("BLOCK_VIDEO:"):
                            url = msg.split(":", 1)[1]
                            self.block_triggered.emit(url)
                        elif msg == "PLAY":
                            self.play_triggered.emit()
                        elif msg == "PAUSE":
                            self.pause_triggered.emit()
                        elif msg == "UNBLOCK":
                            self.unblock_triggered.emit()
                        elif msg.startswith("SEEK:"):
                            try:
                                ms = int(msg.split(":", 1)[1])
                                self.seek_triggered.emit(ms)
                            except ValueError:
                                pass
                        elif msg.startswith("SYNC:"):
                            try:
                                ms = int(msg.split(":", 1)[1])
                                self.sync_triggered.emit(ms)
                            except ValueError:
                                pass
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
