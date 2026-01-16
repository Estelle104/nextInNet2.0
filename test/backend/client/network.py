import socket
import logging

SERVER_IP = "127.0.0.1"
DHCP_PORT = 6767
LOG_PORT = 5050
TIMEOUT = 3


def request_ip(mac):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(TIMEOUT)
        s.sendto(mac.encode(), (SERVER_IP, DHCP_PORT))
        data, _ = s.recvfrom(1024)
        return data.decode()
    except Exception:
        logging.exception("request_ip failed")
        return None
    finally:
        if s:
            try:
                s.close()
            except Exception:
                pass


def send_log(message):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((SERVER_IP, LOG_PORT))
        s.send(message.encode())
    except Exception:
        logging.exception("send_log failed")
    finally:
        if s:
            try:
                s.close()
            except Exception:
                pass
