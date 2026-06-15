import flask
import os
import psutil
import datetime
import time
from dataclasses import dataclass
import pathlib
import random
import nh3
import requests
import captcha
import io
import mail


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


@dataclass
class deadline:
    """Deadline for end of a thing to track. for /bully endpoint."""

    end: datetime.datetime
    name: str
    expired: bool = False

    def remaining_time(
        self,
        date: datetime.datetime = datetime.datetime.now(),
    ) -> int:
        """Returns the time in seconds till end of deadline. Assumes the date passed is BEFORE the deadline, returns negative if after

        Raises:
            Nothing

        Returns:
            int: Seconds till end
        """
        return self.end.timestamp() - date.timestamp()


deadlines: list[deadline] = []
with open("deadlines.txt", "r") as deads:
    l = deads.readlines()
    for d in l:
        split = d.split("|")
        print(split)
        deadlines.append(
            deadline(datetime.datetime.fromtimestamp(float(split[1])), split[0])
        )
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
# print(att)

# print(nh3.ALLOWED_ATTRIBUTES)
cln = nh3.Cleaner(
    tags=allowed_tags,
    clean_content_tags={"script"},
    attributes=att,
    strip_comments=False,
    link_rel="noopener noreferrer nofollow",
)

CPU_INTERVAL = 5
cwd = pathlib.Path.cwd()
print(cwd)
GUESTBOOK_PATH = str(cwd.parent) + "/disk/guestbook.txt"
CHATROOM_PATH = str(cwd.parent) + "/disk/chatroom.txt"
if not os.path.exists(str(cwd.parent) + "/disk/"):
    os.mkdir(str(cwd.parent) + "/disk/")
UAP_PATH = "static/UAP"
UAPS: list[str] = []
MAX_SCROLLBACK = 30
app = flask.Flask(__name__)
last_accessed = time.time()
last_cpu: float = psutil.cpu_percent(interval=0.5)
print(last_cpu)
CHALLENGES_FILE: str = r"./challenges.txt"
Line_Chars = 15
challenges = captcha.read_challenges_from_file(CHALLENGES_FILE)
chats: list[chat] = []
users: list[persona] = []
last_captcha = 0
captchas: dict[int, str] = {}
signatories: dict[str, float] = {}  # str = ip, float = time of last guestbook addition
for dirpath, dirnames, filenames in os.walk(UAP_PATH):
    UAPS.extend(filenames)
    break
for i in range(len(UAPS)):
    UAPS[i] = f"{UAP_PATH}/{UAPS[i]}"


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
        sigs.append(
            signature(
                stripped[0],
                conts,
                stripped[3],
                stripped[2],
                f"/images?img={stripped[1]}",
            )
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
    # print(get_guestbook())


def get_random_captcha(
    challenges: dict[str : set[str]], Line_chars: int
) -> {bytearray, str}:
    listkeys = captcha.get_challenge_questions(challenges)
    ch = random.choice(listkeys)
    img2 = captcha.generate_captcha_from_text(ch, Line_Chars)
    img_byte_arr = io.BytesIO()
    img2.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr, ch


get_guestbook()


@app.route("/.well-known/discord", methods=["GET"])
def discord():
    return "dh=fbeb7eb9df795e0918046a4d8102679bce8525cd"


@app.before_request
def before():
    print(flask.request.headers)
    if flask.request.headers.get("X-Forwarded-For", flask.request.remote_addr) == "37.143.117.214":
        flask.abort(404)
        mail.send_email("ILLEGAL ACCESS DETECTED", f"{flask.request.path}\n{datetime.datetime.now()}\n{flask.request.remote_addr}")

@app.route("/test", methods=["GET"])
def test():
    return print(flask.request.headers)
@app.route("/", methods=["GET"])
def main():
    global last_cpu
    global last_accessed
    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
    CPU = last_cpu
    to = datetime.datetime.today()
    year_percentage = datetime.datetime.now().timetuple().tm_yday / 365 * 100
    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.datetime.fromtimestamp(last_accessed).time()}.",
        "year_percentage": year_percentage,
        "cpu": last_cpu,
        "curryear": datetime.datetime.fromtimestamp(last_accessed).year,
    }
    return flask.render_template(
        "index.html",
        **context,
    )


