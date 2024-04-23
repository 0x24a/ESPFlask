import network  # type: ignore
import time
import socket
import _thread
VERSION = (0, 1, 6)


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

def create_ap(ssid: str, password: str = ""):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    if password:
        ap.config(essid=ssid, password=password)
    else:
        ap.config(essid=ssid)

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
    def __init__(self, connection: socket.socket, address: tuple[str, int], method: bytes, path: bytes, http_version: bytes, headers: dict, path_args: dict, request_body: bytes, logs=True) -> None:
        self.connection, self.address, self.method, self.path, self.http_version, self.request_headers, self.path_args, self.request_body, self.logs = connection, address, method, path, http_version, headers, path_args, request_body, logs
        self.headers = {"Server": "ESPFlask", "Connection": "close"}

class Response:
    def __init__(self, content: str, status_code: int = 200, status_text: str = "OK", headers: dict = {"Server": "ESPFlask", "Connection": "close"}) -> None:
        self.content = content
        self.status_code = status_code
        self.status_text = status_text
        self.headers = headers
    def construct_response(self):
        return construct_response(self.status_code, self.status_text, self.content, self.headers)

def abort(error_code: int = 500, status_text: str = "Internal Server Error") -> Response:
    response = Response(
        content=f"<html><head><title>{error_code} {status_text}</title></head><body><center><h1>{error_code} {status_text}</h1></center><hr><center>ESPFlask/{'.'.join(map(str, VERSION))}</center></body></html>",
        status_code=error_code,
        status_text=status_text
    )
    return response

def redirect(path: str, code: int = 301):
    response = abort(code, "Redirected")
    response.headers.update({"Location": path})
    return response


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
            print("W: Error in handler: ",str(type(e)),str(e))
            request.connection.send(abort(500, "Internal Server Error").construct_response())
            request.connection.close()
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
                conn.send(abort(503,"Service Temporarily Unavailable").construct_response())
                conn.close()


class ESPFlask:
    def __init__(self, appname) -> None:
        self.appname = appname
        self.routes = {}
        self.before_request_functions = []
        self.before_response_functions = []
        # self.error_handlers: dict[int,list] = {}

    def route(self, path, methods=["GET"]):
        def decorator(func):
            if path in self.routes.keys():
                for method in methods:
                    self.routes[path][method] = func
            else:
                for method in methods:
                    self.routes[path] = {method: func}
            return func
        return decorator
    
    def get(self, path):
        return self.route(path)
    def post(self, path):
        return self.route(path, methods=["POST"])
    def put(self, path):
        return self.route(path, methods=["PUT"])
    def delete(self, path):
        return self.route(path, methods=["DELETE"])
    def head(self, path):
        return self.route(path, methods=["HEAD"])
    # def errorhandler(self, error_code: int):
    #     def decorator(func):
    #         if error_code in self.error_handlers.keys():
    #             self.error_handlers[error_code].append(func)
    #         else:
    #             self.error_handlers[error_code]=[func]
    #         return func
    #     return decorator
    def before_request(self, func):
        self.before_request_functions.append(func)
        def decorator(*args, **kwargs):
            func(*args, **kwargs)
        return decorator
    
    def before_response(self, func):
        self.before_response_functions.append(func)
        def decorator(*args, **kwargs):
            func(*args, **kwargs)
        return decorator

    def _router(self, request: Request):
        for function in self.before_request_functions:
            function(request)
        if request.path.decode() not in self.routes.keys():
            print(f"I: {request.method.decode()} {request.path.decode()} - 404 Not Found")
            response=abort(404, "Not Found")
            for function in self.before_response_functions:
                function(request, response)
            request.connection.send(response.construct_response())
            return request.connection.close()
        if request.method.decode() not in self.routes[request.path.decode()].keys():
            print(f"I: {request.method.decode()} {request.path.decode()} - 400 Method Not Allowed")
            response=abort(400, "Method Not Allowed")
            for function in self.before_response_functions:
                function(request, response)
            request.connection.send(response.construct_response())
            return request.connection.close()
        response = self.routes[request.path.decode()][request.method.decode()](request)
        if type(response) == str:
            response = Response(response)
        elif type(response) == tuple:
            if len(response) != 3:
                print("W: Invaild view function response")
                response = abort(500, "Internal Server Error")
            else:
                response = Response(response[2], response[0], response[1])
        elif type(response) == Response:
            pass
        else:
            print("W: Invaild view function response")
            response = abort(500, "Internal Server Error")
        print(f"I: {request.method.decode()} {request.path.decode()} - {response.status_code} {response.status_text}")
        for function in self.before_response_functions:
            function(request, response)
        print(response.construct_response())
        request.connection.send(response.construct_response())
        request.connection.close()

    def run(self, port: int, host: str = "0.0.0.0", listen_number: int = 5):
        runner = BaseWebApp(self.appname)
        runner.handler = self._router
        runner.run(
            port=port,
            host=host,
            listen_number=listen_number
        )
