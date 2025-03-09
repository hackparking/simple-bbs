from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
DATABASE = "database.db"

# データベース接続
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# データベースの初期化
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                content TEXT NOT NULL,
                FOREIGN KEY (thread_id) REFERENCES threads (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                reason TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        """)
        db.commit()

# トップページ（スレッド一覧）
@app.route("/")
def index():
    db = get_db()
    threads = db.execute("SELECT id, title FROM threads").fetchall()
    return render_template("index.html", threads=threads)

# スレッド作成
@app.route("/create_thread", methods=["POST"])
def create_thread():
    title = request.form["title"]
    db = get_db()
    db.execute("INSERT INTO threads (title) VALUES (?)", (title,))
    db.commit()
    return redirect(url_for("index"))

# スレッド詳細ページ
@app.route("/thread/<int:thread_id>")
def thread(thread_id):
    db = get_db()
    thread = db.execute("SELECT id, title FROM threads WHERE id=?", (thread_id,)).fetchone()
    posts = db.execute("SELECT id, content FROM posts WHERE thread_id=?", (thread_id,)).fetchall()
    return render_template("thread.html", thread=thread, posts=posts)

# 投稿を追加
@app.route("/add_post/<int:thread_id>", methods=["POST"])
def add_post(thread_id):
    content = request.form["content"]
    db = get_db()
    db.execute("INSERT INTO posts (thread_id, content) VALUES (?, ?)", (thread_id, content))
    db.commit()
    return redirect(url_for("thread", thread_id=thread_id))

# 通報機能
@app.route("/report/<int:post_id>", methods=["POST"])
def report(post_id):
    reason = request.form["reason"]
    db = get_db()
    db.execute("INSERT INTO reports (post_id, reason) VALUES (?, ?)", (post_id, reason))
    db.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
