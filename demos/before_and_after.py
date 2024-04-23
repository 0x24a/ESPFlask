from espflask import ESPFlask, Request, Response, create_ap
from time import ticks_us, ticks_diff
import esp32 #type: ignore

create_ap("ESPFlaskTestAP")
app=ESPFlask("Process time")

@app.before_request
def before_request(request: Request):
    request.start_time = ticks_us()

@app.before_response
def before_response(request: Request, response: Response):
    response.headers.update({"X-Process-Time": str(ticks_diff(ticks_us(),request.start_time)), "X-Server-Temperature":str(esp32.raw_temperature())})

app.run(80)