@app.route("/bully", methods=["GET"])
def bully():
    global last_cpu
    global last_accessed
    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
    CPU = last_cpu
    to = datetime.datetime.today()
    year_percentage = datetime.datetime.now().timetuple().tm_yday / 365 * 100
    remtimes: dict = {}
    for d in deadlines:
        remtimes[d.name] = d.remaining_time(date=datetime.datetime.now())
    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.datetime.fromtimestamp(last_accessed).time()}.",
        "year_percentage": year_percentage,
        "cpu": last_cpu,
        "curryear": datetime.datetime.fromtimestamp(last_accessed).year,
        "remtimes": remtimes,
    }
    return flask.render_template(
        "bully.html",
        **context,
    )


@app.route("/send_bully", methods=["POST"])
def send_bully():
    print(flask.request.form)
    d: deadline = deadlines[int(flask.request.form.get("task_id", None))]
    print(d)
    if d.remaining_time(datetime.datetime.now()) < 0:
        d.expired = True
        mail.send_email(
            f"{flask.request.form.get("name", None)} says: {flask.request.form.get("subject", None)}",
            flask.request.form.get("text", None),
        )
    return flask.redirect("/bully")


@app.route("/maya", methods=["GET"])
def maya():
    global last_cpu
    global last_accessed
    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
    CPU = last_cpu
    to = datetime.datetime.today()
    year_percentage = datetime.datetime.now().timetuple().tm_yday / 365 * 100
    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.datetime.fromtimestamp(last_accessed).time()}.",
        "year_percentage": year_percentage,
        "cpu": last_cpu,
        "curryear": datetime.datetime.fromtimestamp(last_accessed).year,
    }
    return flask.render_template(
        "maya.html",
        **context,
    )


@app.route("/images", methods=["GET"])
def img():
    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Sec-Gpc": "1",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138"',
        "Dnt": "1",
        "Sec-Ch-Ua-Mobile": "?0",
        "Accept": "image/jxl,image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "image",
        "Referer": "http://127.0.0.1:5001/guestbook",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,cs-CZ;q=0.8,cs;q=0.7",
    }
    get_random: bool = False
    path = flask.request.args["img"]
    print(path)
    if path:
        try:
            r = requests.get(path, headers=headers)
            if not r.status_code == 200:
                get_random = True
        # print(r.content)
        # print(r.status_code)
        except:
            get_random = True

    else:
        get_random = True
    if get_random:
        print("No image!")
        with open(random.choice(UAPS), "rb") as file_t:
            file = file_t.read()
            file_t.close()
        return file
    return r.content


@app.route("/chatroom", methods=["GET"])
def chatroom():
    corrupt_persona = False
    has_account = False
    persona = None
    if flask.request.cookies:
        timeout = 20
        has_account = True
        uid = flask.request.cookies.get("uid")
        try:
            persona = users[int(uid)]
        except:
            persona = None
            corrupt_persona = True
    else:
        timeout = 60
    global last_cpu
    global last_accessed

    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
    CPU = last_cpu
    to = datetime.datetime.today()
    year_percentage = datetime.datetime.now().timetuple().tm_yday / 365 * 100
    if len(chats) > MAX_SCROLLBACK:
        chats.remove(chats[0])
    sendchats: list[sendchat] = []
    for i in chats:
        sendchats.append(sendchat(users[i.uid], i.contents))

    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.datetime.fromtimestamp(last_accessed).time()}.",
        "year_percentage": year_percentage,
        "cpu": last_cpu,
        "curryear": datetime.datetime.fromtimestamp(last_accessed).year,
        "messages": sendchats,
        "has_account": has_account,
        "persona": persona,
        "timeout": timeout,
    }

    if corrupt_persona:
        resp = flask.redirect("/clear_uid")
    else:
        resp = flask.render_template(
            "chatroom.html",
            **context,
        )
    return resp


@app.route("/clear_uid", methods=["GET"])
def clear_uid():
    resp = flask.redirect("/chatroom")
    resp.set_cookie("uid", "", expires=0)
    return resp


@app.route("/projects", methods=["GET"])
def projects():
    global last_cpu
    global last_accessed
    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
    CPU = last_cpu
    to = datetime.datetime.today()
    year_percentage = datetime.datetime.now().timetuple().tm_yday / 365 * 100
    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.datetime.fromtimestamp(last_accessed).time()}.",
        "cpu": last_cpu,
        "curryear": datetime.datetime.fromtimestamp(last_accessed).year,
    }
    return flask.render_template(
        "projects.html",
        **context,
    )


