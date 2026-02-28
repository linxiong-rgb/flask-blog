# Cloudflare R2 对象存储配置指南

## 为什么使用 Cloudflare R2？

Render 免费版的文件系统是临时的，服务重启后上传的图片会丢失。Cloudflare R2 提供免费的对象存储服务，可以永久保存图片文件。

**R2 免费额度：**
- 每月 10GB 存储
- 每月 1000 万次 Class A 操作（写入）
- 每月 1000 万次 Class B 操作（读取）
- 免费出站流量（这是 R2 最大的优势）

## 设置步骤

### 1. 创建 Cloudflare R2 存储桶

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 在左侧菜单中选择 **R2**
3. 点击 **创建存储桶**
4. 输入存储桶名称（例如：`my-blog-images`）
5. 选择位置（建议选择离你用户最近的区域）
6. 点击 **创建存储桶**

### 2. 设置存储桶为公开访问

为了让用户能够访问上传的图片，需要设置存储桶为公开访问：

1. 在存储桶页面，点击 **设置** 标签
2. 滚动到 **公开访问** 部分
3. 点击 **创建域预览** 或 **添加自定义域**

#### 选项 A：使用 R2 公开 URL（简单）
点击 **创建域预览**，Cloudflare 会提供一个公开 URL：
```
https://pub-<account-id>.r2.dev/<object-name>
```

#### 选项 B：使用自定义域名（推荐）
1. 点击 **添加自定义域**
2. 输入你的子域名（例如：`img.yourdomain.com`）
3. 按照提示添加 DNS 记录
4. 等待 SSL 证书自动配置完成

### 3. 创建 API Token

1. 在 Cloudflare Dashboard 中，点击右上角的用户头像
2. 选择 **我的个人资料** > **API 令牌**
3. 滚动到 **R2 API 令牌** 部分
4. 点击 **创建 API 令牌**
5. 或者手动创建：点击 **创建令牌**，选择 **编辑 Cloudflare R2** 模板
6. 设置权限：
   - **账户** -> **R2** -> **编辑**
7. 点击 **继续以显示摘要**，然后 **创建令牌**
8. **重要**：复制并保存以下信息（只显示一次）：
   - **Account ID**（在 URL 中可以看到：`https://dash.cloudflare.com/<account-id>/r2`）
   - **Access Key ID**
   - **Secret Access Key**

### 4. 配置环境变量

在 Render 中配置以下环境变量：

#### 方式 A：通过 Render Dashboard

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 选择你的 Web Service
3. 点击 **Environment** 标签
4. 添加以下环境变量：

| 环境变量 | 值 | 说明 |
|---------|-----|-----|
| `R2_ACCOUNT_ID` | 你的 Cloudflare Account ID | 在 URL 中可以找到 |
| `R2_ACCESS_KEY` | 你的 Access Key ID | R2 API Token |
| `R2_SECRET_KEY` | 你的 Secret Access Key | R2 API Token |
| `R2_BUCKET_NAME` | 你的存储桶名称 | 例如：`my-blog-images` |
| `R2_PUBLIC_DOMAIN` | 你的自定义域名（可选） | 例如：`img.yourdomain.com` |

如果使用 R2 公开 URL（选项 A），可以不设置 `R2_PUBLIC_DOMAIN`。

#### 方式 B：通过 render.yaml

在 `render.yaml` 中添加环境变量：

```yaml
services:
  - type: web
    name: my-blog
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: R2_ACCOUNT_ID
        value: your-account-id
      - key: R2_ACCESS_KEY
        value: your-access-key
      - key: R2_SECRET_KEY
        value: your-secret-key
      - key: R2_BUCKET_NAME
        value: my-blog-images
      - key: R2_PUBLIC_DOMAIN
        value: img.yourdomain.com  # 可选
```

**注意**：不要在 render.yaml 中硬编码敏感信息，建议使用 Render Dashboard 配置。

## 本地开发配置

创建 `.env` 文件（记得添加到 `.gitignore`）：

```bash
# R2 存储配置（可选，不配置则使用本地存储）
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
R2_BUCKET_NAME=my-blog-images
R2_PUBLIC_DOMAIN=img.yourdomain.com  # 可选
```

## 验证配置

部署后，检查日志确认 R2 存储已启用：

```
使用 Cloudflare R2 存储
```

如果看到：
```
使用本地存储: /app/app/static/uploads/covers
```

说明环境变量未正确配置，仍在使用本地存储。

## 迁移现有图片

如果你之前已经上传了一些图片到 Render 的临时存储，可以使用以下脚本迁移到 R2：

```python
# migrate_to_r2.py
import os
from app import create_app, db
from app.models.post import Post
from app.utils.storage import get_storage

app = create_app()

with app.app_context():
    storage = get_storage()

    # 获取所有有封面图的文章
    posts = Post.query.filter(Post.cover_image.isnot(None)).all()

    for post in posts:
        if post.cover_image.startswith('/static/uploads/'):
            # 这是本地存储的图片
            old_path = post.cover_image

            # 提取文件名
            filename = old_path.split('/')[-1]

            # 本地文件路径
            local_path = os.path.join('app/static/uploads/covers', filename)

            if os.path.exists(local_path):
                # 上传到 R2
                object_name = f'covers/{filename}'
                if storage.upload_file(local_path, object_name):
                    # 更新数据库
                    post.cover_image = storage.get_url(object_name)
                    print(f'已迁移: {filename}')
                else:
                    print(f'迁移失败: {filename}')

    db.session.commit()
    print('迁移完成！')
```

## 常见问题

### 1. 图片返回 404 错误

**原因**：存储桶未设置为公开访问

**解决**：按照步骤 2 设置存储桶为公开访问

### 2. 环境变量配置后仍使用本地存储

**原因**：环境变量未正确加载或服务未重启

**解决**：
1. 确认所有必需的环境变量都已设置
2. 在 Render 中触发重新部署
3. 检查日志确认存储类型

### 3. 上传失败

**原因**：API Token 权限不足或已过期

**解决**：
1. 检查 API Token 是否有 R2 编辑权限
2. 重新创建 API Token
3. 更新环境变量中的密钥

## 成本估算

对于小型博客（每月 1000 张图片，平均 500KB）：

- **存储**：1000 × 500KB = 500MB/月 < 10GB 免费额度
- **操作**：约 2000 次操作/月 < 1000 万次免费额度
- **流量**：假设每月 1 万次访问，500MB 流量 = **完全免费**

## 其他存储选项

如果你不想使用 Cloudflare R2，还有以下选择：

### AWS S3
- 免费额度：5GB 存储、2 万次请求/月
- 缺点：出站流量收费较高

### 阿里云 OSS
- 免费额度：5GB 存储、部分流量免费
- 优点：国内访问速度快

### MinIO（自托管）
- 完全免费，但需要自己部署服务器
- 适合有服务器的用户

## 技术支持

如有问题，请查看：
- [Cloudflare R2 文档](https://developers.cloudflare.com/r2/)
- [boto3 文档](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
