import socket
from typing import Any, List, Optional, Union 

class MiniRedis:
    
    def __init__(self, host: str = "127.0.0.1", port: int = 6379, timeout: float = 3.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        
    
    def connect(self):
        s = socket.create_connection((self.host, self.port), timeout=self.timeout)
        s.settimeout(self.timeout)
        
    def _encode(self, parts:List[Union[str, bytes, int]]):
        out = [f"*{len(parts)}\r\n".encode()]
        for p in parts:
            if isinstance(p, int):
                b = str(p).encode()
            elif isinstance(p, bytes):
                b = p
            else:
                b = p.encode()
            out.append(f"${len(b)}\r\n".encode() + b + b"\r\n")
        return b"".join(out)
    
    def read_line(self, s:socket.socket) -> bytes:
        buff = bytearray()
        while True:
            ch = s.recv(1)
            if not ch:
                raise ConnectionError("Redis connection closed")
            buff += ch
            if len(buff) >= 2 and buff[-2:] == b"\r\n":
                return bytes(buff[:-2])
            
    def _readexact(self, s: socket.socket, n: int) -> bytes:
        data = bytearray()
        while len(data) < n:
            chunk = s.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Redis connection closed")
            data += chunk
        return bytes(data)