@app.route("/links", methods=["GET"])
def links():
    global last_cpu
    global last_accessed
    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
    CPU = last_cpu
    to = datetime.datetime.today()
    year_percentage = datetime.datetime.now().timetuple().tm_yday / 365 * 100
    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.datetime.fromtimestamp(last_accessed).time()}.",
        "cpu": last_cpu,
        "curryear": datetime.datetime.fromtimestamp(last_accessed).year,
    }
    return flask.render_template(
        "links.html",
        **context,
    )


@app.route("/c", methods=["GET"])
def c():
    i = captcha.generate_captcha_from_text(
        captchas[int(flask.request.args["c"])], Line_Chars
    )
    if len(captchas) > 50:
        min_id = min(captchas.keys())
        challenge_key = captchas.pop(min_id, None)
        if challenge_key is not None:
            challenges.pop(challenge_key, None)
    print(f"Len: {len(captchas)}")
    img_byte_arr = io.BytesIO()
    i.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


@app.route("/guestbook", methods=["GET"])
def guestbook():
    global last_cpu
    global last_accessed
    global last_captcha
    global captchas
    if time.time() - last_accessed >= CPU_INTERVAL:
        last_cpu = psutil.cpu_percent(interval=0.5)
        last_accessed = time.time()
        print("up")
    CPU = last_cpu
    to = datetime.datetime.today()
    listkeys = captcha.get_challenge_questions(challenges)
    ch = random.choice(listkeys)
    id = last_captcha
    last_captcha += 1
    captchas[id] = ch
    context = {
        "year": f"Today's date is the {to.day}. day of the {to.month}. month of the year {to.year}! Info as of {datetime.datetime.fromtimestamp(last_accessed).time()}.",
        "cpu": last_cpu,
        "curryear": datetime.datetime.fromtimestamp(last_accessed).year,
        "sigs": get_guestbook(),
        "captcha_img": f"/c?c={id}",
        "captcha_id": str(id),
    }
    return flask.render_template(
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
    captcha_id = None
    try:
        name = flask.request.form.get("name", None)
    except:
        return flask.redirect("/guestbook")
    try:
        contents = flask.request.form.get("text", None)
    except:
        return flask.redirect("/guestbook")
    try:
        captcha_id = flask.request.form.get("captcha_id", None)

        if (
            not flask.request.form.get("captcha", None).lower()
            in challenges[captchas[int(captcha_id)]]
        ):

            raise ValueError("Incorrect Captcha!")
        challenges.pop(captchas[int(captcha_id)])
    except Exception as e:
        print(f"malformed captcha id: {e}")
        return flask.redirect("/guestbook")
    try:
        site = flask.request.form.get("site", None)
    except:
        pass
    try:
        mail = flask.request.form.get("email", None)
    except:
        pass
    try:
        image = flask.request.form.get("image", None)
    except:
        pass
    if nh3.is_html(contents):
        cln.clean(contents)
    write_guestbook(signature(name, contents, site, mail, image))
    return flask.redirect("/guestbook")


@app.route("/persona", methods=["POST"])
def persona_set():
    global users
    global chats
    name = ""
    color = ""
    image = ""
    try:
        name = flask.request.form.get("name", None)
    except:
        return flask.redirect("/chatroom")
    try:
        color = flask.request.form.get("color", None)
    except:
        return flask.redirect("/chatroom")
    try:
        image = flask.request.form.get("image", None)
    except:
        return flask.redirect("/chatroom")
    if not len(color) == 7 or not color.startswith("#"):
        return flask.redirect("/chatroom")
    per = persona(name, image, color)
    users.append(per)
    # chats.append(chat(users.index(per), "this is a test"))
    resp = flask.redirect("/chatroom")
    resp.set_cookie("uid", str(users.index(per)))
    return resp


@app.route("/chatroom_add", methods=["POST"])
def chatroom_add():

    global chats
    corrupt_persona = False
    persona = None
    if flask.request.cookies:
        uid = flask.request.cookies.get("uid")
        try:
            persona = users[int(uid)]
        except:
            persona = None
            corrupt_persona = True
    if not corrupt_persona:
        msg = ""
        try:
            msg = flask.request.form.get("mesasge", None)
        except:
            return flask.redirect("/chatroom")
        chats.append(chat(int(uid), msg))
    resp = flask.redirect("/chatroom")
    if corrupt_persona:
        resp = flask.redirect("/clear_uid")
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
