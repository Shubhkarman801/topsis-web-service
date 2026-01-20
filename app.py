import os
import re
import smtplib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request
from email.message import EmailMessage
import uuid

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def run_topsis(input_file, weights_str, impacts_str, output_file):
    df = pd.read_csv(input_file)

    if df.shape[1] < 3:
        raise Exception("CSV must have at least 3 columns")

    data = df.iloc[:, 1:].astype(float)

    weights = np.array(list(map(float, weights_str.split(","))))
    weights = weights / weights.sum()

    impacts = impacts_str.split(",")

    if len(weights) != len(impacts) or len(weights) != data.shape[1]:
        raise Exception("Weights, impacts, and columns must match")

    for i in impacts:
        if i not in ["+", "-"]:
            raise Exception("Impacts must be + or -")

    norm = data / np.sqrt((data ** 2).sum())
    weighted = norm * weights

    ideal_best = []
    ideal_worst = []

    for i, col in enumerate(weighted.columns):
        if impacts[i] == "+":
            ideal_best.append(weighted[col].max())
            ideal_worst.append(weighted[col].min())
        else:
            ideal_best.append(weighted[col].min())
            ideal_worst.append(weighted[col].max())

    dist_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))

    score = dist_worst / (dist_best + dist_worst)

    df["Topsis Score"] = score
    df["Rank"] = df["Topsis Score"].rank(ascending=False, method="max").astype(int)

    df.to_csv(output_file, index=False)

def send_email(receiver, attachment_path):
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    if not sender or not password:
        raise Exception("Email credentials not set")

    msg = EmailMessage()
    msg["Subject"] = "TOPSIS Result"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content("Your TOPSIS result file is attached.")

    with open(attachment_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename="result.csv"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

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
