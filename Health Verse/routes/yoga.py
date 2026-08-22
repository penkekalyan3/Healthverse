from flask import render_template

def yoga_view():
    """Renders the Yoga routine planner."""
    return render_template("yoga.html")
