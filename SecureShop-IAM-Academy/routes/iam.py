from flask import Blueprint, session, redirect, url_for, render_template
from audit import log_event
import sqlite3
from flask import current_app, request


iam_bp = Blueprint("iam", __name__)


@iam_bp.route("/health")
def health():
    return {
        "application": "SecureShop IAM Academy",
        "status": "ok",
        "csrf_protection": "enabled",
    }


@iam_bp.route("/iam")
def iam_overview():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    return render_template("iam.html")

@iam_bp.route("/admin")
def admin_page():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        log_event(
            event="admin_access_denied",
            username=session.get("username"),
            result="failure",
            details="Användaren saknar administratörsbehörighet.",
        )

        return render_template("access_denied.html"), 403

    return render_template("admin.html")



@iam_bp.route("/account")
def account_page():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    return render_template("account.html")


@iam_bp.route("/admin/audit-logs")
def audit_logs():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        log_event(
            event="audit_logs_access_denied",
            username=session.get("username"),
            result="failure",
            details="Försök att öppna auditloggen utan adminbehörighet.",
        )
        return render_template("access_denied.html"), 403

    selected_event = request.args.get("event", "")
    allowed_events = {
        "",
        "login_success",
        "login_failed",
        "logout",
        "admin_access_denied",
        "audit_logs_access_denied",
    }

    if selected_event not in allowed_events:
        selected_event = ""

    with sqlite3.connect(current_app.config["DATABASE_PATH"]) as conn:
        conn.row_factory = sqlite3.Row

        if selected_event:
            rows = conn.execute(
                """
                SELECT id, timestamp, event, username, result, details
                FROM audit_logs
                WHERE event = ?
                ORDER BY id DESC
                LIMIT 200
                """,
                (selected_event,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, timestamp, event, username, result, details
                FROM audit_logs
                ORDER BY id DESC
                LIMIT 200
                """
            ).fetchall()

    return render_template(
        "audit_logs.html",
        logs=rows,
        selected_event=selected_event,
    )

