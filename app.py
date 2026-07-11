"""
TravelPlannerAI — Flask Application
IBM watsonx Orchestrate powered travel planning
"""

import os
import json
import io
from datetime import datetime, date
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, send_file, flash
)
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
CORS(app)

# ── Lazy import so the app starts even without the SDK ─────────────────────
import watsonx_ai as wx


# ════════════════════════════════════════════════════════════
#  Auth routes  (demo: no real DB — just session-based)
# ════════════════════════════════════════════════════════════

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        # Demo auth — accept any non-empty credentials
        if email and password:
            session["user"] = {"email": email, "name": email.split("@")[0].title()}
            flash("Welcome back! Your AI travel planner is ready.", "success")
            return redirect(url_for("index"))
        flash("Invalid credentials. Please try again.", "danger")
    return render_template("auth.html", mode="login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if name and email and password:
            session["user"] = {"email": email, "name": name}
            flash("Account created! Welcome to TravelPlannerAI.", "success")
            return redirect(url_for("index"))
        flash("Please fill in all fields.", "danger")
    return render_template("auth.html", mode="signup")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ════════════════════════════════════════════════════════════
#  Page routes
# ════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))


@app.route("/plan")
def plan():
    return render_template("plan.html", user=session.get("user"))


@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html", user=session.get("user"))


@app.route("/about")
def about():
    return render_template("about.html", user=session.get("user"))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thanks for reaching out! We'll respond within 24 hours.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", user=session.get("user"))


@app.route("/itinerary")
def itinerary():
    itinerary_data = session.get("itinerary_data")
    trip_data      = session.get("trip_data")
    if not itinerary_data:
        flash("Please generate an itinerary first.", "warning")
        return redirect(url_for("plan"))
    return render_template(
        "itinerary.html",
        user=session.get("user"),
        itinerary=itinerary_data,
        trip=trip_data,
    )


# ════════════════════════════════════════════════════════════
#  API endpoints
# ════════════════════════════════════════════════════════════

@app.route("/api/generate-itinerary", methods=["POST"])
def api_generate_itinerary():
    try:
        data = request.get_json(force=True)
        required = ["destination", "start_date", "end_date"]
        for field in required:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Normalise
        trip_data = {
            "destination":          data.get("destination"),
            "start_date":           data.get("start_date"),
            "end_date":             data.get("end_date"),
            "budget":               data.get("budget", "medium"),
            "travelers":            int(data.get("travelers", 2)),
            "preferences":          data.get("preferences", []),
            "special_requirements": data.get("special_requirements", ""),
        }

        itinerary_result = wx.generate_itinerary(trip_data)

        # Persist in session for itinerary page + PDF
        session["itinerary_data"] = itinerary_result
        session["trip_data"]      = trip_data

        return jsonify({"success": True, "itinerary": itinerary_result})

    except Exception as exc:
        app.logger.error(f"Itinerary generation error: {exc}")
        return jsonify({"error": "Failed to generate itinerary. Please try again."}), 500


@app.route("/api/destination-info", methods=["POST"])
def api_destination_info():
    try:
        data        = request.get_json(force=True)
        destination = data.get("destination", "").strip()
        if not destination:
            return jsonify({"error": "Destination is required"}), 400
        info = wx.get_destination_info(destination)
        return jsonify({"success": True, "info": info})
    except Exception as exc:
        app.logger.error(f"Destination info error: {exc}")
        return jsonify({"error": "Could not fetch destination info"}), 500


@app.route("/api/download-pdf", methods=["POST"])
def api_download_pdf():
    """Generate and return a PDF of the itinerary."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable
        )

        data          = request.get_json(force=True)
        itinerary     = data.get("itinerary", session.get("itinerary_data", {}))
        trip          = data.get("trip",      session.get("trip_data", {}))
        destination   = itinerary.get("destination", "Travel Itinerary")

        buffer = io.BytesIO()
        doc    = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm,   bottomMargin=2*cm,
        )

        styles  = getSampleStyleSheet()
        primary = colors.HexColor("#1e3a5f")
        accent  = colors.HexColor("#f39c12")

        title_style = ParagraphStyle("Title", parent=styles["Heading1"],
                                     textColor=primary, fontSize=24, spaceAfter=6)
        h2_style    = ParagraphStyle("H2", parent=styles["Heading2"],
                                     textColor=primary, fontSize=14, spaceAfter=4)
        h3_style    = ParagraphStyle("H3", parent=styles["Heading3"],
                                     textColor=accent, fontSize=12, spaceAfter=3)
        body_style  = ParagraphStyle("Body", parent=styles["Normal"],
                                     fontSize=10, spaceAfter=3, leading=14)
        bullet_style= ParagraphStyle("Bullet", parent=styles["Normal"],
                                     fontSize=10, leftIndent=15, spaceAfter=2)

        story = []

        # Title
        story.append(Paragraph(f"✈ {destination}", title_style))
        story.append(Paragraph(
            f"Travel Itinerary | {trip.get('start_date','')} → {trip.get('end_date','')} | "
            f"{trip.get('travelers', 2)} traveler(s) | Budget: {trip.get('budget','').title()}",
            body_style
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=primary))
        story.append(Spacer(1, 0.3*cm))

        # Overview
        story.append(Paragraph("Destination Overview", h2_style))
        story.append(Paragraph(itinerary.get("overview", ""), body_style))
        story.append(Spacer(1, 0.2*cm))

        info_table_data = [
            ["Best Time to Visit", itinerary.get("best_time_to_visit", "")],
            ["Currency",           itinerary.get("currency", "")],
            ["Language",           itinerary.get("language", "")],
        ]
        info_table = Table(info_table_data, colWidths=[4*cm, 13*cm])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), primary),
            ("TEXTCOLOR",  (0, 0), (0, -1), colors.white),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("PADDING",    (0, 0), (-1, -1), 6),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.4*cm))

        # Day-by-day itinerary
        story.append(Paragraph("Day-by-Day Itinerary", h2_style))
        for day in itinerary.get("days", []):
            story.append(Paragraph(
                f"Day {day.get('day')} — {day.get('theme', '')}  ({day.get('date', '')})",
                h3_style
            ))
            for slot in ("morning", "afternoon", "evening"):
                slot_data = day.get(slot, {})
                if slot_data:
                    story.append(Paragraph(
                        f"<b>{slot.title()}:</b> {slot_data.get('activity','')} "
                        f"({slot_data.get('duration','')}, {slot_data.get('cost','')})",
                        body_style
                    ))
                    story.append(Paragraph(slot_data.get("description", ""), bullet_style))
            meals = day.get("meals", {})
            if meals:
                meal_txt = " | ".join(f"{k.title()}: {v}" for k, v in meals.items())
                story.append(Paragraph(f"<b>Meals:</b> {meal_txt}", body_style))
            if day.get("tips"):
                story.append(Paragraph(f"<b>💡 Tip:</b> {day['tips']}", bullet_style))
            story.append(Spacer(1, 0.3*cm))

        # Budget
        story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
        story.append(Paragraph("Budget Breakdown", h2_style))
        budget = itinerary.get("budget_breakdown", {})
        for k, v in budget.items():
            story.append(Paragraph(
                f"<b>{k.replace('_', ' ').title()}:</b> {v}", body_style
            ))

        story.append(Spacer(1, 0.3*cm))

        # Safety Tips
        story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
        story.append(Paragraph("Safety Tips", h2_style))
        for tip in itinerary.get("safety_tips", []):
            story.append(Paragraph(f"• {tip}", bullet_style))

        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(
            f"Generated by TravelPlannerAI powered by IBM watsonx Orchestrate — {datetime.now().strftime('%B %d, %Y')}",
            ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
        ))

        doc.build(story)
        buffer.seek(0)

        filename = f"itinerary_{destination.replace(' ', '_').replace(',', '')}.pdf"
        return send_file(
            buffer, as_attachment=True,
            download_name=filename, mimetype="application/pdf"
        )

    except ImportError:
        return jsonify({"error": "PDF generation requires reportlab. Run: pip install reportlab"}), 500
    except Exception as exc:
        app.logger.error(f"PDF error: {exc}")
        return jsonify({"error": "PDF generation failed"}), 500


# ════════════════════════════════════════════════════════════
#  Error handlers
# ════════════════════════════════════════════════════════════

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", user=session.get("user")), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", user=session.get("user")), 500


# ════════════════════════════════════════════════════════════
#  Template context processor — make `now` available everywhere
# ════════════════════════════════════════════════════════════

@app.context_processor
def inject_globals():
    return {
        "now":      datetime.utcnow(),
        "app_name": os.getenv("APP_NAME", "TravelPlannerAI"),
    }


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000)
