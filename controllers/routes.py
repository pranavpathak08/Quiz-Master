from flask import Blueprint, render_template, session

routes_blueprint = Blueprint("routes", __name__)

@routes_blueprint.route("/")
def home():
    return render_template("index.html")
