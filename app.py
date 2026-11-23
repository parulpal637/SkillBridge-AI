
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, create_tables
import json

app = Flask(__name__)

app.config["SECRET_KEY"] = "skillbridge-ai-local-development-key"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

CORS(app, supports_credentials=True, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500"
])


# =====================================
# 1. HOME API
# =====================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "SkillBridge AI Backend is running!",
        "status": "success"
    })


# =====================================
# 2. STUDENT REGISTRATION API
# =====================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must contain at least 8 characters"}), 400

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO students (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, hashed_password))

        conn.commit()

        return jsonify({
            "message": "Registration successful!",
            "status": "success"
        }), 201

    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            return jsonify({"error": "Email already registered"}), 409

        return jsonify({"error": "Registration failed"}), 500

    finally:
        conn.close()


# =====================================
# 3. STUDENT LOGIN API
# =====================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE email = ?",
        (email,)
    )

    student = cursor.fetchone()
    conn.close()

    if not student or not check_password_hash(
        student["password"], password
    ):
        return jsonify({"error": "Invalid email or password"}), 401

    session.clear()
    session["student_id"] = student["id"]

    return jsonify({
        "message": "Login successful!",
        "status": "success",
        "student": {
            "id": student["id"],
            "name": student["name"],
            "email": student["email"]
        }
    })


# =====================================
# 4. STUDENT ASSESSMENT API
# =====================================

@app.route("/api/assessment", methods=["POST"])
def save_assessment():

    student_id = session.get("student_id")

    if not student_id:
        return jsonify({"error": "Please login first"}), 401

    data = request.get_json(silent=True) or {}

    preferred_domain = data.get("preferredDomain", "").strip()

    if not preferred_domain:
        return jsonify({"error": "Please select a domain"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO assessments (
            student_id,
            college,
            know_domain,
            domain_explanation,
            know_types,
            known_domains,
            video_answer,
            preferred_domain
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        data.get("college", ""),
        data.get("knowDomain", ""),
        data.get("domainExplanation", ""),
        data.get("knowTypes", ""),
        json.dumps(data.get("knownDomains", [])),
        data.get("videoAnswer", ""),
        preferred_domain
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Assessment saved successfully!",
        "status": "success"
    }), 201


# =====================================
# 5. STUDENT PROFILE API
# =====================================

@app.route("/api/profile", methods=["GET"])
def profile():

    student_id = session.get("student_id")

    if not student_id:
        return jsonify({"error": "Please login first"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, created_at
        FROM students
        WHERE id = ?
    """, (student_id,))

    student = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM assessments
        WHERE student_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,))

    assessment = cursor.fetchone()
    conn.close()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "student": dict(student),
        "assessment": dict(assessment) if assessment else None
    })


# =====================================
# 6. SAVE SKILL ASSESSMENT API
# =====================================

@app.route("/api/skills", methods=["POST"])
def save_skills():

    student_id = session.get("student_id")

    if not student_id:
        return jsonify({"error": "Please login first"}), 401

    data = request.get_json(silent=True) or {}
    results = data.get("results", [])

    if not isinstance(results, list) or not results:
        return jsonify({"error": "Skill results are required"}), 400

    allowed_levels = ["Beginner", "Intermediate", "Advanced"]

    for item in results:
        if (
            not isinstance(item, dict)
            or not item.get("skill")
            or item.get("level") not in allowed_levels
        ):
            return jsonify({"error": "Invalid skill data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM skill_results WHERE student_id = ?",
        (student_id,)
    )

    for item in results:
        cursor.execute("""
            INSERT INTO skill_results (
                student_id, skill_name, skill_level
            )
            VALUES (?, ?, ?)
        """, (
            student_id,
            item["skill"],
            item["level"]
        ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Skills saved successfully!",
        "status": "success"
    })


# =====================================
# 7. GET SAVED SKILLS API
# =====================================

@app.route("/api/skills", methods=["GET"])
def get_skills():

    student_id = session.get("student_id")

    if not student_id:
        return jsonify({"error": "Please login first"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skill_name, skill_level
        FROM skill_results
        WHERE student_id = ?
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify({
        "skills": [
            {
                "skill": row["skill_name"],
                "level": row["skill_level"]
            }
            for row in rows
        ]
    })


# =====================================
# 8. LOGOUT API
# =====================================

@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "message": "Logged out successfully!"
    })


# =====================================
# START SERVER
# =====================================

if __name__ == "__main__":
    create_tables()
    app.run(debug=True, port=5000)
