from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "civiclens.db"))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS leaders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            office TEXT NOT NULL,
            county TEXT NOT NULL,
            party TEXT NOT NULL,
            performance REAL NOT NULL,
            activity REAL NOT NULL,
            promise REAL NOT NULL,
            budget REAL NOT NULL,
            evidence REAL NOT NULL
        )
    """)

    count = conn.execute("SELECT COUNT(*) FROM leaders").fetchone()[0]

    if count == 0:
        demo_leaders = [
            ("Sample Leader A", "National Office", "Kenya", "Party A", 72, 81, 68, 74, 92),
            ("Sample Leader B", "County Office", "Example County", "Party B", 65, 76, 61, 79, 88),
            ("Sample Leader C", "Parliament", "Example County", "Independent", 80, 69, 73, 71, 95),
            ("Sample Leader D", "National Office", "Kenya", "Party C", 77, 84, 70, 68, 90),
            ("Sample Leader E", "County Office", "Example County", "Independent", 71, 73, 75, 82, 86)
        ]

        conn.executemany("""
            INSERT INTO leaders
            (name, office, county, party, performance, activity, promise, budget, evidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_leaders)

    conn.commit()
    conn.close()


def prepare_leader(row):
    leader = dict(row)

    scores = [
        leader["performance"],
        leader["activity"],
        leader["promise"],
        leader["budget"],
        leader["evidence"]
    ]

    leader["overall"] = round(sum(scores) / len(scores), 1)

    return leader


initialize_database()


@app.route("/")
def home():
    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM leaders
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    leaders = [prepare_leader(row) for row in rows]

    score = 0

    if leaders:
        score = round(
            sum(leader["overall"] for leader in leaders) / len(leaders),
            1
        )

    return render_template(
        "index.html",
        leaders=leaders,
        score=score,
        average_score=score
    )


@app.route("/leaders")
def leaders_page():
    search = request.args.get("search", "").strip()

    conn = get_db()

    if search:
        rows = conn.execute("""
            SELECT *
            FROM leaders
            WHERE name LIKE ?
               OR office LIKE ?
               OR county LIKE ?
               OR party LIKE ?
            ORDER BY name
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        )).fetchall()
    else:
        rows = conn.execute("""
            SELECT *
            FROM leaders
            ORDER BY name
        """).fetchall()

    conn.close()

    leaders = []

    for row in rows:
        leader = dict(row)

        scores = [
            float(leader.get("performance", 0)),
            float(leader.get("activity", 0)),
            float(leader.get("promise", 0)),
            float(leader.get("budget", 0)),
            float(leader.get("evidence", 0))
        ]

        leader["overall"] = round(sum(scores) / 5, 1)

        # Compatibility with older templates
        leader["overall_score"] = leader["overall"]

        leaders.append(leader)

    return render_template(
        "leaders.html",
        leaders=leaders,
        search=search,
        score=0
    )

@app.route("/leader/<int:leader_id>")
def leader_page(leader_id):
    conn = get_db()

    row = conn.execute("""
        SELECT *
        FROM leaders
        WHERE id = ?
    """, (leader_id,)).fetchone()

    conn.close()

    if row is None:
        return "Leader not found", 404

    leader = prepare_leader(row)

    return render_template(
        "leader.html",
        leader=leader,
        score=leader["overall"]
    )


@app.route("/compare")
def compare():
    ids = request.args.getlist("id")

    conn = get_db()

    leaders = []

    for leader_id in ids[:2]:
        try:
            leader_id = int(leader_id)
        except ValueError:
            continue

        row = conn.execute("""
            SELECT *
            FROM leaders
            WHERE id = ?
        """, (leader_id,)).fetchone()

        if row:
            leaders.append(prepare_leader(row))

    conn.close()

    return render_template(
        "compare.html",
        leaders=leaders
    )


@app.route("/api/leaders")
def api_leaders():
    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM leaders
        ORDER BY name
    """).fetchall()

    conn.close()

    leaders = [prepare_leader(row) for row in rows]

    return jsonify({
        "success": True,
        "count": len(leaders),
        "leaders": leaders
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "database": os.path.exists(DB_PATH)
    })


@app.route("/refresh")
def refresh():
    initialize_database()

    return jsonify({
        "success": True,
        "message": "Database checked and initialized."
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)