<div align="center">

# Flask Blog 部署指南

**多种部署方案，轻松将博客上线**

</div>

---

## 目录

- [部署前准备](#部署前准备)
- [方案一：Render 部署（推荐）](#方案一render-部署推荐)
- [方案二：Vercel + PostgreSQL](#方案二vercel--postgresql)
- [方案三：传统 VPS 部署](#方案三传统-vps-部署)
- [方案四：Docker 部署](#方案四docker-部署)
- [域名配置](#域名配置)
- [常见问题](#常见问题)

---

## 部署前准备

### 1. 数据库初始化

首次部署前，需要初始化数据库并创建管理员账号：

```bash
python reset_database.py
```

这将创建默认管理员账号：
- 用户名: `admin01`
- 密码: `123456`

> **安全提醒**：部署后请立即修改默认密码！

### 2. 准备代码仓库

将代码推送到 GitHub：

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/flask-blog.git
git branch -M main
git push -u origin main
```

### 3. 字体文件准备（可选）

如果需要使用封面图生成功能，建议将中文字体文件放置在 `app/static/fonts/` 目录：

- `simkai.ttf` - 楷体
- `simsun.ttc` / `simsunb.ttf` - 宋体/粗宋体
- `msyh.ttc` / `msyhbd.ttc` - 微软雅黑

系统会自动检测并使用可用的字体。

---

## 方案一：Render 部署（推荐）

### 优势

- 免费套餐
- 自动部署
- 自动 HTTPS
- PostgreSQL 数据库
- 零配置启动

### 部署步骤

#### 第一步：创建数据库

1. 访问 [Render Dashboard](https://dashboard.render.com)
2. 点击 **"New +"** → **"PostgreSQL"**
3. 配置数据库：
   - 数据库名: `flaskblog`
   - 用户名: 随机生成
   - 区域: Singapore（推荐，国内访问快）
4. 选择 **Free** 套餐并创建
5. 复制 **Internal Database URL**

#### 第二步：创建 Web Service

1. 点击 **"New +"** → **"Web Service"**
2. 连接 GitHub 仓库并选择 `main` 分支

3. 配置构建：

| 选项 | 值 |
|------|-----|
| Name | `flaskblog` |
| Environment | `Python 3` |
| Region | Singapore |
| Branch | `main` |
| Root Directory | (留空) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | (留空，使用 Procfile) |

4. 配置环境变量：

| Key | Value |
|-----|-------|
| `SECRET_KEY` | 随机生成32位字符串 |
| `DATABASE_URL` | 第一步复制的 PostgreSQL URL |
| `PORT` | `5000` |
| `DEBUG` | `False` |
| `FLASK_ENV` | `production` |

5. 选择 **Free** 套餐并创建

#### 第三步：初始化数据库

部署完成后，需要手动初始化数据库：

1. 等待 2-3 分钟构建完成
2. 访问你的应用 URL，添加 `/init-db` 路径
   ```
   https://你的应用名.onrender.com/init-db
   ```
3. 你会看到类似这样的响应：
   ```json
   {
     "success": true,
     "message": "数据库初始化成功！",
     "admin_created": true
   }
   ```

#### 第四步：登录后台

访问登录页面：
```
https://你的应用名.onrender.com/auth/login
```

**默认管理员账号：**
- 用户名: `admin01`
- 密码: `123456`

> **安全提醒**：首次登录后请立即修改默认密码！

#### 第五步：配置字体（可选）

如果需要使用封面图生成功能，可以通过 Render 的 Shell 功能上传字体文件：

1. 进入 Render Dashboard
2. 选择你的 Web Service
3. 点击 "Shell" 进入命令行
4. 上传字体文件到 `app/static/fonts/` 目录

---

## 方案二：Vercel + PostgreSQL

### 优势

- 全球 CDN
- 自动 HTTPS
- 极快的部署速度
- 免费额度充足
- 边缘计算

### 部署步骤

#### 第一步：创建 PostgreSQL

推荐使用 [Supabase](https://supabase.com) 或 [Neon](https://neon.tech)：

```bash
# Supabase 免费套餐
# - 500MB 数据库存储
# - 无限 API 请求
```

#### 第二步：部署到 Vercel

1. 访问 [Vercel](https://vercel.com)
2. 点击 **"New Project"**
3. 导入 GitHub 仓库
4. 配置项目：
   - Framework Preset: **Other**
   - Root Directory: (留空)
   - Build Command: `pip install -r requirements.txt && gunicorn app:create_app():proxy`
   - Output Directory: (留空)
5. 添加环境变量：
   ```
   DATABASE_URL=你的PostgreSQL URL
   SECRET_KEY=你的密钥
   DEBUG=False
   ```
6. 部署！

#### 第三步：初始化数据库

部署完成后访问：
```
https://你的应用.vercel.app/init-db
```

---

## 方案三：传统 VPS 部署

### 系统要求

- Ubuntu 20.04+ / CentOS 8+
- Python 3.8+
- 512MB+ 内存
- 10GB+ 磁盘

### 部署步骤

#### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib supervisor

# CentOS/RHEL
sudo yum install -y python3-pip python3-venv nginx postgresql-server postgresql-contrib supervisor
```

#### 2. 配置 PostgreSQL

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE flaskblog;
CREATE USER flaskblog WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE flaskblog TO flaskblog;
\q
```

#### 3. 配置项目

```bash
# 克隆代码
cd /var/www
git clone https://github.com/你的用户名/flask-blog.git
cd flask-blog

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# 初始化数据库
python reset_database.py
```

#### 4. 配置环境变量

```bash
cat > .env << EOF
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=postgresql://flaskblog:your_password@localhost/flaskblog
DEBUG=False
EOF
```

#### 5. 配置 Supervisor

```bash
sudo tee /etc/supervisor/conf.d/flaskblog.conf << EOF
[program:flaskblog]
command=/var/www/flask-blog/venv/bin/gunicorn app:create_app():proxy
directory=/var/www/flask-blog
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/flaskblog.err.log
stdout_logfile=/var/log/flaskblog.out.log
EOF
```

#### 6. 配置 Nginx

```bash
sudo tee /etc/nginx/sites-available/flaskblog << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /var/www/flask-blog/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用配置
sudo ln -s /etc/nginx/sites-available/flaskblog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. 启动服务

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start flaskblog
```

---

## 方案四：Docker 部署

### 创建 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "app:create_app():proxy", "--bind", "0.0.0.0:5000"]
```

### 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/flaskblog
      - DEBUG=False
    depends_on:
      - db
    restart: always

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=flaskblog
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

### 启动服务

```bash
# 构建并启动
docker-compose up -d

# 初始化数据库
docker-compose exec web python reset_database.py

# 查看日志
docker-compose logs -f
```

---

## 域名配置

### 购买域名

推荐域名注册商：
- [阿里云](https://wanwang.aliyun.com)
- [腾讯云](https://dnspod.cloud.tencent.com)
- [Namecheap](https://www.namecheap.com)

### DNS 配置

添加以下记录：

| 类型 | 名称 | 值 |
|------|------|-----|
| A | @ | 你的服务器 IP |
| CNAME | www | 你的域名 |
| CNAME | @ | (如果使用 Vercel/Render) |

### SSL 证书

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 常见问题

### 1. 应用无法启动

**检查项**：
- [ ] 环境变量是否正确配置
- [ ] `requirements.txt` 依赖是否完整
- [ ] 数据库连接字符串是否正确
- [ ] 日志中是否有具体错误信息

### 2. Render 部署后 Internal Server Error

**症状**：应用启动成功，但访问任何页面都返回 500 错误

**原因**：数据库表未创建

**解决方案**：
1. 访问 `https://你的应用.onrender.com/init-db` 初始化数据库
2. 访问 `https://你的应用.onrender.com/check-db` 检查状态
3. 查看 Render 日志确认具体错误

### 3. 登录失败 - "用户名或密码错误"

**症状**：使用正确的用户名密码仍无法登录

**可能原因**：
- 数据库中用户未创建
- 密码哈希字段长度不足

**解决方案**：
1. 访问 `/check-db` 确认用户是否存在
2. 访问 `/init-db` 重新创建管理员账号
3. 如果仍失败，查看日志确认密码哈希字段是否为 VARCHAR(255)

### 4. 部署辅助说明端点

**应用内置了以下调试端点**：

| 端点 | 用途 | 说明 |
|------|------|------|
| `/init-db` | 初始化数据库 | 创建表和默认管理员 |
| `/check-db` | 检查数据库状态 | 查看表和用户信息 |

> **安全提示**：生产环境部署完成后，建议删除或保护这些端点

### 5. 数据库连接失败

**PostgreSQL 连接字符串格式**：
```
postgresql://username:password@hostname:5432/database_name
```

**SQLite 连接字符串格式**：
```
sqlite:///path/to/database.db
```

### 6. 静态文件 404

**Nginx 配置**：
```nginx
location /static {
    alias /path/to/app/static;
    expires 30d;
}
```

### 7. CSS 样式未加载

确保：
- [ ] `DEBUG=False` 时静态文件路径正确
- [ ] Nginx 配置了 `/static` 别名
- [ ] 文件权限正确（`chmod -R 755`）

### 8. 忘记管理员密码

**本地开发环境**：运行数据库重置脚本
```bash
python reset_database.py
```

**生产环境**：访问 `/init-db` 重新创建管理员

### 9. 更新代码后未生效

**手动重启服务**：
```bash
# Supervisor
sudo supervisorctl restart flaskblog

# Docker
docker-compose restart

# Render/Vercel
git push 会自动触发重新部署
```

### 10. 封面图生成失败

**可能原因**：
- 字体文件不存在
- Pillow 库未安装
- 权限问题

**解决方案**：
1. 确认字体文件在 `app/static/fonts/` 目录
2. 检查 Pillow 是否安装：`pip list | grep Pillow`
3. 确保 `app/static/uploads/covers/` 目录有写入权限
4. 查看应用日志获取详细错误信息

### 11. 图片上传失败

**检查项**：
- [ ] 上传目录是否存在且有写入权限
- [ ] 图片格式是否支持（PNG、JPG、GIF、WebP）
- [ ] 图片大小是否超过限制
- [ ] 查看 Nginx/应用日志

---

## 平台对比

| 平台 | 免费额度 | 优点 | 缺点 | 推荐度 |
|------|---------|------|------|--------|
| **Render** | 750h/月 | 自动部署，PostgreSQL | 休眠慢 | ⭐⭐⭐⭐⭐ |
| **Vercel** | 100GB/月 | 全球CDN，极快 | 需要单独配置 DB | ⭐⭐⭐⭐ |
| **VPS** | 取决于配置 | 完全控制 | 需运维 | ⭐⭐⭐ |
| **Docker** | 取决于配置 | 环境一致 | 学习成本 | ⭐⭐⭐⭐ |

---

## 性能优化建议

### 应用层

1. **启用缓存**
   ```python
   # 安装 Redis
   pip install redis
   ```

2. **静态文件 CDN**
   - 将 `app/static` 上传到 CDN
   - 修改 `static_folder` 为 CDN URL

### 数据库层

1. **添加索引**
   ```sql
   CREATE INDEX idx_post_published ON post(published);
   CREATE INDEX idx_post_created_at ON post(created_at DESC);
   ```

2. **连接池配置**
   ```python
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_size': 10,
       'pool_recycle': 3600,
       'pool_pre_ping': True
   }
   ```

### Web 服务器

1. **启用 Gzip 压缩**
   ```nginx
   gzip on;
   gzip_types text/css application/javascript;
   ```

2. **配置缓存头**
   ```nginx
   location /static {
       expires 30d;
       add_header Cache-Control "public, immutable";
   }
   ```

### 图片优化

1. **启用图片懒加载** - 已内置
2. **使用 WebP 格式** - 减少图片大小
3. **配置 CDN** - 加速图片加载

---

## 备份建议

### 数据库备份

```bash
# PostgreSQL 备份
pg_dump -U flaskblog flaskblog > backup_$(date +%Y%m%d).sql

# 恢复
psql -U flaskblog flaskblog < backup_20250101.sql
```

### 文件备份

```bash
# 定期备份上传文件
tar -czf uploads_$(date +%Y%m%d).tar.gz app/static/uploads/

# 备份到云存储
# 阿里云OSS / 腾讯云COS
```

---

## 监控建议

### 必要监控项

- **Uptime** - 网站可用性
- **响应时间** - 页面加载速度
- **错误率** - 5xx 错误比例
- **数据库连接** - 连接池状态

### 监控工具

- [UptimeRobot](https://uptimerobot.com) - 免费
- [Pingdom](https://www.pingdom.com) - 免费
- [Grafana](https://grafana.com) - 自建监控

---

## 文档说明

| 文件 | 说明 |
|------|------|
| `README.md` | 项目介绍文档 |
| `DEPLOY.md` | 本部署文档 |
| `CONTRIBUTING.md` | 贡献指南 |
| `requirements.txt` | Python 依赖 |
| `reset_database.py` | 数据库重置脚本 |
| `run.py` | 启动脚本 |

---

## 部署经验总结

### 从首次部署中学习

本项目的首次 Render 部署过程中遇到了一些问题，这些问题及解决方案已整合到项目中：

**问题 1：数据库表未自动创建**
- **原因**：`db.create_all()` 只在 DEBUG=True 时执行
- **解决**：添加 `/init-db` HTTP 端点，允许手动初始化

**问题 2：密码哈希字段长度不足**
- **原因**：werkzeug 生成的 scrypt 哈希为 132 字符，超过 VARCHAR(128)
- **解决**：将 `password_hash` 字段增加到 VARCHAR(255)

**问题 3：缺少部署调试工具**
- **原因**：无法快速诊断数据库状态
- **解决**：添加 `/check-db` 端点查看表和用户信息

**改进后的部署流程：**
1. 部署代码到 Render
2. 访问 `/init-db` 初始化数据库（自动迁移密码字段）
3. 访问 `/check-db` 验证状态
4. 登录后台开始使用

---

## 获取帮助

- **邮箱**: 3497875641@qq.com
- **Issues**: [GitHub Issues](https://github.com/linxiong-rgb/flask-blog/issues)
- **文档**: [完整文档](https://github.com/linxiong-rgb/flask-blog)

---

<div align="center">

**祝你部署顺利！**

如有问题，欢迎反馈

</div>
