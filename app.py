from flask import Flask, render_template, request
import pickle
import PyPDF2
import os
import random

app = Flask(__name__)

# Load model
with open("models/resume_model.pkl", "rb") as f:
    model = pickle.load(f)

# Load vectorizer
with open("models/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)


# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# About page
@app.route("/about")
def about():
    return render_template("about.html")

#upload analyze page
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["resume"]

        if file:
            # Extract text
            resume_text = extract_text_from_pdf(file)

            # Transform text
            transformed_text = vectorizer.transform([resume_text])

            # Predict
            prediction = model.predict(transformed_text)[0]

            # Generate Score
            if prediction == "Strong":
                score = random.randint(80, 95)
            elif prediction == "Average":
                score = random.randint(60, 79)
            else:
                score = random.randint(30, 59)
            
            # Keyword-based explanation
            resume_lower = resume_text.lower()

            technical_keywords = ["python", "java", "sql", "machine learning", "data", "analysis"]
            experience_keywords = ["experience", "worked", "years", "company", "intern"]

            tech_found = any(word in resume_lower for word in technical_keywords)
            exp_found = any(word in resume_lower for word in experience_keywords)

            explanation_points = []

            if tech_found:
                explanation_points.append("Technical skills detected.")
            else:
                explanation_points.append("Consider adding more technical skills.")

            if exp_found:
                explanation_points.append("Work experience section identified.")
            else:
                explanation_points.append("Consider describing your work experience more clearly.")

            if len(resume_text.split()) < 150:
                explanation_points.append("Resume content appears brief. Consider expanding it.")

            message = " ".join(explanation_points)

            return render_template(
                "result.html",
                strength=prediction,
                message=message,
                score=score
            )
    return render_template("upload.html")



# Result page
@app.route("/result")
def result():
    return render_template("result.html")


if __name__ == "__main__":
    app.run(debug=True)
