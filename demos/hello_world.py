from espflask import ESPFlask, Request
app=ESPFlask("Hello world")
@app.route("GET", "/")
def mainpage(request: Request):
    request.headers.update({"Content-Type":"text/html; charset=utf-8"})
    return request.finish("<h1>Hello, world!</h1>")
@app.route("GET", "/some-forbidden-path")
def forbidden(request: Request):
    return request.abort(403, "Forbidden")
app.run(80)