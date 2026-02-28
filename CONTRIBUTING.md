<div align="center">

# 贡献指南

**感谢你对 Flask Blog 项目的关注！**

我们欢迎任何形式的贡献，包括但不限于：报告问题、提交代码、改进文档、分享想法。

</div>

---

## 目录

- [如何贡献](#如何贡献)
- [报告问题](#报告问题)
- [提交代码](#提交代码)
- [代码规范](#代码规范)
- [开发环境设置](#开发环境设置)
- [测试指南](#测试指南)
- [提交 Pull Request](#提交-pull-request)
- [代码审查流程](#代码审查流程)

---

## 如何贡献

### 贡献类型

我们欢迎以下类型的贡献：

- **Bug 报告** - 发现并报告问题
- **功能建议** - 提出新功能或改进建议
- **代码贡献** - 修复 Bug 或实现新功能
- **文档改进** - 完善项目文档
- **代码审查** - 帮助审查他人的 PR
- **测试** - 编写和运行测试
- **分享** - 向他人推荐本项目

---

## 报告问题

### 报告 Bug

如果你发现了 bug：

1. 在 [Issues](https://github.com/linxiong-rgb/flask-blog/issues) 页面搜索是否已有类似问题
2. 如果没有，创建新 Issue，使用 "Bug" 标签
3. 详细描述问题：
   - **标题**：简洁描述问题
   - **环境信息**：
     - Python 版本
     - 操作系统
     - 浏览器（如果是前端问题）
   - **复现步骤**：
     1. 步骤一...
     2. 步骤二...
     3. 步骤三...
   - **预期行为**：应该发生什么
   - **实际行为**：实际发生了什么
   - **截图/日志**：如果适用，提供截图或错误日志
   - **补充信息**：其他相关信息

### 功能建议

如果你有功能建议：

1. 在 [Issues](https://github.com/linxiong-rgb/flask-blog/issues) 搜索是否已有类似建议
2. 如果没有，创建新 Issue，使用 "Enhancement" 标签
3. 详细说明：
   - **功能描述**：你希望实现什么功能
   - **使用场景**：这个功能解决什么问题
   - **实现建议**（可选）：你希望如何实现
   - **替代方案**（可选）：是否有其他方式解决

---

## 提交代码

### 1. Fork 仓库

点击 GitHub 页面右上角的 Fork 按钮，将项目 Fork 到你的账号下。

### 2. 克隆你的 Fork

```bash
git clone https://github.com/你的用户名/flask-blog.git
cd flask-blog
```

### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/linxiong-rgb/flask-blog.git
```

### 4. 创建特性分支

```bash
# 更新主分支
git fetch upstream
git checkout main
git merge upstream/main

# 创建新分支
git checkout -b feature/你的特性名称
# 或修复 bug
git checkout -b fix/问题描述
# 或文档更新
git checkout -b docs/文档说明
```

**分支命名规范**：
- `feature/` - 新功能
- `fix/` - Bug 修复
- `docs/` - 文档更新
- `refactor/` - 代码重构
- `test/` - 测试相关
- `style/` - 代码格式调整

### 5. 进行修改

#### 遵循代码规范

- Python 代码遵循 PEP 8 规范
- 使用有意义的变量名和函数名
- 添加必要的注释和文档字符串
- 保持代码简洁清晰

#### 修改文件

- 编辑相关文件
- 添加必要的测试
- 更新相关文档
- 确保代码通过所有测试

### 6. 提交修改

```bash
git add .
git commit -m "类型: 简短描述"
```

**提交信息规范**：

```
<类型>: <简短描述>

<详细描述>

<关联的 Issue>
```

**类型示例**：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**：
```
feat: 添加图片懒加载功能

实现了文章内容的图片懒加载，
提升页面加载速度和用户体验。

- 添加 IntersectionObserver 监听
- 优化图片加载动画
- 添加加载占位符

Closes #123
```

### 7. 推送到你的 Fork

```bash
git push origin feature/你的特性名称
```

### 8. 创建 Pull Request

1. 访问你 Fork 的 GitHub 页面
2. 点击 "Compare & pull request"
3. 填写 PR 信息：
   - **标题**：简洁描述修改内容
   - **内容**：
     - 修改说明
     - 修改原因
     - 测试情况
     - 关联的 Issue（如适用）
4. 提交 PR

---

## 代码规范

### Python 代码风格

#### 基本规范

- 遵循 [PEP 8](https://pep8.org/) 规范
- 使用 4 个空格缩进
- 每行最多 79 个字符
- 使用有意义的命名

#### 命名规范

```python
# 类名：大驼峰
class UserPost:
    pass

# 函数和变量：小写+下划线
def get_user_posts():
    user_id = 1
    return user_id

# 常量：大写+下划线
MAX_POSTS_PER_PAGE = 10
```

#### 文档字符串

```python
def create_post(title, content, author_id):
    """
    创建新文章

    Args:
        title (str): 文章标题
        content (str): 文章内容
        author_id (int): 作者ID

    Returns:
        Post: 创建的文章对象

    Raises:
        ValueError: 如果标题或内容为空
    """
    if not title or not content:
        raise ValueError("标题和内容不能为空")
    # 实现代码...
```

#### 注释

```python
# 单行注释：解释为什么这样做，而不是做了什么

# 好的注释
# 使用 UUID 避免文件名冲突
filename = f"cover_{uuid.uuid4().hex[:12]}.png"

# 不好的注释
# 设置文件名
filename = f"cover_{uuid.uuid4().hex[:12]}.png"

# 复杂逻辑的解释
if (user.is_admin and user.has_permission) or post.author_id == user.id:
    # 管理员或有权限的用户可以编辑文章
    pass
```

### JavaScript 代码风格

- 使用 ES6+ 语法
- 使用 const/let，避免 var
- 函数使用驼峰命名
- 事件处理器使用 on 前缀

```javascript
// 好的写法
const handleSearch = (event) => {
    const query = event.target.value;
    performSearch(query);
};

// 避免全局变量
(function() {
    'use strict';
    // 你的代码
})();
```

### CSS 代码风格

- 使用 BEM 命名规范（可选）
- 使用 CSS 变量
- 移动优先响应式设计

```css
/* 使用 CSS 变量 */
:root {
    --primary-color: #667eea;
    --text-color: #2d3748;
}

/* BEM 命名 */
.search-form { }
.search-form__input { }
.search-form__button { }
.search-form--dark { }
```

---

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/linxiong-rgb/flask-blog.git
cd flask-blog
```

### 2. 创建虚拟环境

```bash
# Python 3
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt

# 可选：安装开发依赖
pip install -r requirements-dev.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置必要的环境变量
```

### 5. 初始化数据库

```bash
python reset_database.py
```

### 6. 运行应用

```bash
python run.py
```

访问 http://localhost:5000

### 7. 运行测试（如果有）

```bash
pytest
```

---

## 测试指南

### 本地测试清单

在提交 PR 前，请确保：

- [ ] 代码本地运行正常
- [ ] 没有语法错误
- [ ] 遵循代码规范
- [ ] 添加了必要的注释
- [ ] 更新了相关文档
- [ ] 通过了所有测试

### 功能测试

#### 基本功能

- [ ] 用户注册和登录
- [ ] 创建和编辑文章
- [ ] 上传封面图
- [ ] Markdown 渲染
- [ ] 搜索功能
- [ ] 夜间模式切换

#### 图片功能

- [ ] 封面图自动生成
- [ ] 重新生成封面
- [ ] 图片上传
- [ ] 图片懒加载
- [ ] 图片查看

#### 管理功能

- [ ] 文章管理（CRUD）
- [ ] 分类和标签管理
- [ ] Markdown 文件导入
- [ ] 数据导出

### 浏览器测试

建议在以下浏览器测试：

- [ ] Chrome/Edge（最新版）
- [ ] Firefox（最新版）
- [ ] Safari（如果可用）
- [ ] 移动浏览器

---

## 提交 Pull Request

### PR 标题格式

使用以下格式：

```
类型: 简短描述
```

示例：
- `feat: 添加图片懒加载功能`
- `fix: 修复夜间模式下导航栏样式问题`
- `docs: 更新部署文档`

### PR 描述模板

```markdown
## 修改说明

简要描述你的修改内容。

## 修改原因

说明为什么需要这个修改。

## 改动内容

- 改动点1
- 改动点2
- 改动点3

## 测试情况

描述你如何测试这个修改：
- 测试环境
- 测试步骤
- 测试结果

## 截图（如果适用）

添加相关的截图。

## 关联 Issue

Closes #123
Related to #456
```

### PR 注意事项

1. **保持 PR 简洁**：一个 PR 只做一件事
2. **及时响应**：关注 PR 的审查意见
3. **保持更新**：及时同步上游代码
4. **关闭 Issue**：PR 合并后，在描述中关联的 Issue 会自动关闭

---

## 代码审查流程

### 审查者视角

当审查他人的 PR 时：

1. **检查代码质量**
   - 是否遵循代码规范
   - 是否有充分的测试
   - 是否有必要的注释

2. **检查功能正确性**
   - 是否实现了预期功能
   - 是否有边界情况处理
   - 是否有安全考虑

3. **提供反馈**
   - 具体指出问题
   - 提供改进建议
   - 保持友善和专业

### 贡献者视角

当你的 PR 被审查时：

1. **积极回应**
   - 感谢审查者的时间
   - 解释你的实现思路
   - 接受合理的建议

2. **及时修改**
   - 根据反馈更新代码
   - 标记已完成的修改
   - 提出疑问时说明原因

3. **保持沟通**
   - 遇到问题及时讨论
   - 寻求帮助时说明情况
   - 保持开放的心态

---

## 优秀贡献者

我们会在项目的 README 中特别感谢那些做出杰出贡献的开发者。

成为优秀贡献者的标准：

- 提交多个高质量的 PR
- 积极帮助审查代码
- 及时响应 Issue
- 帮助完善文档
- 帮助其他开发者

---

## 行为准则

### 我们的承诺

为了营造开放和友好的环境，我们承诺：

- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

以下行为是不可接受的：

- 使用性别化语言或图像
- 人身攻击或侮辱性言论
- 公开或私下骚扰
- 未经许可发布他人私人信息
- 其他不专业或不恰当的行为

---

## 获取帮助

如果你在贡献过程中遇到问题：

1. **查看文档**：先查阅项目文档
2. **搜索 Issues**：查看是否有人遇到类似问题
3. **提问**：在 Issues 中提问，标记为 "question"
4. **联系维护者**：通过邮箱联系

---

## 许可证

贡献的代码将采用项目的 [MIT License](LICENSE)。

---

## 联系方式

- **邮箱**: 3497875641@qq.com
- **GitHub**: [@linxiong-rgb](https://github.com/linxiong-rgb)
- **Issues**: [GitHub Issues](https://github.com/linxiong-rgb/flask-blog/issues)

---

<div align="center">

**再次感谢你的贡献！**

每一个贡献，无论大小，都让这个项目变得更好。

</div>
