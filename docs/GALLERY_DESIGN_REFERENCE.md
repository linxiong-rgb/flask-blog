# 云相册功能设计参考文档

> 此文档记录了原始相册功能的设计架构，作为重新设计的参考。

## 一、功能架构

### 1.1 数据模型

#### Album（相册模型）
```python
class Album(db.Model):
    id: int                          # 相册唯一标识
    name: str(100)                   # 相册名称
    description: str(500)            # 相册描述
    user_id: int                     # 所属用户ID
    parent_id: int                   # 父相册ID（支持多级目录）
    cover_photo_id: int              # 封面图片ID
    is_private: bool                 # 是否私密（默认True）
    is_public: bool                  # 是否在共享空间显示
    access_password: str(100)        # 相册访问密码
    sort_order: int                  # 排序顺序
    created_at: datetime             # 创建时间
    updated_at: datetime             # 更新时间
```

#### Photo（图片模型）
```python
class Photo(db.Model):
    id: int                          # 图片唯一标识
    filename: str(255)               # 原始文件名
    file_path: str(500)              # 存储路径
    file_size: int                   # 文件大小（字节）
    width: int                       # 图片宽度
    height: int                      # 图片高度
    mime_type: str(50)               # MIME类型
    thumbnail_path: str(500)         # 缩略图路径
    album_id: int                    # 所属相册ID
    user_id: int                     # 上传用户ID
    title: str(200)                  # 图片标题
    description: text                # 图片描述
    exif_data: JSON                  # EXIF信息
    is_public: bool                  # 是否公开
    access_password: str(100)        # 访问密码
    views: int                       # 浏览次数
    likes: int                       # 点赞次数
    created_at: datetime             # 上传时间
    taken_at: datetime               # 拍摄时间
```

#### PhotoShare（分享模型）
```python
class PhotoShare(db.Model):
    id: int                          # 分享唯一标识
    share_token: str(64)             # 分享令牌
    photo_id: int                    # 图片ID
    user_id: int                     # 创建用户ID
    expires_at: datetime             # 过期时间
    access_password: str(100)        # 访问密码
    access_count: int                # 访问次数
    max_access: int                  # 最大访问次数
    is_active: bool                  # 是否有效
```

### 1.2 路由结构

| 路由 | 方法 | 功能 |
|------|------|------|
| `/gallery/` | GET | 相册首页（显示所有相册） |
| `/gallery/album/new` | GET/POST | 创建新相册 |
| `/gallery/album/<id>` | GET | 查看相册详情 |
| `/gallery/album/<id>/edit` | GET/POST | 编辑相册 |
| `/gallery/album/<id>/delete` | POST | 删除相册 |
| `/gallery/album/<id>/upload` | POST | 上传图片 |
| `/gallery/photo/<id>/delete` | POST | 删除图片 |
| `/gallery/photo/<id>/move` | POST | 移动图片 |
| `/gallery/photo/<id>/toggle-public` | POST | 切换图片公开状态 |
| `/gallery/photo/<id>/public` | POST | 设置图片公开状态 |
| `/gallery/photo/<id>/edit-info` | POST | 编辑图片信息 |
| `/gallery/photo/<id>/share` | POST | 创建分享链接 |
| `/gallery/shared` | GET | 共享空间 |
| `/gallery/batch/move` | POST | 批量移动 |
| `/gallery/batch/delete` | POST | 批量删除 |
| `/gallery/batch/share` | POST | 批量设置公开/私密 |

## 二、核心功能

### 2.1 相册管理
- 创建、编辑、删除相册
- 多级目录支持（parent_id）
- 相册排序
- 封面图片设置

### 2.2 图片管理
- 单张/批量上传
- 图片编辑（标题、描述）
- 图片删除
- 图片移动到其他相册
- 缩略图生成（small: 200x200, medium: 400x400, large: 1200x900）

### 2.3 权限控制
- 私密相册：仅所有者访问
- 公开相册：所有用户可访问
- 密码保护：需要密码才能访问
- 超级管理员：可管理所有相册

### 2.4 分享功能
- 图片公开/私密切换
- 相册公开/私密切换
- 访问密码设置
- 临时分享链接（带过期时间）
- 分享链接访问统计

### 2.5 批量操作
- 批量选择图片
- 批量删除
- 批量设置公开/私密
- 批量移动

### 2.6 存储支持
- 本地文件系统存储
- GitHub 仓库作为图床
- CDN镜像支持（jsDelivr）
- 自动故障转移

## 三、UI设计

### 3.1 相册列表页
```
┌─────────────────────────────────────────────────────┐
│  云相册                        [共享空间] [新建相册]  │
├─────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │ 📁 相册  │  │ 🖼️ 照片  │  │ ⬆️ 上传  │              │
│  │   12    │  │   345   │  │         │              │
│  └─────────┘  └─────────┘  └─────────┘              │
├─────────────────────────────────────────────────────┤
│  相册列表                                          │
│  📁 我的相册 (12张)         [🔒] [✏️]               │
│  📁 旅行照片 (56张)         [🌐] [✏️]               │
│  📁 家庭聚会 (23张)         [🔒] [✏️]               │
└─────────────────────────────────────────────────────┘
```

### 3.2 相册详情页
```
┌─────────────────────────────────────────────────────┐
│  云相册 > 我的相册                                  │
│  我的相册                              [🌐私密] [上传] │
│  34张照片                                          │
├─────────────────────────────────────────────────────┤
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐          │
│  │ [图片] │ │ [图片] │ │ [图片] │ │ [图片] │          │
│  │  ✓    │ │       │ │  🌐  │ │       │          │
│  └───────┘ └───────┘ └───────┘ └───────┘          │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐          │
│  │ [图片] │ │ [图片] │ │ [图片] │ │ [图片] │          │
│  └───────┘ └───────┘ └───────┘ └───────┘          │
└─────────────────────────────────────────────────────┘
```

### 3.3 图片灯箱
```
┌─────────────────────────────────────────────────────┐
│                                              [✕]     │
│                                       ┌─────────┐   │
│                                    [←] │  图片   │ [→] │
│                                       └─────────┘   │
│                                           图片标题    │
└─────────────────────────────────────────────────────┘
```

## 四、技术栈

- **后端**: Flask + SQLAlchemy
- **前端**: Bootstrap 5 + Bootstrap Icons
- **图片处理**: Pillow (PIL)
- **存储**: 本地文件系统 / GitHub API
- **CDN**: jsDelivr

## 五、已知问题

1. 代码量大（1357行路由代码），维护复杂
2. 异常处理可能隐藏真实错误
3. 模板中JS代码较多，可能存在兼容性问题
4. 数据库迁移依赖手动执行脚本
