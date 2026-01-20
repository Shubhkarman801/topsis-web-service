import os
import re
import smtplib
import pandas as pd
import numpy as np
from topsis_shubhkarman_102303661 import topsis_core
from flask import Flask, render_template, request
from email.message import EmailMessage
import uuid
import requests

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def run_topsis(input_file, weights_str, impacts_str, output_file):
    topsis_core(input_file, weights_str, impacts_str, output_file)

def send_email(receiver, attachment_path):
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise Exception("RESEND_API_KEY not set")

    with open(attachment_path, "rb") as f:
        file_bytes = f.read()

    files = {
        "file": ("result.csv", file_bytes)
    }

    data = {
        "from": "TOPSIS <onboarding@resend.dev>",
        "to": receiver,
        "subject": "Your TOPSIS Result",
        "html": "<p>Your TOPSIS result file is attached.</p>"
    }

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.post(
        "https://api.resend.com/emails",
        headers=headers,
        data=data,
        files=files
    )

    if response.status_code not in [200, 201]:
        raise Exception(f"Email failed: {response.text}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        weights = request.form["weights"]
        impacts = request.form["impacts"]
        email = request.form["email"]

        if not file or not file.filename.endswith(".csv"):
            return "Please upload a valid CSV file"

        if not re.match(EMAIL_REGEX, email):
            return "Invalid email format"

        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(RESULT_FOLDER, f"result_{uuid.uuid4().hex}.csv")

        file.save(input_path)

        try:
            run_topsis(input_path, weights, impacts, output_path)
            send_email(email, output_path)
        except Exception as e:
            return f"Error: {str(e)}"

        return "Success! Result has been emailed to you."

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
