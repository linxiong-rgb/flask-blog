"""
用户认证路由模块

该模块处理用户注册、登录和登出功能：
- 用户注册（用户名和邮箱唯一性检查）
- 用户登录（带重定向支持）
- 用户登出
- 登录失败限制
- 密码重置
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, current_user
from app.forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models.user import User
from app import db
from app.security import get_client_ip, record_login_attempt, login_rate_limit
import secrets
from datetime import datetime, timedelta

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

    form = RegisterForm()
    if form.validate_on_submit():
        # 创建新用户
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('注册成功，请登录')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
@login_rate_limit
def login():
    """
    用户登录路由

    处理用户登录：
    - GET: 显示登录表单
    - POST: 验证用户名和密码
    - 支持 next 参数重定向
    - 登录失败限制（5次失败后封禁30分钟）

    Query Parameters:
        next: 登录成功后重定向的URL

    Returns:
        str: 渲染后的登录页面HTML或重定向
    """
    # 如果已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    client_ip = get_client_ip()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # 验证用户名和密码
        if user and user.check_password(form.password.data):
            # 登录成功，清除失败记录
            record_login_attempt(client_ip, success=True)
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            # 登录失败，记录尝试
            record_login_attempt(client_ip, success=False)

            # 获取剩余尝试次数
            from app.security import check_login_attempts
            allowed, info = check_login_attempts(client_ip)
            if not allowed and info.get('remaining') is not None:
                flash(f'用户名或密码错误。剩余尝试次数：{info["remaining"]} 次')
            else:
                flash('用户名或密码错误')

    return render_template('auth/login.html', form=form)


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


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """
    密码重置请求路由

    处理密码重置请求：
    - GET: 显示密码重置请求表单
    - POST: 发送重置链接到邮箱

    Returns:
        str: 渲染后的页面HTML或重定向
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            # 生成重置令牌
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            # 在实际应用中，这里应该发送邮件
            # 为了演示，我们直接显示重置链接
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            app = current_app._get_current_object()
            app.logger.info(f'密码重置链接: {reset_url}')

            flash('密码重置链接已生成（开发环境）')
            return render_template('auth/reset_link.html', reset_url=reset_url)
        else:
            flash('如果该邮箱已注册，您将收到密码重置链接')

    return render_template('auth/reset_password_request.html', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    密码重置路由

    处理密码重置：
    - GET: 显示密码重置表单
    - POST: 更新用户密码

    Args:
        token: 重置令牌

    Returns:
        str: 渲染后的页面HTML或重定向
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(reset_token=token).first()

    if not user or user.reset_token_expires < datetime.utcnow():
        flash('重置链接无效或已过期，请重新申请')
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()

        flash('密码已重置，请使用新密码登录')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form, token=token)
