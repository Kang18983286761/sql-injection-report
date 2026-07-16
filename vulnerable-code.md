# 用户信息管理系统 - 漏洞版本

> 本代码包含多个安全漏洞，仅用于安全学习和漏洞演示目的。请勿在生产环境中使用！

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

## 🚨 存在的安全漏洞

| 漏洞类型 | 严重程度 | 位置 |
|---------|---------|------|
| 明文密码存储 | ⭐⭐⭐⭐⭐ 高危 | `app.py` USERS字典 |
| 敏感信息泄露 | ⭐⭐⭐⭐⭐ 高危 | `templates/login.html` HTML注释 |
| 信息泄露 | ⭐⭐⭐⭐ 高危 | `templates/index.html` 密码展示 |
| 弱密钥 | ⭐⭐⭐⭐ 高危 | `app.py` secret_key |
| 缺少CSRF保护 | ⭐⭐⭐ 中危 | 所有表单 |

---

## 📄 app.py

```python
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "dev-key-2025"  # 🚨 漏洞：弱密钥，容易被猜测

# 🚨 漏洞：明文存储密码，未进行哈希处理
USERS = {
    "admin": {
        "password": "admin123",  # 明文密码
        "role": "admin",
        "email": "admin@example.com",
        "phone": "13800138000",
        "balance": 99999
    },
    "alice": {
        "password": "alice2025",  # 明文密码
        "role": "user",
        "email": "alice@example.com",
        "phone": "13900139001",
        "balance": 100
    }
}

# 首页
@app.route("/")
def index():
    username = session.get("username")
    user_info = None
    if username and username in USERS:
        user_info = USERS[username]
        user_info["username"] = username
    # 🚨 漏洞：将包含密码的完整用户信息传递给模板
    return render_template("index.html", user_info=user_info)

# 登录
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # 🚨 漏洞：直接字符串比较，未使用安全的密码哈希验证
        if username in USERS and USERS[username]["password"] == password:
            session["username"] = username
            user_info = USERS[username]
            user_info["username"] = username
            # 🚨 漏洞：登录成功后传递包含密码的用户信息
            return render_template("index.html", user_info=user_info)
        else:
            error = "用户名或密码错误"

    return render_template("login.html", error=error)

# 登出
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

---

## 📄 templates/base.html

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
<!-- 🚨 漏洞：HTML注释泄露默认管理员账号信息 -->
<!-- 调试信息 - 默认管理员账号 用户名: admin 密码: admin123 -->
{% extends "base.html" %}

{% block content %}
<div class="card">
    <h2>用户登录</h2>
    {% if error %}
    <div class="error-msg">{{ error }}</div>
    {% endif %}
    <!-- 🚨 漏洞：缺少CSRF令牌保护 -->
    <form method="POST" action="/login">
        <div class="form-group">
            <label for="username">用户名</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div class="form-group">
            <label for="password">密码</label>
            <input type="password" id="password" name="password" required>
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
            <!-- 🚨 漏洞：在页面上显示用户密码 -->
            <li><strong>密码：</strong>{{ user_info.password }}</li>
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

.form-group input {
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

## ⚠️ 漏洞详情说明

### 1. 明文密码存储

**问题描述**：用户密码以明文形式直接存储在代码中的字典里。

**危害**：
- 数据库泄露时，攻击者可直接获取所有用户密码
- 开发人员、运维人员可直接看到用户密码
- 用户习惯在多个网站使用相同密码，造成连锁危害

**攻击示例**：
```python
# 攻击者只需读取代码或数据库即可获取密码
print(USERS["admin"]["password"])  # 输出: admin123
```

---

### 2. HTML注释泄露敏感信息

**问题描述**：登录页面HTML源代码中包含默认管理员账号密码注释。

**危害**：
- 任何查看网页源代码的人都能看到管理员密码
- 攻击者可直接使用泄露的密码登录系统

**攻击步骤**：
1. 访问登录页面
2. 右键查看网页源代码
3. 找到注释中的账号密码
4. 使用泄露的密码登录

---

### 3. 页面展示用户密码

**问题描述**：登录后，用户信息页面直接展示用户的明文密码。

**危害**：
- 用户密码暴露在页面上
- 屏幕录制、肩窥攻击可获取密码
- 浏览器历史记录可能保存页面内容

---

### 4. 弱密钥配置

**问题描述**：Flask应用使用简单的字符串作为secret_key。

**危害**：
- 攻击者可伪造session
- 可绕过登录验证，直接以任意用户身份登录

---

### 5. 缺少CSRF保护

**问题描述**：表单未添加CSRF令牌保护。

**危害**：
- 攻击者可诱导用户点击恶意链接
- 可在用户不知情的情况下提交表单

---

## 🎯 漏洞利用演示

### 利用HTML注释泄露的密码登录

```bash
# 步骤1: 获取登录页面
curl http://localhost:5000/login

# 步骤2: 从HTML源代码中找到注释
# <!-- 调试信息 - 默认管理员账号 用户名: admin 密码: admin123 -->

# 步骤3: 使用泄露的密码登录
curl -X POST http://localhost:5000/login \
  -d "username=admin&password=admin123"
```

---

## 📚 学习建议

本代码示例展示了Web开发中常见的安全错误：

1. **永远不要明文存储密码** - 使用 `bcrypt`、`argon2` 等哈希算法
2. **不要在前端代码中泄露敏感信息** - HTML注释、JavaScript代码都可能被查看
3. **不要在页面展示敏感信息** - 密码等敏感字段不应展示给用户
4. **使用强密钥** - 生成随机、复杂的密钥，不要硬编码
5. **启用CSRF保护** - Flask-WTF 等扩展提供CSRF令牌功能

---

> ⚠️ **声明**：本代码仅用于安全教学目的，请勿用于实际生产环境。