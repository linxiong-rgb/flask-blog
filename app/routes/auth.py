"""
用户认证路由模块

该模块处理用户注册、登录和登出功能：
- 用户注册（用户名和邮箱唯一性检查）
- 用户登录（带重定向支持）
- 用户登出
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册路由

    处理新用户注册：
    - GET: 显示注册表单
    - POST: 处理注册请求
    - 检查用户名和邮箱唯一性
    - 使用 werkzeug 安全哈希存储密码

    Returns:
        str: 渲染后的注册页面HTML或重定向
    """
    # 如果已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return render_template('auth/register.html')

        # 检查邮箱是否已被注册
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册')
            return render_template('auth/register.html')

        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('注册成功，请登录')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录路由

    处理用户登录：
    - GET: 显示登录表单
    - POST: 验证用户名和密码
    - 支持 next 参数重定向

    Query Parameters:
        next: 登录成功后重定向的URL

    Returns:
        str: 渲染后的登录页面HTML或重定向
    """
    # 如果已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        # 验证用户名和密码
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误')

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """
    用户登出路由

    清除用户会话并重定向到首页

    Returns:
        str: 重定向到首页
    """
    logout_user()
    return redirect(url_for('main.index'))
