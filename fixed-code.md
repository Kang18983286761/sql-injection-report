# 用户信息管理系统 - 安全版本

> 本代码修复了所有已知安全漏洞，可作为安全开发的参考实现。

---

## 📋 项目结构

```
project/
├── app.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── login.html
└── static/
    └── css/
        └── style.css
```

---

## 🔐 安全修复清单

| 原漏洞 | 修复方案 | 状态 |
|-------|---------|------|
| 明文密码存储 | 使用 `werkzeug.security` 进行密码哈希 | ✅ 已修复 |
| HTML注释泄露密码 | 移除所有敏感信息注释 | ✅ 已修复 |
| 页面展示密码 | 从模板中移除密码字段显示 | ✅ 已修复 |
| 弱密钥 | 使用环境变量配置随机密钥 | ✅ 已修复 |
| 缺少CSRF保护 | 添加隐藏令牌字段 | ✅ 已修复 |

---

## 📦 依赖安装

```bash
pip install flask werkzeug
```

---

## 📄 app.py

```python
import os
import secrets
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ✅ 修复：从环境变量获取密钥，或生成安全的随机密钥
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# ✅ 修复：密码使用安全的哈希算法存储
USERS = {
    "admin": {
        "password_hash": generate_password_hash("admin123"),  # 哈希存储
        "role": "admin",
        "email": "admin@example.com",
        "phone": "13800138000",
        "balance": 99999
    },
    "alice": {
        "password_hash": generate_password_hash("alice2025"),  # 哈希存储
        "role": "user",
        "email": "alice@example.com",
        "phone": "13900139001",
        "balance": 100
    }
}

# ✅ 修复：生成CSRF令牌
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

# ✅ 修复：验证CSRF令牌
def validate_csrf_token(token):
    return token == session.get('_csrf_token')

# ✅ 修复：过滤敏感字段，不传递密码哈希到模板
def get_safe_user_info(username):
    if username not in USERS:
        return None
    user = USERS[username]
    return {
        "username": username,
        "role": user["role"],
        "email": user["email"],
        "phone": user["phone"],
        "balance": user["balance"]
        # 注意：不包含任何密码相关字段
    }

@app.route("/")
def index():
    username = session.get("username")
    user_info = get_safe_user_info(username) if username else None
    return render_template("index.html", user_info=user_info)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        # ✅ 修复：验证CSRF令牌
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            error = "安全验证失败，请刷新页面重试"
        else:
            username = request.form.get("username")
            password = request.form.get("password")

            if username in USERS:
                # ✅ 修复：使用安全的密码哈希验证
                if check_password_hash(USERS[username]["password_hash"], password):
                    session["username"] = username
                    session.pop('_csrf_token', None)  # 登录成功后重置CSRF令牌
                    # ✅ 修复：使用过滤后的用户信息
                    return redirect("/")
                else:
                    # ✅ 修复：错误提示模糊化，不透露具体信息
                    error = "用户名或密码错误"
            else:
                error = "用户名或密码错误"

    # GET请求或登录失败时渲染页面
    csrf_token = generate_csrf_token()
    return render_template("login.html", error=error, csrf_token=csrf_token)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    # ✅ 修复：生产环境应关闭debug模式
    app.run(debug=False, host="127.0.0.1", port=5000)
```

---

## 📄 templates/base.html

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <title>用户管理系统</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="navbar-brand">用户管理系统</div>
        <div class="navbar-menu">
            {% if session.get("username") %}
            <span class="navbar-welcome">欢迎，{{ session.get("username") }}</span>
            <a href="/logout" class="navbar-link">退出</a>
            {% else %}
            <a href="/login" class="navbar-link">登录</a>
            {% endif %}
        </div>
    </nav>
    <main class="container">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

---

## 📄 templates/login.html

```html
{# ✅ 修复：移除了泄露敏感信息的HTML注释 #}
{% extends "base.html" %}

{% block content %}
<div class="card">
    <h2>用户登录</h2>
    {% if error %}
    <div class="error-msg">{{ error }}</div>
    {% endif %}
    <form method="POST" action="/login">
        {# ✅ 修复：添加CSRF令牌隐藏字段 #}
        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
        <div class="form-group">
            <label for="username">用户名</label>
            <!-- ✅ 添加autocomplete属性增强安全 -->
            <input type="text" id="username" name="username"
                   required autocomplete="username" maxlength="50">
        </div>
        <div class="form-group">
            <label for="password">密码</label>
            <input type="password" id="password" name="password"
                   required autocomplete="current-password" maxlength="100">
        </div>
        <button type="submit" class="btn">登录</button>
    </form>
</div>
{% endblock %}
```

---

## 📄 templates/index.html

```html
{% extends "base.html" %}

{% block content %}
<div class="card">
    {% if user_info %}
    <h2>欢迎回来，{{ user_info.username }}！</h2>
    <div class="user-info">
        <h3>用户信息</h3>
        <ul>
            <li><strong>用户名：</strong>{{ user_info.username }}</li>
            {# ✅ 修复：移除了密码字段显示 #}
            <li><strong>邮箱：</strong>{{ user_info.email }}</li>
            <li><strong>手机：</strong>{{ user_info.phone }}</li>
            <li><strong>角色：</strong>{{ user_info.role }}</li>
            <li><strong>余额：</strong>{{ user_info.balance }}</li>
        </ul>
    </div>
    <a href="/logout" class="btn">退出登录</a>
    {% else %}
    <h2>请先登录</h2>
    <p>您尚未登录，请点击下方按钮登录系统。</p>
    <a href="/login" class="btn">去登录</a>
    {% endif %}
</div>
{% endblock %}
```

