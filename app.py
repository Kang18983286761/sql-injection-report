import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "dev-key-2025"

# 🚨 漏洞：文件上传配置（不做类型检查）
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

    # 插入默认用户（使用 INSERT OR IGNORE 防止重复插入）
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES ('admin', 'admin123', 'admin@example.com', '13800138000')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES ('alice', 'alice2025', 'alice@example.com', '13900139001')")

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
    success = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        phone = request.form.get("phone")

        if not username or not password:
            error = "用户名和密码不能为空"
        else:
            try:
                conn = get_db()
                cursor = conn.cursor()

                # 🚨 漏洞：使用 f-string 字符串拼接 SQL（存在 SQL 注入）
                sql = f"INSERT INTO users (username, password, email, phone) VALUES ('{username}', '{password}', '{email}', '{phone}')"
                print(f"[DEBUG] 执行的 SQL: {sql}")

                cursor.execute(sql)
                conn.commit()
                conn.close()

                flash("注册成功，请登录")
                return redirect("/login")
            except sqlite3.IntegrityError:
                error = "用户名已存在"
            except Exception as e:
                error = f"注册失败: {str(e)}"

    return render_template("register.html", error=error)

# 搜索
@app.route("/search")
def search():
    username = session.get("username")
    if not username:
        return redirect("/login")

    keyword = request.args.get("keyword", "")
    results = []

    if keyword:
        conn = get_db()
        cursor = conn.cursor()

        # 🚨 漏洞：使用 f-string 字符串拼接 SQL（存在 SQL 注入）
        sql = f"SELECT * FROM users WHERE username LIKE '%{keyword}%' OR email LIKE '%{keyword}%'"
        print(f"[DEBUG] 执行的 SQL: {sql}")

        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        results = [dict(row) for row in rows]

    user_info = None
    if username in USERS:
        user_info = USERS[username]
        user_info["username"] = username

    return render_template("index.html", user_info=user_info, keyword=keyword, results=results)

# 上传头像
@app.route("/upload", methods=["GET", "POST"])
def upload():
    # 检查是否登录
    username = session.get("username")
    if not username:
        flash("请先登录")
        return redirect("/login")

    user_info = None
    if username in USERS:
        user_info = USERS[username]
        user_info["username"] = username

    error = None
    file_url = None

    if request.method == "POST":
        # 检查是否有文件
        if 'file' not in request.files:
            error = "没有选择文件"
        else:
            file = request.files['file']
            if file.filename == '':
                error = "没有选择文件"
            else:
                try:
                    # 🚨 漏洞：使用用户提供的原始文件名（存在路径遍历漏洞）
                    filename = file.filename
                    print(f"[DEBUG] 上传文件名: {filename}")

                    # 确保上传目录存在
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                    # 🚨 漏洞：直接使用原始文件名保存，不做任何检查
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    # 返回文件访问 URL
                    file_url = f"/static/uploads/{filename}"
                    flash(f"上传成功！文件路径: {file_url}")
                except Exception as e:
                    error = f"上传失败: {str(e)}"

    return render_template("upload.html", user_info=user_info, error=error, file_url=file_url)

if __name__ == "__main__":
    init_db()
    # 确保上传目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)