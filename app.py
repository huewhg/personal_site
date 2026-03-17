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
from pathlib import Path
import random
import nh3
import requests

@dataclass
class signature:
    name: str
    contents: str
    site: str = None
    mail: str = None
    image: str = None


@dataclass
class persona:
    user: str
    image: str
    color: str


@dataclass
class chat:
    uid: int
    contents: str


@dataclass
class sendchat:
    user: persona
    contents: str


attrs = {
    "href",
    "name",
    "target",
    "title",
    "id",
    "rel",
    "width",
    "height",
    "direction",
    "style",
    "class",
    "role",
    "aria-controls",
}
tags = {
    "a",
    "h1",
    "h2",
    "h3",
    "strong",
    "em",
    "p",
    "ul",
    "ol",
    "li",
    "br",
    "sub",
    "sup",
    "hr",
    "marquee",
    "del",
    "ins",
    "code",
    "abbr",
    "meter",
    "progress",
    "img",
    "details",
    "summary",
    "blockquote",
    "cite",
    "time",
    "datalist",
    "mark",
    "audio",
    "video",
}
allowed_tags = nh3.ALLOWED_TAGS | tags
att: dict[str, set[str]] = {}
for t in tags:
    att[t] = attrs
att["a"].discard("rel")
print(att)

# print(nh3.ALLOWED_ATTRIBUTES)
cln = nh3.Cleaner(
    tags=allowed_tags,
    clean_content_tags={"script"},
    attributes=att,
    strip_comments=False,
    link_rel="noopener noreferrer nofollow",
)

CPU_INTERVAL = 5
cwd = Path.cwd()
print(cwd)
GUESTBOOK_PATH = str(cwd.parent) + "/disk/guestbook.txt"
CHATROOM_PATH = str(cwd.parent) + "/disk/chatroom.txt"
MAX_SCROLLBACK = 30
app = Flask(__name__)
last_accessed = time.time()
last_cpu: float = psutil.cpu_percent(interval=0.5)
print(last_cpu)

chats: list[chat] = []
users: list[persona] = []


def init_guestbook(path: str) -> None:
    if not os.path.isfile(path):
        file = open(path, "w")
        file.write("")
        file.close()
        print(f"{path} created successfully!")


def set_persona(
    users: list[persona],
    uid: int,
    name: str = None,
    color: str = None,
    image: str = None,
) -> None:
    u = users[uid]
    if not name:
        newname = u.user
    else:
        newname = name
    if not color:
        newcolor = u.color
    else:
        newcolor = color
    if not image:
        newimage = u.image
    else:
        newimage = image
    users[uid] = persona(newname, newimage, newcolor)


init_guestbook(GUESTBOOK_PATH)
# init_guestbook(CHATROOM_PATH)


def get_guestbook() -> list[signature]:
    init_guestbook(GUESTBOOK_PATH)
    file = open(GUESTBOOK_PATH, "r")
    sigs: list[signature] = []
    for i in file:
        split = i.split("|")
        stripped = []
        for i in split:
            stripped.append(i.strip("\n").strip())
        conts = stripped[4].replace("_%", "<br />")
        if nh3.is_html(conts):
            conts = cln.clean(conts)
        print(stripped)
        sigs.append(
            signature(stripped[0], conts, stripped[3], stripped[2], f"/images?img={stripped[1]}")
        )

    file.close()
    sigs.reverse()
    return sigs


def write_guestbook(s: signature) -> None:
    init_guestbook(GUESTBOOK_PATH)
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


@app.route("/images", methods=["GET"])
def img():
    print(request.headers)
    headers = {
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Sec-Gpc": "1",
    "Sec-Ch-Ua-Platform": "\"Linux\"",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Sec-Ch-Ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\"",
    "Dnt": "1",
    "Sec-Ch-Ua-Mobile": "?0",
    "Accept": "image/jxl,image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Dest": "image",
    "Referer": "http://127.0.0.1:5001/guestbook",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,cs-CZ;q=0.8,cs;q=0.7"}
    
    r = requests.get(request.args["img"], headers=headers)
    #print(r.content)
    print(r.status_code)
    if not r.status_code == 200:
        return 404
    return r.content


@app.route("/chatroom", methods=["GET"])
def chatroom():
    corrupt_persona = False
    has_account = False
    persona = None
    if request.cookies:
        has_account = True
        uid = request.cookies.get("uid")
        try:
            persona = users[int(uid)]
        except:
            print("corrupt!")
            persona = None
            corrupt_persona = True

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
    if len(chats) > MAX_SCROLLBACK:
        chats.remove(chats[0])
    sendchats: list[sendchat] = []
    for i in chats:
        sendchats.append(sendchat(users[i.uid], i.contents))

    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.fromtimestamp(last_accessed).time()}.",
        "year_percentage": year_percentage,
        "cpu": last_cpu,
        "curryear": datetime.fromtimestamp(last_accessed).year,
        "messages": sendchats,
        "has_account": has_account,
        "persona": persona,
    }

    if corrupt_persona:
        resp = redirect("/clear_uid")
    else:
        resp = render_template(
            "chatroom.html",
            **context,
        )
    return resp


@app.route("/clear_uid", methods=["GET"])
def clear_uid():
    resp = redirect("/chatroom")
    resp.set_cookie("uid", "", expires=0)
    return resp


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
        "cpu": last_cpu,
        "curryear": datetime.fromtimestamp(last_accessed).year,
    }
    return render_template(
        "projects.html",
        **context,
    )


@app.route("/links", methods=["GET"])
def links():
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
        "cpu": last_cpu,
        "curryear": datetime.fromtimestamp(last_accessed).year,
    }
    return render_template(
        "links.html",
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
    if nh3.is_html(contents):
        cln.clean(contents)
    write_guestbook(signature(name, contents, site, mail, image))
    return redirect("/guestbook")


@app.route("/persona", methods=["POST"])
def persona_set():
    global users
    global chats
    name = ""
    color = ""
    image = ""
    print(request.form)
    try:
        name = request.form.get("name", None)
    except:
        return redirect("/chatroom")
    try:
        color = request.form.get("color", None)
        print(color)
    except:
        return redirect("/chatroom")
    try:
        image = request.form.get("image", None)
    except:
        return redirect("/chatroom")
    if not len(color) == 7 or not color.startswith("#"):
        return redirect("/chatroom")
    per = persona(name, image, color)
    users.append(per)
    # chats.append(chat(users.index(per), "this is a test"))
    resp = redirect("/chatroom")
    resp.set_cookie("uid", str(users.index(per)))
    return resp


@app.route("/chatroom_add", methods=["POST"])
def chatroom_add():

    global chats
    corrupt_persona = False
    persona = None
    if request.cookies:
        uid = request.cookies.get("uid")
        try:
            persona = users[int(uid)]
        except:
            print("corrupt!")
            persona = None
            corrupt_persona = True
    if not corrupt_persona:
        msg = ""
        print(request.form)
        try:
            msg = request.form.get("mesasge", None)
        except:
            return redirect("/chatroom")
        print(msg)
        chats.append(chat(int(uid), msg))
    resp = redirect("/chatroom")
    if corrupt_persona:
        resp = redirect("/clear_uid")
    return resp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if not port == 5000:
        # Render injects PORT env var
        print("render")
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        print("local")
        app.run(host="127.0.0.1", port=5001, debug=True)