---

## 📄 static/css/style.css

```css
/* 全局 reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: #f5f5f5;
    color: #333;
}

/* 导航栏样式 */
.navbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: white;
}

.navbar-brand {
    font-size: 20px;
    font-weight: bold;
}

.navbar-menu {
    display: flex;
    align-items: center;
    gap: 20px;
}

.navbar-welcome {
    font-size: 14px;
}

.navbar-link {
    color: white;
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 4px;
    transition: background 0.3s;
}

.navbar-link:hover {
    background: rgba(255, 255, 255, 0.2);
}

/* 容器 */
.container {
    max-width: 800px;
    margin: 30px auto;
    padding: 0 20px;
}

/* 卡片样式 */
.card {
    background: white;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.card h2 {
    margin-bottom: 20px;
    color: #333;
}

/* 表单样式 */
.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #555;
}

.form-group input[type="text"],
.form-group input[type="password"] {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.form-group input:focus {
    outline: none;
    border-color: #667eea;
}

/* 按钮样式 */
.btn {
    display: inline-block;
    padding: 12px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    text-decoration: none;
    transition: opacity 0.3s;
}

.btn:hover {
    opacity: 0.9;
}

/* 用户信息 */
.user-info {
    margin: 20px 0;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 4px;
}

.user-info h3 {
    margin-bottom: 15px;
    color: #555;
}

.user-info ul {
    list-style: none;
}

.user-info li {
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.user-info li:last-child {
    border-bottom: none;
}

/* 错误提示 */
.error-msg {
    background: #fee;
    color: #c00;
    padding: 10px 15px;
    border-radius: 4px;
    margin-bottom: 20px;
}
```

---

## 🔧 安全修复详解

### 1. 密码哈希存储

**修复方法**：使用 `werkzeug.security` 模块的 `generate_password_hash` 和 `check_password_hash` 函数。

```python
from werkzeug.security import generate_password_hash, check_password_hash

# 存储密码时
password_hash = generate_password_hash("admin123")

# 验证密码时
if check_password_hash(stored_hash, input_password):
    # 密码正确
```

**为什么安全**：
- 使用 PBKDF2-HMAC-SHA256 算法
- 自动添加随机盐值
- 即使数据库泄露，攻击者也无法还原原始密码

---

### 2. 移除敏感信息注释

**修复方法**：完全移除HTML中的注释，或使用模板引擎的注释语法。

```html
{# Jinja2模板注释，不会出现在HTML源代码中 #}
<!-- 这种注释会出现在HTML源代码中，不要写敏感信息 -->
```

---

### 3. 过滤敏感字段

**修复方法**：创建专门函数过滤用户信息，只返回需要展示的字段。

```python
def get_safe_user_info(username):
    user = USERS[username]
    return {
        "username": username,
        "role": user["role"],
        # 不返回 password_hash
    }
```

---

### 4. 安全密钥配置

**修复方法**：使用环境变量或生成随机密钥。

```python
import os
import secrets

# 方式1：从环境变量读取
app.secret_key = os.environ.get('SECRET_KEY')

# 方式2：生成随机密钥
app.secret_key = secrets.token_hex(32)
```

**生产环境建议**：
```bash
# Linux/Mac
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Windows PowerShell
$env:SECRET_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

---

### 5. CSRF保护

**修复方法**：在表单中添加隐藏的CSRF令牌字段。

```python
# 生成令牌
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

# 验证令牌
def validate_csrf_token(token):
    return token == session.get('_csrf_token')
```

```html
<!-- 表单中添加隐藏字段 -->
<input type="hidden" name="csrf_token" value="{{ csrf_token }}">
```

---

## 🛡️ 额外安全建议

### 使用 Flask-WTF 扩展

Flask-WTF 提供了更完善的CSRF保护和表单验证：

```bash
pip install Flask-WTF
```

```python
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField

csrf = CSRFProtect(app)

class LoginForm(FlaskForm):
    username = StringField('用户名')
    password = PasswordField('密码')
```

### 使用 Flask-Login 管理会话

```bash
pip install Flask-Login
```

```python
from flask_login import LoginManager, login_user, logout_user, login_required

login_manager = LoginManager(app)
login_manager.login_view = 'login'
```

### 使用真实数据库

生产环境应使用真实数据库（如 PostgreSQL、MySQL），而不是内存字典：

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/db'
db = SQLAlchemy(app)
```

---

## 📊 安全对比表

| 安全项目 | 漏洞版本 | 安全版本 |
|---------|---------|---------|
| 密码存储 | 明文 | PBKDF2哈希 |
| 密钥强度 | 简单字符串 | 32字节随机 |
| 信息泄露 | HTML注释含密码 | 无敏感信息 |
| 页面展示 | 显示密码 | 过滤敏感字段 |
| CSRF保护 | 无 | 令牌验证 |
| Debug模式 | 开启 | 关闭 |
| 监听地址 | 0.0.0.0 | 127.0.0.1 |

---

## 🚀 部署建议

### 生产环境配置

```python
# config.py
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    SESSION_COOKIE_SECURE = True    # 仅HTTPS
    SESSION_COOKIE_HTTPONLY = True  # 防止JS访问
    PERMANENT_SESSION_LIFETIME = 3600  # 会话超时1小时
```

### 运行命令

```bash
# 设置环境变量
export FLASK_ENV=production
export SECRET_KEY=your-random-secret-key

# 使用生产服务器
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

---

> ✅ **提示**：本代码修复了所有已知安全漏洞，但仍需结合具体业务场景进行安全评估。建议定期进行安全审计和渗透测试。