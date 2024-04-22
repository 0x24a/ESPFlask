from espflask import ESPFlask, Request, Response
from time import time
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
app.run(80)