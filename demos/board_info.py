from espflask import ESPFlask, Request
import espflask
from time import time
app=ESPFlask("BoardInfo")
@app.get("/")
def info(request: Request):
    request.headers.update({"Content-Type":"text/html"})
    return request.finish("""
<h1>Request Info</h1>
Remote Address: {}<br>
Request Headers: {}<br>
HTTP Request Line: HTTP/{} {} {}<br>
Path arguments: {}<br>
Request Body: {}<br>
<h1>Board Info</h1>
Internal Time: {}<br>

""".format(request.address, request.request_headers, request.http_version, request.method, request.path, request.path_args, request.request_body, str(time())))
app.run(80)