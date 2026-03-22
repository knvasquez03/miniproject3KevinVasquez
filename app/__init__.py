# INF601 - Advanced Programming in Python

# Kevin Vasquez

# Mini Project 3

import os
from flask import Flask, render_template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "tasktracker.sqlite"),
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    from . import tasks

    app.register_blueprint(auth.bp)
    app.register_blueprint(tasks.bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app