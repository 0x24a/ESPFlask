from espflask import ESPFlask, Request, Response, abort, redirect, create_ap
app=ESPFlask("Hello world")
create_ap("ESPFlaskTestAP")
@app.get("/")
def mainpage(request: Request):
    response = Response("<h1>Hello, world!</h1>")
    response.headers.update({"Content-Type":"text/html; charset=utf-8"})
    return response
@app.get("/some-forbidden-path")
def forbidden(request: Request):
    return abort(403, "Forbidden")
@app.get("/to-root")
def redirect_to_root(request: Request):
    return redirect("/")
app.run(80)