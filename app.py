from flask import Flask, render_template, request, send_file
import base64
import io
import pdfkit
from utils import normalize_data, validate, score_resume, render_resume

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    raw = request.form.to_dict(flat=False)
    clean = {k.replace("[]",""):v for k,v in raw.items()}

    section_order = {
        "summary": int(request.form.get("order_summary",1)),
        "skills": int(request.form.get("order_skills",2)),
        "education": int(request.form.get("order_education",3)),
        "experience": int(request.form.get("order_experience",4)),
        "certificates": int(request.form.get("order_certificates",5))
    }

    clean["section_order"] = [s for s,_ in sorted(section_order.items(), key=lambda x:x[1])]
    clean["template"] = request.form.get("template_choice","classic")

    photo = request.files.get("photo")
    if photo and photo.filename:
        clean["photo_base64"] = base64.b64encode(photo.read()).decode("utf-8")
    else:
        clean["photo_base64"] = ""

    data = normalize_data(clean)
    errors = validate(data)
    resume_score = score_resume(data)
    resume_html = render_resume(data)

    return render_template(
        "preview.html",
        resume_html=resume_html,
        score=resume_score,
        errors=errors
    )

@app.route("/download/pdf", methods=["POST"])
def download_pdf():
    html = request.form.get("resume_html")
    pdf = pdfkit.from_string(html, False)
    return send_file(
        io.BytesIO(pdf),
        download_name="resume.pdf",
        as_attachment=True
    )

if __name__ == "__main__":
    app.run()

