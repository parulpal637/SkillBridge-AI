
import os
import json
import logging

from datetime import timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, create_tables


# =====================================
# 1. FLASK APPLICATION
# =====================================

app = Flask(__name__)

app.logger.setLevel(logging.INFO)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY environment variable is missing.")

# Session configuration
COOKIE_SECURE = os.environ.get(
    "COOKIE_SECURE", "true"
).lower() == "true"

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = COOKIE_SECURE
app.config["SESSION_COOKIE_SAMESITE"] = (
    "None" if COOKIE_SECURE else "Lax"
)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)


# =====================================
# 2. CORS CONFIGURATION
# =====================================

ALLOWED_ORIGINS = [
    "https://skillbridge-ai-oofk.netlify.app",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ALLOWED_ORIGINS
        }
    },
    supports_credentials=True
)


# =====================================
# 3. DATABASE INITIALIZATION
# =====================================

try:
    create_tables()
    app.logger.info("Database tables initialized successfully.")

except Exception:
    app.logger.exception("Database initialization failed.")
    raise


# =====================================
# 4. HELPER FUNCTIONS
# =====================================

def login_required():

    student_id = session.get("student_id")

    if not student_id:
        return None

    return student_id


def database_error_response(message):
    app.logger.exception(message)

    return jsonify({
        "error": message,
        "status": "error"
    }), 500


# =====================================
# 5. HOME API
# =====================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "SkillBridge AI Backend is running!",
        "status": "success"
    })


@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "success",
        "message": "Backend is healthy"
    }), 200


# =====================================
# 6. STUDENT REGISTRATION API
# =====================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "error": "All fields are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must contain at least 8 characters"
        }), 400

    if len(name) > 150 or len(email) > 254:
        return jsonify({
            "error": "Name or email is too long"
        }), 400

    conn = get_db_connection()

    try:

        cursor = conn.cursor()

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO students (name, email, password)
            VALUES (?, ?, ?)
        """, (
            name,
            email,
            hashed_password
        ))

        student_id = cursor.lastrowid

        conn.commit()

        # Automatically login after successful registration
        session.clear()

        session.permanent = True
        session["student_id"] = student_id

        return jsonify({
            "message": "Registration successful!",
            "status": "success",
            "student": {
                "id": student_id,
                "name": name,
                "email": email
            }
        }), 201

    except Exception as error:

        conn.rollback()

        if "UNIQUE constraint failed" in str(error):
            return jsonify({
                "error": "Email already registered. Please login."
            }), 409

        app.logger.exception("Registration failed")

        return jsonify({
            "error": "Registration failed"
        }), 500

    finally:
        conn.close()


# =====================================
# 7. STUDENT LOGIN API
# =====================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    conn = get_db_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email = ?",
            (email,)
        )

        student = cursor.fetchone()

    except Exception:
        app.logger.exception("Login database error")

        return jsonify({
            "error": "Login failed. Please try again."
        }), 500

    finally:
        conn.close()

    if not student or not check_password_hash(
        student["password"], password
    ):

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    # Create authenticated session
    session.clear()

    session.permanent = True
    session["student_id"] = student["id"]

    return jsonify({
        "message": "Login successful!",
        "status": "success",
        "student": {
            "id": student["id"],
            "name": student["name"],
            "email": student["email"]
        }
    }), 200


# =====================================
# 8. STUDENT ASSESSMENT API
# =====================================

@app.route("/api/assessment", methods=["POST"])
def save_assessment():

    student_id = login_required()

    if not student_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    data = request.get_json(silent=True) or {}

    preferred_domain = data.get(
        "preferredDomain", ""
    ).strip()

    if not preferred_domain:
        return jsonify({
            "error": "Please select a domain"
        }), 400

    conn = get_db_connection()

    try:

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

        return jsonify({
            "message": "Assessment saved successfully!",
            "status": "success"
        }), 201

    except Exception:
        conn.rollback()
        return database_error_response(
            "Assessment saving failed"
        )

    finally:
        conn.close()


# =====================================
# 9. STUDENT PROFILE API
# =====================================

@app.route("/api/profile", methods=["GET"])
def profile():

    student_id = login_required()

    if not student_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    conn = get_db_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, email, created_at
            FROM students
            WHERE id = ?
        """, (student_id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        cursor.execute("""
            SELECT *
            FROM assessments
            WHERE student_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (student_id,))

        assessment = cursor.fetchone()

        return jsonify({
            "student": dict(student),
            "assessment": (
                dict(assessment) if assessment else None
            )
        }), 200

    except Exception:
        return database_error_response(
            "Could not load student profile"
        )

    finally:
        conn.close()


# =====================================
# 10. SAVE SKILL ASSESSMENT API
# =====================================

@app.route("/api/skills", methods=["POST"])
def save_skills():

    student_id = login_required()

    if not student_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    data = request.get_json(silent=True) or {}

    results = data.get("results", [])

    if not isinstance(results, list) or not results:
        return jsonify({
            "error": "Skill results are required"
        }), 400

    allowed_levels = [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]

    for item in results:

        if (
            not isinstance(item, dict)
            or not isinstance(item.get("skill"), str)
            or not item.get("skill").strip()
            or item.get("level") not in allowed_levels
        ):

            return jsonify({
                "error": "Invalid skill data"
            }), 400

    conn = get_db_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM skill_results WHERE student_id = ?",
            (student_id,)
        )

        for item in results:

            cursor.execute("""
                INSERT INTO skill_results (
                    student_id,
                    skill_name,
                    skill_level
                )
                VALUES (?, ?, ?)
            """, (
                student_id,
                item["skill"].strip(),
                item["level"]
            ))

        conn.commit()

        return jsonify({
            "message": "Skills saved successfully!",
            "status": "success"
        }), 200

    except Exception:
        conn.rollback()

        return database_error_response(
            "Skills saving failed"
        )

    finally:
        conn.close()


# =====================================
# 11. GET SAVED SKILLS API
# =====================================

@app.route("/api/skills", methods=["GET"])
def get_skills():

    student_id = login_required()

    if not student_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    conn = get_db_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT skill_name, skill_level
            FROM skill_results
            WHERE student_id = ?
        """, (student_id,))

        rows = cursor.fetchall()

        return jsonify({
            "skills": [
                {
                    "skill": row["skill_name"],
                    "level": row["skill_level"]
                }
                for row in rows
            ]
        }), 200

    except Exception:
        return database_error_response(
            "Could not load saved skills"
        )

    finally:
        conn.close()


# =====================================
# 12. LOGOUT API
# =====================================

@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    response = jsonify({
        "message": "Logged out successfully!",
        "status": "success"
    })

    response.delete_cookie(
        "session",
        path="/",
        secure=COOKIE_SECURE,
        httponly=True,
        samesite="None" if COOKIE_SECURE else "Lax"
    )

    return response, 200


# =====================================
# 13. ERROR HANDLERS
# =====================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "error": "API endpoint not found",
        "status": "error"
    }), 404


@app.errorhandler(500)
def internal_error(error):

    app.logger.exception("Internal server error")

    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500


# =====================================
# 14. LOCAL DEVELOPMENT SERVER
# =====================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
