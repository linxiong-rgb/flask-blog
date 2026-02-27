# 贡献指南

感谢你对 Flask Blog 项目的关注！我们欢迎任何形式的贡献。

## 🤝 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 在 [Issues](https://github.com/linxiong-rgb/flask-blog/issues) 页面
2. 搜索是否已有类似问题
3. 创建新 Issue，详细描述：
   - 问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（Python 版本、操作系统等）

### 提交代码

#### 1. Fork 仓库

点击 GitHub 页面右上角的 Fork 按钮

#### 2. 克隆你的 Fork

```bash
git clone https://github.com/你的用户名/flask-blog.git
cd flask-blog
```

#### 3. 创建特性分支

```bash
git checkout -b feature/你的特性名称
# 或修复 bug
git checkout -b fix/问题描述
```

#### 4. 进行修改

- 遵循现有代码风格
- 添加必要的注释
- 更新相关文档

#### 5. 提交修改

```bash
git add .
git commit -m "描述你的修改"
```

#### 6. 推送到你的 Fork

```bash
git push origin feature/你的特性名称
```

#### 7. 创建 Pull Request

1. 访问你 Fork 的 GitHub 页面
2. 点击 "Compare & pull request"
3. 填写 PR 描述：
   - 标题：简洁描述修改内容
   - 内容：详细说明修改原因和内容
4. 提交 PR

---

## 📝 代码规范

### Python 代码风格

- 遵循 PEP 8 规范
- 使用有意义的变量名和函数名
- 添加必要的文档字符串

### Git 提交信息规范

```
<类型>: <简短描述>

<详细描述>

<关联的 Issue>
```

**类型示例：**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```
feat: 添加文章搜索功能

实现了基于标题和内容的关键词搜索，
支持实时建议和分类过滤。

Closes #123
```

---

## 🎨 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/linxiong-rgb/flask-blog.git
cd flask-blog
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python reset_database.py
```

### 5. 运行应用

```bash
python run.py
```

访问 http://localhost:5000

---

## 🧪 测试

在提交 PR 前，请确保：

- [ ] 代码本地运行正常
- [ ] 没有语法错误
- [ ] 遵循代码规范
- [ ] 添加了必要的注释
- [ ] 更新了相关文档

---

## 📧 联系方式

- **邮箱**: 3497875641@qq.com
- **GitHub**: [@linxiong-rgb](https://github.com/linxiong-rgb)

---

再次感谢你的贡献！🎉
