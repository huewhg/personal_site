from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    send_from_directory,
    url_for,
    flash,
)
import os
import psutil
from datetime import datetime
import time
CPU_INTERVAL = 5
app = Flask(__name__)
last_accessed = time.time()
last_cpu:float = psutil.cpu_percent(interval=0.5)
print(last_cpu)
@app.route("/", methods=["GET"])
def main():
    global last_cpu
    global last_accessed
    print(time.time() - last_accessed)
    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
        print("up")
    CPU = last_cpu
    to = datetime.today()
    year_percentage = datetime.now().timetuple().tm_yday / 365 * 100
    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.fromtimestamp(last_accessed).time()}.",
        "year_percentage": year_percentage,
        "cpu": last_cpu,
        "curryear":datetime.fromtimestamp(last_accessed).year    
    }
    return render_template(
        "index.html",
        **context,
    )
@app.route("/projects", methods=["GET"])
def projects():
    global last_cpu
    global last_accessed
    print(time.time() - last_accessed)
    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
        print("up")
    CPU = last_cpu
    to = datetime.today()
    year_percentage = datetime.now().timetuple().tm_yday / 365 * 100
    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.fromtimestamp(last_accessed).time()}.",
        "year_percentage": year_percentage,
        "cpu": last_cpu,
        "curryear":datetime.fromtimestamp(last_accessed).year    
    }
    return render_template(
        "projects.html",
        **context,
    )

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 5000))  # Render injects PORT env var
        print("render")
        app.run(host="0.0.0.0", port=port)
    except:
        print("local")
        app.run(host="127.0.0.1", port=5001, debug=False)
