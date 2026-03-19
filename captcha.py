from PIL import Image, ImageFont, ImageDraw
import random


def generate_captcha_from_text(input_text: str, Line_Chars: int) -> Image:
    sImg = "base.png"  # source image
    sFont = "AdwaitaMono-Regular.ttf"  # font file
    sSize = random.randint(28, 32)  # font size
    sColor = (1, 1, 1)  # text color
    sPos = (random.randint(0, 30), random.randint(0, 30))  # write text at this position
    ind = 0
    nls = 0
    sText = ""
    for i in input_text:
        ind += 1
        sText += i
        if ind % Line_Chars == 0:
            sText += "\n"
            nls += 1
            if nls > 6:
                raise ValueError("Text too long")

    iOpen = Image.open(sImg)
    pixels = iOpen.load()
    width, height = iOpen.size
    for h in range(height):
        for w in range(width):
            pixels[w, h] = (
                random.randint(0, 150),
                random.randint(0, 150),
                random.randint(0, 150),
            )
    iDraw = ImageDraw.Draw(iOpen)
    iFont = ImageFont.truetype(sFont, sSize)
    iDraw.text(sPos, sText, fill=sColor, font=iFont)
    pixels = iOpen.load()
    for h in range(height):
        for w in range(width):
            if pixels[w, h] == sColor:
                pixels[w, h] = (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255),
                )
    """    for i in range(int((w * h) * (random.randint(5, 30) / 30))):
        pixels[random.randint(0, w), random.randint(0, h)] = (
            random.randint(50, 240),
            random.randint(50, 240),
            random.randint(50, 240),
        )"""
    return iOpen


def read_challenges_from_file(CHALLENGES_FILE: str) -> dict[str : set[str]]:
    challenges: dict[str : set[str]] = {}
    with open(CHALLENGES_FILE, "r") as f:
        for l in f.readlines():
            l = l.split(":")
            question = l[0].strip()
            answers = l[1].split(",")
            for a in answers:
                answers[answers.index(a)] = a.strip().strip("\n")
            answers = set(answers)
            challenges[question] = answers
    return challenges


def get_challenge_questions(challenges):
    listkeys = []
    for k in challenges.keys():
        listkeys.append(k)
    return listkeys


if __name__ == "__main__":
    challenges = read_challenges_from_file(r"challenges.txt")
    generate_captcha_from_text(random.choice(get_challenge_questions(challenges)))
