import network  # type: ignore
import time
import socket
import _thread
VERSION = (0, 1, 3)


def connect_to_ap(ssid: str, password: str = "", timeout: int = 10):
    interface = network.WLAN(network.STA_IF)
    interface.active(True)
    if password:
        interface.connect(ssid, password)
    else:
        interface.connect(ssid)
    for _ in range(timeout):
        if interface.isconnected():
            return interface
        else:
            time.sleep(1)
    raise TimeoutError("Failed to connect to AP")


def construct_response(status_code: int, status_message: str, content: str, headers: dict = {"Server": "ESPFlask", "Connection": "close"}):
    response = b"HTTP/1.1 "
    response += (str(status_code)+" ").encode("utf-8")
    response += status_message.encode("utf-8")
    response += "\r\n".encode("utf-8")
    for name, value in headers.items():
        name: str
        value: str
        response += name.encode("utf-8")
        response += ": ".encode("utf-8")
        response += value.encode("utf-8")
        response += b"\r\n"
    response += "\r\n".encode("utf-8")
    response += content.encode("utf-8")
    return response


def process_request(request: bytes):
    request_lines = request.split(b"\r\n")
    headline = request_lines[0].split(b" ")
    method = headline[0]
    path = headline[1]
    http_version = headline[2].split(b"/")[1]
    del request_lines[0]
    headers = {}
    for line in request_lines:
        if not line:
            break
        line = line.decode().split(": ", 1)
        headers.update({line[0]: line[1]})
    if len(request.split(b"\r\n\r\n")) > 1:
        request_body = request.split(b"\r\n\r\n", 1)[1]
    else:
        request_body = b""
    if len(path.split(b"?", 1)) != 1:
        args = path.split(b"?", 1)[1]
        path = path.split(b"?", 1)[0]
        path_args = {}
        for arg in args.split(b"&"):
            arg = arg.split(b"=", 1)
            path_args.update({arg[0]: arg[1]})
    else:
        path_args = {}
    return method, path, http_version, headers, path_args, request_body


class Request:
    def __init__(self, conn: socket.socket, address: tuple[str, int], method: bytes, path: bytes, http_version: bytes, headers: dict, path_args: dict, request_body: bytes, logs=True) -> None:
        self.address, self.method, self.path, self.http_version, self.headers, self.path_args, self.request_body, self.connection, self.logs = address, method, path, http_version, headers, path_args, request_body, conn, logs
        self.headers = {"Server": "ESPFlask", "Connection": "close"}

    def finish(self, content: str, status_code: int = 200, status_text: str = "OK"):
        try:
            self.connection.send(construct_response(
                status_code, status_text, content, self.headers))
            if self.logs:
                print(f"I: HTTP/1.1 {self.method.decode()}"
                      f"{self.path.decode()} - {status_code} {status_text}")
            self.connection.close()
        except:
            pass

    def abort(self, error_code: int = 500, status_text: str = "Internal Server Error"):
        self.headers.update({"Content-Type": "text/html; charset=utf-8"})
        self.finish(f"<html><head><title>{error_code} {status_text}</title></head><body><center><h1>{error_code} {status_text}</h1></center><hr><center>ESPFlask/{'.'.join(map(str, VERSION))}</center></body></html>",
                    error_code,
                    status_text=status_text)


class BaseWebApp:
    def __init__(self, name) -> None:
        self.name = name

    def handler(self, request: Request, address: tuple[str, int], method: bytes, path: bytes, http_version: bytes, headers: dict, path_args: dict, request_body: bytes) -> tuple[int, str, str]:
        raise NotImplementedError

    def _connected(self, conn: socket.socket, addr):
        conn.settimeout(5)
        data = conn.recv(1024)
        if not data:
            return
        try:
            method, path, http_version, headers, path_args, request_body = process_request(
                data)
        except:
            conn.send(construct_response(
                400, "Bad Request", f"400 Bad Request"))
            conn.close()
            return
        request = Request(conn, addr, method, path,
                          http_version, headers, path_args, request_body)
        try:
            self.handler(request)
            return
        except Exception as e:
            request.abort(500, "Internal Server Error")
            return

    def run(self, port: int, host: str = "0.0.0.0", listen_number: int = 5):
        print(f"I: Running ESPFlask APP \"{self.name}\" On {host}:{port}")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        while 1:
            conn, addr = self.socket.accept()
            try:
                _thread.start_new_thread(self._connected, (conn, addr))
            except:
                print(f"W: Server overload!")


class ESPFlask:
    def __init__(self, appname) -> None:
        self.appname = appname
        self.routes = {}

    def route(self, method, path) -> None:
        def decorator(func):
            if path in self.routes.keys():
                self.routes[path][method] = func
            else:
                self.routes[path] = {method: func}
        return decorator

    def _router(self, request: Request):
        if request.path.decode() not in self.routes.keys():
            return request.abort(404, "Not Found")
        if request.method.decode() not in self.routes[request.path.decode()].keys():
            return request.abort(400, "Forbidden")
        self.routes[request.path.decode()][request.method.decode()](request)

    def run(self, port: int, host: str = "0.0.0.0", listen_number: int = 5):
        runner = BaseWebApp(self.appname)
        runner.handler = self._router
        runner.run(
            port=port,
            host=host,
            listen_number=listen_number
        )
