from espflask import ESPFlask, Request, Response, create_ap, abort, redirect
from time import time
from machine import Pin #type: ignore
create_ap("ESPFlaskTestAP")
app=ESPFlask("BoardInfo")
@app.get("/")
def info(request: Request):
    response = Response("""
<h1>Request Info</h1>
Remote Address: {}<br>
Request Headers: {}<br>
HTTP Request Line: HTTP/{} {} {}<br>
Path arguments: {}<br>
Request Body: {}<br>
<h1>Board Info</h1>
Internal Time: {}<br>

""".format(request.address, request.request_headers, request.http_version, request.method, request.path, request.path_args, request.request_body, str(time())))
    response.headers.update({"Content-Type":"text/html; charset=utf-8"})
    return response
@app.get("/pin")
def pin(request: Request):
    Pin(int(request.path_args[b"pin"]),Pin.OUT).value(int(request.path_args[b"value"]))
    return Response("OK")
@app.get("/some-forbidden-path")
def forbidden(request: Request):
    return abort(403, "Forbidden")
@app.get("/to-root")
def redirect_to_root(request: Request):
    return redirect("/")
app.run(80)