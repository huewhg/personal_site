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
from dataclasses import dataclass


@dataclass
class signature:
    name: str
    contents: str
    site: str = None
    mail: str = None
    image: str = None


CPU_INTERVAL = 5
GUESTBOOK_PATH = r"./guestbook.txt"
app = Flask(__name__)
last_accessed = time.time()
last_cpu: float = psutil.cpu_percent(interval=0.5)
print(last_cpu)


def init_guestbook() -> None:
    if not os.path.isfile(GUESTBOOK_PATH):
        file = open(GUESTBOOK_PATH, "w")
        file.write("")
        file.close()
        print("Guestbook created successfully!")


init_guestbook()


def get_guestbook() -> list[signature]:
    init_guestbook()
    file = open(GUESTBOOK_PATH, "r")
    sigs: list[signature] = []
    for i in file:
        split = i.split("|")
        stripped = []
        for i in split:
            stripped.append(i.strip("\n").strip())
        conts = stripped[4].replace("_%", "\n")
        print(stripped)
        sigs.append(
            signature(stripped[0], conts, stripped[3], stripped[2], stripped[1])
        )

    file.close()
    sigs.reverse()
    return sigs


def write_guestbook(s: signature) -> None:
    init_guestbook()
    file = open(GUESTBOOK_PATH, "a")
    newconts = s.contents.replace("\n", "_%").replace("\r", "")

    file.write(f"{s.name}|{s.image}|{s.mail}|{s.site}|{newconts}\n")
    file.close()
    print(get_guestbook())


get_guestbook()


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
        "curryear": datetime.fromtimestamp(last_accessed).year,
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
        "curryear": datetime.fromtimestamp(last_accessed).year,
    }
    return render_template(
        "projects.html",
        **context,
    )


@app.route("/guestbook", methods=["GET"])
def guestbook():
    global last_cpu
    global last_accessed
    print(time.time() - last_accessed)
    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
        print("up")
    CPU = last_cpu
    to = datetime.today()
    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.fromtimestamp(last_accessed).time()}.",
        "cpu": last_cpu,
        "curryear": datetime.fromtimestamp(last_accessed).year,
        "sigs": get_guestbook(),
    }
    return render_template(
        "guestbook.html",
        **context,
    )


@app.route("/guestbook_add", methods=["POST"])
def guestbook_add():
    name = ""
    contents = ""
    site = None
    mail = None
    image = None
    try:
        name = request.form.get("name", None)
    except:
        return redirect("/guestbook")
    try:
        contents = request.form.get("text", None)
    except:
        return redirect("/guestbook")
    try:
        site = request.form.get("site", None)
    except:
        pass
    try:
        mail = request.form.get("email", None)
    except:
        pass
    try:
        image = request.form.get("image", None)
    except:
        pass
    write_guestbook(signature(name, contents, site, mail, image))
    return redirect("/guestbook")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if not port == 5000:
        # Render injects PORT env var
        print("render")
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        print("local")
        app.run(host="127.0.0.1", port=5001, debug=True)
