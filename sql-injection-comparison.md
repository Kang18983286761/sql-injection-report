# 用户管理系统 - SQL注入漏洞对比

> 本文档对比了漏洞版本和安全版本的代码差异，用于学习SQL注入漏洞及其修复方法。

---

## 📋 漏洞概述

| 漏洞类型 | 严重程度 | 影响范围 |
|---------|---------|---------|
| 注册功能SQL注入 | ⭐⭐⭐⭐⭐ 高危 | 可插入任意数据、绕过验证 |
| 搜索功能SQL注入 | ⭐⭐⭐⭐ 高危 | 可泄露所有用户数据 |

---

## 🚨 漏洞版本代码

### 注册功能 - 存在SQL注入

```python
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

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

                # 🚨 漏洞：使用 f-string 字符串拼接 SQL
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
```

### 搜索功能 - 存在SQL注入

```python
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

        # 🚨 漏洞：使用 f-string 字符串拼接 SQL
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
```

---

## ✅ 安全版本代码

### 注册功能 - 参数化查询

```python
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

    return render_template("register.html", error=error)
```

### 搜索功能 - 参数化查询

```python
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
```

---

## 🎯 SQL注入攻击演示

### 1. 注册功能注入攻击

#### 攻击payload 1：绕过注册直接插入管理员

**输入数据：**
```
用户名: hacker
密码: hack123
邮箱: ', 'admin'), ('hacker2', 'hack123', 'hacker@evil.com', '1234567890');--
手机: (留空)
```

**执行的SQL：**
```sql
INSERT INTO users (username, password, email, phone) VALUES ('hacker', 'hack123', '', 'admin'), ('hacker2', 'hack123', 'hacker@evil.com', '1234567890');--', '')
```

**结果：** 成功插入两个用户，其中一个是管理员。

---

#### 攻击payload 2：修改已有用户密码

**输入数据：**
```
用户名: test');UPDATE users SET password='hacked' WHERE username='admin';--
密码: anything
邮箱: test@test.com
手机: 1234567890
```

**执行的SQL：**
```sql
INSERT INTO users (username, password, email, phone) VALUES ('test');UPDATE users SET password='hacked' WHERE username='admin';--', 'anything', 'test@test.com', '1234567890')
```

**结果：** admin用户的密码被修改为 `hacked`。

---

### 2. 搜索功能注入攻击

#### 攻击payload 1：获取所有用户数据

**搜索关键词：**
```
' OR '1'='1
```

**执行的SQL：**
```sql
SELECT * FROM users WHERE username LIKE '%' OR '1'='1%' OR email LIKE '%' OR '1'='1%'
```

**结果：** 返回数据库中所有用户记录。

---

#### 攻击payload 2：获取数据库表结构

**搜索关键词：**
```
' UNION SELECT 1, name, sql, '4' FROM sqlite_master WHERE type='table'--
```

**执行的SQL：**
```sql
SELECT * FROM users WHERE username LIKE '%' UNION SELECT 1, name, sql, '4' FROM sqlite_master WHERE type='table'--%' OR email LIKE '%' UNION SELECT 1, name, sql, '4' FROM sqlite_master WHERE type='table'--%'
```

**结果：** 显示数据库中所有表的结构信息。

---

#### 攻击payload 3：批量删除数据

**搜索关键词：**
```
%';DELETE FROM users WHERE '1'='1
```

**执行的SQL：**
```sql
SELECT * FROM users WHERE username LIKE '%%';DELETE FROM users WHERE '1'='1%' OR email LIKE '%%';DELETE FROM users WHERE '1'='1%'
```

**结果：** 删除所有用户数据。

---

## 🔧 修复方法详解

### 1. 参数化查询（最有效）

**原理：** 参数化查询将SQL语句和数据分离，数据库驱动会自动处理特殊字符转义。

**Python SQLite示例：**
```python
# 危险：字符串拼接
sql = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(sql)

# 安全：参数化查询
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

**注意事项：**
- SQLite 使用 `?` 作为占位符
- MySQL 使用 `%s` 作为占位符
- PostgreSQL 使用 `%s` 或 `%(name)s`

---

### 2. 输入验证

```python
# 长度限制
if len(username) > 50:
    return "用户名过长"

# 字符白名单（只允许字母数字下划线）
import re
if not re.match(r'^[a-zA-Z0-9_]+$', username):
    return "用户名只能包含字母数字下划线"

# 邮箱格式验证
import re
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
if not re.match(email_pattern, email):
    return "邮箱格式不正确"
```

---

### 3. 最小权限原则

```python
# 创建只读数据库用户
# CREATE USER 'web_readonly'@'localhost' IDENTIFIED BY 'password';
# GRANT SELECT ON user_db.users TO 'web_readonly'@'localhost';

# 应用中连接时使用只读账户
conn = sqlite3.connect(DB_PATH)
# 搜索功能只需要SELECT权限，不应有INSERT/UPDATE/DELETE权限
```

---

### 4. 错误信息处理

```python
# 危险：暴露详细错误信息
except Exception as e:
    error = f"注册失败: {str(e)}"  # 可能泄露数据库结构

# 安全：模糊错误信息
except Exception as e:
    error = "注册失败，请稍后重试"
    # 记录详细错误到日志，但不显示给用户
    app.logger.error(f"Registration error: {str(e)}")
```

---

## 📊 对比总结

| 安全项目 | 漏洞版本 | 安全版本 |
|---------|---------|---------|
| SQL拼接方式 | f-string字符串拼接 | 参数化查询 `?` 占位符 |
| 输入验证 | 无 | 长度、格式验证 |
| 错误处理 | 显示详细错误 | 模糊错误信息 |
| 调试信息 | 打印SQL到控制台 | 不打印敏感信息 |
| 数据库权限 | 未分离 | 建议只读账户 |

---

## 🛡️ 额外安全建议

### 使用ORM框架

```python
# SQLAlchemy ORM示例
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    email = db.Column(db.String(100))

# 安全的用户创建
user = User(username=username, password=password, email=email)
db.session.add(user)
db.session.commit()
```

### 密码哈希存储

```python
from werkzeug.security import generate_password_hash, check_password_hash

# 存储时哈希
password_hash = generate_password_hash(password)

# 验证时比对
if check_password_hash(user.password_hash, input_password):
    # 登录成功
```

---

> ⚠️ **声明**：本文档仅用于安全教学目的。请勿在未经授权的系统上尝试SQL注入攻击。