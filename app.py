import os
from flask import Flask

app = Flask(__name__)
COLOR = os.getenv("COLOR", "blue")
VERSION = os.getenv("VERSION", "1")

@app.route("/")
def home():
    bg = "#1e66f5" if COLOR == "blue" else "#2e9e4f"
    return f"""
    <html><body style="background:{bg};color:white;font-family:Arial;text-align:center;padding-top:80px">
    <h1>PBL-III Task 8: Blue-Green Deployment</h1>
    <h2>Live environment: {COLOR.upper()}</h2>
    <h3>Build version: {VERSION}</h3>
    </body></html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
