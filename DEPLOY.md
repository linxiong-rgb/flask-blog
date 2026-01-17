# linxiong's Blog - Render 部署指南

## 快速开始

### Windows 用户

```cmd
# 1. 运行部署脚本
deploy.bat

# 2. 按提示输入 GitHub 仓库地址
# 3. 等待推送完成
# 4. 访问 Render 控制台创建 Web Service
```

### Linux/Mac 用户

```bash
# 1. 给脚本添加执行权限
chmod +x deploy.sh

# 2. 运行部署脚本
./deploy.sh
```

---

## 部署步骤详解

### 第一步：准备代码

1. **生成配置**
   ```cmd
   python deploy.py
   ```
   这会生成 `SECRET_KEY` 和 `.env` 文件

2. **初始化本地数据库**（可选）
   ```cmd
   python init_db.py
   ```
   按提示创建管理员账号

3. **推送到 GitHub**
   ```cmd
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/你的用户名/my-blog.git
   git branch -M main
   git push -u origin main
   ```

---

### 第二步：在 Render 创建数据库

1. 访问 https://dashboard.render.com
2. 点击 **"New +"** → **"PostgreSQL"**
3. 配置：
   - 数据库名: `linxiong_blog`
   - 用户名: 随机生成
   - 选择 **Free** 套餐
4. 创建后，复制 **Internal Database URL**
   - 格式: `postgresql://user:pass@host/dbname`

---

### 第三步：在 Render 创建 Web Service

1. 点击 **"New +"** → **"Web Service"**

2. **连接仓库**
   - 授权 GitHub 访问
   - 选择 `my-blog` 仓库
   - 选择 `main` 分支

3. **配置构建**
   | 选项 | 值 |
   |------|-----|
   | Name | `linxiong-blog` |
   | Environment | `Python 3` |
   | Region | Singapore (离国内最近) |
   | Branch | `main` |
   | Root Directory | (留空) |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:create_app()` |

4. **配置环境变量** (Environment Variables)

   点击 "Advanced" → "Environment Variables"，添加：

   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | 运行 `python deploy.py` 获取 |
   | `DATABASE_URL` | 第二步复制的 PostgreSQL URL |
   | `PORT` | `5000` |
   | `DEBUG` | `False` |

5. **选择套餐**
   - 选择 **Free** 套餐
   - 点击 **"Create Web Service"**

---

### 第四步：完成部署

1. **等待构建**（约2-3分钟）
   - Render 会自动拉取代码
   - 安装依赖
   - 启动服务

2. **获取访问地址**
   - 部署成功后会显示 URL
   - 格式: `https://linxiong-blog.onrender.com`

3. **创建管理员账号**
   - 访问博客 URL
   - 点击"注册"
   - 创建账号

---

## 常见问题

### 1. 应用无法启动

**检查 Logs**：
- Web Service → Logs 标签
- 常见原因：
  - `DATABASE_URL` 格式错误
  - 缺少环境变量
  - 依赖安装失败

### 2. 数据库连接失败

确认 `DATABASE_URL` 格式正确：
```
postgresql://用户名:密码@主机:端口/数据库名
```

### 3. 休眠唤醒慢

免费套餐15分钟无请求会休眠，首次访问需等待约30秒唤醒。

### 4. 如何更新代码

```cmd
git add .
git commit -m "更新描述"
git push
# Render 会自动检测并重新部署
```

---

## 免费套餐限制

| 项目 | 限制 |
|------|------|
| 运行时间 | 750小时/月 |
| 休眠时间 | 15分钟无活动 |
| 内存 | 512MB |
| 数据库 | PostgreSQL Free 90天 |
| 带宽 | 100GB/月 |

> **提示**：PostgreSQL Free 实例 90天后需要手动续期（仍然免费）

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `deploy.py` | 生成 SECRET_KEY 和环境变量 |
| `init_db.py` | 初始化本地数据库和管理员 |
| `deploy.bat` | Windows 快速部署脚本 |
| `deploy.sh` | Linux/Mac 快速部署脚本 |
| `Procfile` | Render 启动配置 |
| `runtime.txt` | Python 版本 |
| `requirements.txt` | 项目依赖 |

---

## 自定义域名（需要付费）

1. 在域名注册商添加 CNAME 记录：
   - 主机记录: `www`
   - 记录值: `linxiong-blog.onrender.com`

2. Render 控制台：
   - Web Service → Settings → Custom Domains
   - 添加域名

3. 升级到付费套餐（$7/月起）

---

## 备份建议

免费套餐不保证数据持久，建议定期备份：

```cmd
# 导出文章
访问: https://你的博客/admin/export
```

或使用 PostgreSQL 导出功能。
