from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField(
        '用户名',
        validators=[DataRequired(message='请输入用户名')]
    )
    password = PasswordField(
        '密码',
        validators=[DataRequired(message='请输入密码')]
    )
    remember_me = BooleanField('记住我')


class RegisterForm(FlaskForm):
    """注册表单"""
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
        ]
    )
    email = StringField(
        '邮箱',
        validators=[
            DataRequired(message='请输入邮箱'),
            Email(message='请输入有效的邮箱地址')
        ]
    )
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='请输入密码'),
            Length(min=6, message='密码长度不能少于6个字符')
        ]
    )
    confirm_password = PasswordField(
        '确认密码',
        validators=[
            DataRequired(message='请确认密码'),
            EqualTo('password', message='两次输入的密码不一致')
        ]
    )

    def validate_username(self, field):
        """验证用户名是否已存在"""
        from app.models.user import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        """验证邮箱是否已注册"""
        from app.models.user import User
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')


class SearchForm(FlaskForm):
    """搜索表单"""
    q = StringField(
        '搜索关键词',
        validators=[
            DataRequired(message='请输入搜索关键词'),
            Length(min=1, max=100, message='搜索关键词长度必须在1-100个字符之间')
        ]
    )


class ResetPasswordRequestForm(FlaskForm):
    """密码重置请求表单"""
    email = StringField(
        '邮箱',
        validators=[
            DataRequired(message='请输入邮箱'),
            Email(message='请输入有效的邮箱地址')
        ]
    )

    def validate_email(self, field):
        """验证邮箱是否已注册"""
        from app.models.user import User
        user = User.query.filter_by(email=field.data).first()
        if not user:
            raise ValidationError('该邮箱未注册')


class ResetPasswordForm(FlaskForm):
    """密码重置表单"""
    password = PasswordField(
        '新密码',
        validators=[
            DataRequired(message='请输入新密码'),
            Length(min=6, message='密码长度不能少于6个字符')
        ]
    )
    confirm_password = PasswordField(
        '确认新密码',
        validators=[
            DataRequired(message='请确认新密码'),
            EqualTo('password', message='两次输入的密码不一致')
        ]
    )


class ContactForm(FlaskForm):
    """联系表单"""
    name = StringField(
        '您的称呼',
        validators=[
            DataRequired(message='请输入您的称呼'),
            Length(min=2, max=50, message='称呼长度必须在2-50个字符之间')
        ]
    )
    email = StringField(
        '邮箱',
        validators=[
            DataRequired(message='请输入邮箱'),
            Email(message='请输入有效的邮箱地址')
        ]
    )
    subject = StringField(
        '主题',
        validators=[
            DataRequired(message='请输入主题'),
            Length(min=2, max=100, message='主题长度必须在2-100个字符之间')
        ]
    )
    message = TextAreaField(
        '留言内容',
        validators=[
            DataRequired(message='请输入留言内容'),
            Length(min=10, max=1000, message='留言内容长度必须在10-1000个字符之间')
        ]
    )