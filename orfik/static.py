import os
import logging
from hashlib import sha512
from pathlib import Path

import htmlmin
from jinja2 import Environment, FileSystemLoader, Template
from orfik.questions import get_questions, Question


def build(args):
    templates_dir = Path(args.templates_dir)
    target_dir = Path(args.target_dir)
    env = Environment(loader=FileSystemLoader(templates_dir))
    html = env.get_template("index.html").render(api_base=args.api_base)
    with open(target_dir / "index.html", "w") as fl:
        fl.write(htmlmin.minify(html))
    # ---------------
    previous_hashes = [sha512("orfik".encode()).hexdigest()]
    for q in get_questions():
        print("Question:", q)
        if q.image:
            ext = q.image.name.split(".")[-1]
            image_path = target_dir / f"{previous_hash}.{ext}"
            with open(image_path, "wb") as fl:
                with open(q.image, "rb") as im:
                    fl.write(im.read())
            q = Question(q.number, q.statement, Path(image_path).name, q.answers)
        tpl = env.get_template("question.html")
        html = htmlmin.minify(tpl.render(q=q, api_base=args.api_base))
        for previous_hash in previous_hashes:
            with open(target_dir / f"{previous_hash}.html", "w") as fl:
                fl.write(html)
        previous_hashes = [sha512(ans.encode()).hexdigest() for ans in q.answers]
    # ----------------
    tpl = env.get_template("end.html")
    html = htmlmin.minify(tpl.render(api_base=args.api_base))
    for previous_hash in previous_hashes:
        with open(target_dir / f"{previous_hash}.html", "w") as fl:
            fl.write(html)
    tpl = env.get_template("lb.html")
    html = htmlmin.minify(tpl.render(api_base=args.api_base))
    with open(target_dir / "lb.html", "w") as fl:
        fl.write(html)
