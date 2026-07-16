import sqlite3
import os
import subprocess
import platform
import urllib.request
import urllib.error
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

# 用户ID映射（用于IDOR漏洞演示）
USER_ID_MAP = {
    1: "admin",
    2: "alice"
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

# 个人中心
@app.route("/profile")
def profile():
    # 🚨 漏洞：从 URL 参数获取 user_id，不验证权限（IDOR 漏洞）
    user_id = request.args.get("user_id", type=int)

    if not user_id:
        flash("用户ID不能为空")
        return redirect("/")

    # 🚨 漏洞：不验证当前登录用户是否有权查看该用户资料
    # 任何人都可以通过修改 URL 参数查看其他用户的资料
    profile_user = None

    if user_id in USER_ID_MAP:
        username = USER_ID_MAP[user_id]
        if username in USERS:
            user_data = USERS[username]
            profile_user = {
                "id": user_id,
                "username": username,
                "email": user_data["email"],
                "phone": user_data["phone"],
                "balance": user_data["balance"],
                "role": user_data["role"]
            }

    # 获取当前登录用户信息
    current_username = session.get("username")
    user_info = None
    if current_username in USERS:
        user_info = USERS[current_username]
        user_info["username"] = current_username

    return render_template("profile.html", user_info=user_info, profile_user=profile_user)

# 充值
@app.route("/recharge", methods=["POST"])
def recharge():
    # 🚨 漏洞：从表单获取 user_id 和 amount，不验证权限
    user_id = request.form.get("user_id", type=int)
    amount = request.form.get("amount", type=float)

    print(f"[DEBUG] 充值请求 - user_id: {user_id}, amount: {amount}")

    if not user_id or amount is None:
        flash("参数错误")
        return redirect("/")

    # 🚨 漏洞：不验证 amount 是否为负数（可能导致余额减少）
    # 攻击者可以通过提交负数金额来减少其他用户的余额

    if user_id in USER_ID_MAP:
        username = USER_ID_MAP[user_id]
        if username in USERS:
            # 🚨 漏洞：直接修改余额，不做任何校验
            old_balance = USERS[username]["balance"]
            new_balance = old_balance + amount
            USERS[username]["balance"] = new_balance

            print(f"[DEBUG] 余额更新 - 用户: {username}, 原余额: {old_balance}, 变动: {amount}, 新余额: {new_balance}")

            if amount >= 0:
                flash(f"充值成功！余额增加 {amount}，当前余额：{new_balance}")
            else:
                flash(f"操作成功！余额变动 {amount}，当前余额：{new_balance}")

    return redirect(f"/profile?user_id={user_id}")

# 修改密码
@app.route("/change-password", methods=["POST"])
def change_password():
    # 🚨 漏洞：不验证 CSRF Token
    # 🚨 漏洞：不验证请求来源（Referer）
    
    # 检查是否登录（只要登录即可修改任何人的密码）
    current_user = session.get("username")
    if not current_user:
        flash("请先登录")
        return redirect("/login")

    # 🚨 漏洞：从表单获取 username，不验证是否为当前用户
    username = request.form.get("username")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    print(f"[DEBUG] 修改密码请求 - 用户: {username}, 新密码: {new_password}")

    # 🚨 漏洞：不需要验证原密码
    # 🚨 漏洞：不验证当前 session 用户和提交的 username 是否一致
    
    if not username or not new_password:
        flash("用户名和新密码不能为空")
        return redirect("/")

    if new_password != confirm_password:
        flash("两次输入的密码不一致")
        return redirect(f"/profile?user_id={USER_ID_MAP.get(1, 1)}")

    # 🚨 漏洞：任何已登录用户都可以修改任何人的密码
    if username in USERS:
        old_password = USERS[username]["password"]
        USERS[username]["password"] = new_password
        print(f"[DEBUG] 密码修改成功 - 用户: {username}, 原密码: {old_password}, 新密码: {new_password}")
        flash(f"密码修改成功！用户 {username} 的密码已更新")
    else:
        flash("用户不存在")

    # 获取 user_id 用于重定向
    user_id = None
    for uid, uname in USER_ID_MAP.items():
        if uname == username:
            user_id = uid
            break
    
    if user_id:
        return redirect(f"/profile?user_id={user_id}")
    return redirect("/")

# 动态页面加载
@app.route("/page")
def page():
    # 🚨 漏洞：从 URL 参数获取页面名称，不做路径校验（路径遍历漏洞）
    name = request.args.get("name", "")

    if not name:
        flash("页面名称不能为空")
        return redirect("/")

    # 🚨 漏洞：直接拼接用户输入到路径中，不检查 "../" 等
    # 攻击者可以通过 ../../../etc/passwd 等方式读取系统文件
    filepath = os.path.join("pages", name)
    print(f"[DEBUG] 尝试读取页面: {filepath}")

    page_content = None
    page_name = name

    # 尝试读取文件
    try:
        # 🚨 漏洞：不使用 os.path.abspath 或 os.path.realpath 规范化路径
        with open(filepath, 'r', encoding='utf-8') as f:
            page_content = f.read()
            print(f"[DEBUG] 成功读取页面内容，长度: {len(page_content)}")
    except FileNotFoundError:
        # 尝试加上 .html 后缀
        try:
            filepath_html = filepath + ".html"
            print(f"[DEBUG] 尝试读取页面（加后缀）: {filepath_html}")
            with open(filepath_html, 'r', encoding='utf-8') as f:
                page_content = f.read()
                print(f"[DEBUG] 成功读取页面内容，长度: {len(page_content)}")
        except FileNotFoundError:
            page_content = "<div class='error-msg'>页面不存在</div>"
            print(f"[DEBUG] 页面不存在: {name}")
    except Exception as e:
        page_content = f"<div class='error-msg'>读取页面失败: {str(e)}</div>"
        print(f"[DEBUG] 读取页面失败: {str(e)}")

    # 获取当前登录用户信息
    username = session.get("username")
    user_info = None
    if username in USERS:
        user_info = USERS[username]
        user_info["username"] = username

    return render_template("index.html", user_info=user_info, page_content=page_content, page_name=page_name)

# URL 抓取
@app.route("/fetch-url", methods=["POST"])
def fetch_url():
    # 检查是否登录
    username = session.get("username")
    if not username:
        flash("请先登录")
        return redirect("/login")

    # 🚨 漏洞：从表单获取 URL，不做任何限制或过滤
    url = request.form.get("url", "")
    
    print(f"[DEBUG] URL 抓取请求 - URL: {url}")

    if not url:
        flash("URL 不能为空")
        return redirect("/")

    fetch_result = None
    fetch_error = None
    status_code = None

    try:
        # 🚨 漏洞：直接将用户输入的 URL 传给 urlopen()
        # 🚨 漏洞：不限制 URL 的协议（支持 file://、dict:// 等）
        # 🚨 漏洞：不阻止内网 IP（127.0.0.1、10.x.x.x、192.168.x.x）
        # 🚨 漏洞：不设置任何代理或防火墙检查
        
        print(f"[DEBUG] 尝试抓取 URL: {url}")
        
        # 创建请求对象
        req = urllib.request.Request(url)
        
        # 🚨 漏洞：直接打开用户提供的 URL，超时 10 秒
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.status
            content = response.read().decode('utf-8', errors='ignore')
            
            # 只返回前 5000 字符
            content_preview = content[:5000]
            if len(content) > 5000:
                content_preview += "\n\n... (内容已截断，仅显示前 5000 字符)"
            
            fetch_result = {
                "url": url,
                "status_code": status_code,
                "content_length": len(content),
                "content": content_preview
            }
            
            print(f"[DEBUG] URL 抓取成功 - 状态码: {status_code}, 内容长度: {len(content)}")
            
    except urllib.error.HTTPError as e:
        fetch_error = f"HTTP 错误: {e.code} {e.reason}"
        status_code = e.code
        print(f"[DEBUG] HTTP 错误: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        fetch_error = f"URL 错误: {e.reason}"
        print(f"[DEBUG] URL 错误: {e.reason}")
    except Exception as e:
        fetch_error = f"抓取失败: {str(e)}"
        print(f"[DEBUG] 抓取失败: {str(e)}")

    # 获取当前登录用户信息
    user_info = None
    if username in USERS:
        user_info = USERS[username]
        user_info["username"] = username

    return render_template("index.html", 
                           user_info=user_info, 
                           fetch_result=fetch_result, 
                           fetch_error=fetch_error,
                           fetch_url_value=url)

# Ping 网络诊断
@app.route("/ping", methods=["GET", "POST"])
def ping():
    # 检查是否登录
    username = session.get("username")
    if not username:
        flash("请先登录")
        return redirect("/login")

    user_info = None
    if username in USERS:
        user_info = USERS[username]
        user_info["username"] = username

    ping_result = None
    ping_error = None
    ping_ip = None

    if request.method == "POST":
        # 🚨 漏洞：从表单获取 IP 参数，不做任何过滤或校验
        ip = request.form.get("ip", "")
        ping_ip = ip

        print(f"[DEBUG] Ping 请求 - IP: {ip}")

        if not ip:
            ping_error = "IP 地址不能为空"
        else:
            try:
                # 🚨 漏洞：使用 f-string 字符串拼接构建系统命令（命令注入漏洞）
                # 🚨 漏洞：使用 shell=True 执行命令，极其危险
                # Windows 使用 -n，Linux/Mac 使用 -c
                if platform.system().lower() == "windows":
                    # Windows 系统
                    command = f"ping -n 3 {ip}"
                else:
                    # Linux/Mac 系统
                    command = f"ping -c 3 {ip}"
                
                print(f"[DEBUG] 执行的命令: {command}")

                # 🚨 漏洞：直接执行用户拼接的命令，超时 30 秒
                result = subprocess.check_output(
                    command,
                    shell=True,  # 🚨 危险：使用 shell=True
                    stderr=subprocess.STDOUT,
                    timeout=30,
                    encoding='utf-8',
                    errors='ignore'
                )

                ping_result = result
                print(f"[DEBUG] Ping 成功，结果长度: {len(result)}")

            except subprocess.TimeoutExpired:
                ping_error = "Ping 超时（30秒）"
                print(f"[DEBUG] Ping 超时")
            except subprocess.CalledProcessError as e:
                ping_error = f"Ping 失败: {e.output if e.output else str(e)}"
                print(f"[DEBUG] Ping 失败: {e}")
            except Exception as e:
                ping_error = f"执行错误: {str(e)}"
                print(f"[DEBUG] Ping 错误: {str(e)}")

    return render_template("ping.html", 
                           user_info=user_info, 
                           ping_result=ping_result, 
                           ping_error=ping_error,
                           ping_ip=ping_ip)

if __name__ == "__main__":
    init_db()
    # 确保上传目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # 确保 pages 目录存在
    os.makedirs("pages", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)