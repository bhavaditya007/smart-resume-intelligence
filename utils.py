from jinja2 import Environment, FileSystemLoader
import re

TEMPLATE_MAP = {
    "classic": "resume_classic.html",
    "modern": "resume_modern.html",
    "twocol": "resume_twocol.html",
    "minimal": "resume_minimal.html",
    "creative": "resume_creative.html"
}

ACTION_VERBS = [
    "led","built","designed","developed","implemented","managed",
    "analyzed","improved","optimized","created","executed","automated"
]

def first(val):
    if isinstance(val, list):
        return val[0] if val else ""
    return val if val else ""

def normalize_data(raw):
    data = {}

    data["full_name"] = first(raw.get("full_name")).strip()
    data["email"] = first(raw.get("email")).strip()
    data["phone"] = first(raw.get("phone")).strip()
    data["location"] = first(raw.get("location")).strip()
    data["summary"] = first(raw.get("summary")).strip()

    data["skills"] = [s.strip() for s in raw.get("skills",[]) if s.strip()]

    data["education"] = []
    for i in range(len(raw.get("education_degree",[]))):
        data["education"].append({
            "degree": raw["education_degree"][i].strip(),
            "institution": raw["education_institution"][i].strip(),
            "year": raw["education_year"][i],
            "cgpa": raw["education_cgpa"][i]
        })

    data["experience"] = []
    for i in range(len(raw.get("experience_role",[]))):
        data["experience"].append({
            "role": raw["experience_role"][i].strip(),
            "company": raw["experience_company"][i].strip(),
            "duration": raw["experience_duration"][i].strip(),
            "desc": raw["experience_desc"][i].strip()
        })

    data["certificates"] = [c.strip() for c in raw.get("certificates",[]) if c.strip()]
    data["theme"] = first(raw.get("theme","blue"))
    data["template"] = first(raw.get("template","classic"))
    data["photo_base64"] = raw.get("photo_base64","")
    data["section_order"] = raw["section_order"]

    return data

def validate(data):
    errors = []
    if not data["full_name"]:
        errors.append("Name missing")
    if not data["email"]:
        errors.append("Email missing")
    if len(data["skills"]) < 3:
        errors.append("Too few skills")
    if not data["experience"]:
        errors.append("No experience added")
    return errors

def score_resume(data):
    score = 0

    if data["summary"]:
        score += 10

    score += min(len(data["skills"]) * 2, 20)

    exp_score = 0
    for e in data["experience"]:
        if any(v in e["desc"].lower() for v in ACTION_VERBS):
            exp_score += 10
        if re.search(r"\d", e["desc"]):
            exp_score += 5
    score += min(exp_score, 30)

    if data["education"]:
        score += 10

    if data["certificates"]:
        score += 10

    return min(score, 100)

def render_resume(data):
    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)
    template_file = TEMPLATE_MAP.get(data["template"], "resume_classic.html")
    template = env.get_template(template_file)
    return template.render(data=data)
