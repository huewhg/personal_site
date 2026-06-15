import flask
from dataclasses import dataclass
import orjson
import pathlib

cwd = pathlib.Path.cwd()
QUIZ_PATH = str(cwd.parent) + "/disk/quiz.json"


@dataclass
class question:
    contents: str
    answers: list[str]
    eval_contents: bool = False
    answer_eval: str = ""
    manual_scoring: bool = False


@dataclass
class quiz:
    questions: list[question]
    timed: bool = False
    random_order: bool = True
    random_ammount_of_questions: bool = False


tempquestion: question = question(
    answer_eval='f"{30**3} - test"',
    answers=[],
    eval_contents=True,
    contents='f"What is {30**3}"',
)
questions: list[question] = []
for i in range(300):
    questions.append(tempquestion)
tempquiz: quiz = quiz(
    questions=questions, timed=True, random_order=True, random_ammount_of_questions=True
)
print(eval(tempquestion.answer_eval))
with open(QUIZ_PATH, "w") as f:
    f.write(orjson.dumps)
    f.flush()
