from flask import Flask, render_template, request, make_response
from emotion_model import detect_emotion
from datetime import datetime
import csv
import os 
import re

app = Flask(__name__)

# Clean mood (remove emoji)
def clean_mood(mood):
    return re.sub(r'[^\w\s]', '', mood).strip()

# Save to CSV (correct path)
def save_mood_entry(text, mood):
    mood = clean_mood(mood)
    file_path = os.path.join(app.root_path, 'mood_log.csv')
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mood, text])
    print(f"[SAVED] {mood} -> {text}")

# Mood + color message
def get_motivation_and_color(mood):
    if "Very Happy" in mood:
        return ("#a8ff78", "Keep shining! 😎")
    elif "Happy" in mood:
        return ("#d4fc79", "Smile more today! 😊")
    elif "Neutral" in mood:
        return ("#fefcea", "Stay steady. ✌️")
    elif "Sad" in mood:
        return ("#fbc2eb", "Better days are coming. 🌈")
    else:
        return ("#f5576c", "It's okay to feel low. ❤️")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        text = request.form.get("journal", "").strip()
        if not text:
            error = "Please enter your journal entry."
            return render_template("index.html", error=error)
        mood = detect_emotion(text)
        color, message = get_motivation_and_color(mood)
        save_mood_entry(text, mood)
        return render_template("result.html", mood=mood, text=text, color=color, message=message)
    return render_template("index.html")

@app.route("/history")
def history():
    dates, moods = [], []
    file_path = os.path.join(app.root_path, 'mood_log.csv')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    dates.append(row[0].strip())
                    moods.append(row[1].strip())
    except Exception as e:
        print("Error reading:", e)

    response = make_response(render_template("history.html", dates=dates, moods=moods))
    response.headers["Cache-Control"] = "no-store"
    return response

if __name__ == "__main__":
    app.run(debug=True)
