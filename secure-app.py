import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, flash, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-key-2025'

# 用户数据库（明文存储密码）
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "email": "admin@example.com",
        "phone": "13800138000",
        "balance": 99999
    },
    "alice": {
        "password": "alice2025",
        "role": "user",
        "email": "alice@example.com",
        "phone": "13900139001",
        "balance": 100
    }
}

# 数据库路径
DB_PATH = "data/users.db"

# 初始化数据库
def init_db():
    # 确保 data 目录存在
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建 users 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            phone TEXT
        )
    ''')

    # ✅ 修复：使用参数化查询插入默认用户
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
        ('admin', 'admin123', 'admin@example.com', '13800138000')
    )
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
        ('alice', 'alice2025', 'alice@example.com', '13900139001')
    )

    conn.commit()
    conn.close()

# 获取数据库连接
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 首页
@app.route("/")
def index():
    username = session.get("username")
    user_info = None
    if username and username in USERS:
        user_info = USERS[username]
        user_info["username"] = username
    return render_template("index.html", user_info=user_info)

# 登录
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in USERS and USERS[username]["password"] == password:
            session["username"] = username
            user_info = USERS[username]
            user_info["username"] = username
            return render_template("index.html", user_info=user_info)
        else:
            error = "用户名或密码错误"

    return render_template("login.html", error=error)

# 登出
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# 注册
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        # ✅ 修复：输入验证
        if not username or not password:
            error = "用户名和密码不能为空"
        elif len(username) < 3 or len(username) > 50:
            error = "用户名长度需在3-50个字符之间"
        elif len(password) < 6:
            error = "密码长度至少6个字符"
        else:
            try:
                conn = get_db()
                cursor = conn.cursor()

                # ✅ 修复：使用参数化查询防止SQL注入
                cursor.execute(
                    "INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
                    (username, password, email, phone)
                )
                conn.commit()
                conn.close()

                flash("注册成功，请登录")
                return redirect("/login")
            except sqlite3.IntegrityError:
                error = "用户名已存在"
            except Exception as e:
                error = "注册失败，请稍后重试"
                # 生产环境不应打印详细错误

    return render_template("register.html", error=error)

# 搜索
@app.route("/search")
def search():
    username = session.get("username")
    if not username:
        return redirect("/login")

    keyword = request.args.get("keyword", "").strip()
    results = []

    if keyword:
        # ✅ 修复：限制搜索关键词长度
        if len(keyword) > 100:
            flash("搜索关键词过长")
            return redirect("/")

        conn = get_db()
        cursor = conn.cursor()

        # ✅ 修复：使用参数化查询防止SQL注入
        # 注意：LIKE的通配符需要在参数中设置，不能在SQL中拼接
        search_pattern = f"%{keyword}%"
        cursor.execute(
            "SELECT * FROM users WHERE username LIKE ? OR email LIKE ?",
            (search_pattern, search_pattern)
        )
        rows = cursor.fetchall()
        conn.close()

        results = [dict(row) for row in rows]

    user_info = None
    if username in USERS:
        user_info = USERS[username]
        user_info["username"] = username

    return render_template("index.html", user_info=user_info, keyword=keyword, results=results)

if __name__ == "__main__":
    init_db()
    # 生产环境应关闭 debug=True
    app.run(debug=True, host="127.0.0.1", port=5000)