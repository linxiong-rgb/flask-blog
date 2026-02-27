"""
安全工具模块

该模块提供安全相关的功能：
- 登录失败限制
- IP 封禁
- 请求限流
"""

import time
from functools import wraps
from flask import session, request, abort
from datetime import datetime, timedelta


# 存储登录失败尝试的字典 (生产环境应使用 Redis)
login_attempts = {}
blocked_ips = {}


def get_client_ip():
    """获取客户端 IP 地址"""
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr


def is_ip_blocked(ip):
    """检查 IP 是否被封禁"""
    if ip in blocked_ips:
        block_info = blocked_ips[ip]
        # 检查封禁时间是否已过期
        if datetime.now() > block_info['expire_time']:
            del blocked_ips[ip]
            return False
        return True
    return False


def get_remaining_block_time(ip):
    """获取剩余封禁时间（秒）"""
    if ip in blocked_ips:
        remaining = blocked_ips[ip]['expire_time'] - datetime.now()
        return max(0, int(remaining.total_seconds()))
    return 0


def record_login_attempt(ip, success=False):
    """
    记录登录尝试

    Args:
        ip: 客户端 IP
        success: 登录是否成功
    """
    if success:
        # 登录成功，清除失败记录
        if ip in login_attempts:
            del login_attempts[ip]
    else:
        # 记录失败尝试
        if ip not in login_attempts:
            login_attempts[ip] = {'count': 1, 'last_attempt': datetime.now()}
        else:
            login_attempts[ip]['count'] += 1
            login_attempts[ip]['last_attempt'] = datetime.now()

            # 检查是否需要封禁 IP
            if login_attempts[ip]['count'] >= 5:
                # 封禁 30 分钟
                blocked_ips[ip] = {
                    'expire_time': datetime.now() + timedelta(minutes=30)
                }


def check_login_attempts(ip):
    """
    检查登录尝试次数

    Args:
        ip: 客户端 IP

    Returns:
        tuple: (是否允许登录, 剩余尝试次数/封禁时间)
    """
    # 检查 IP 是否被封禁
    if is_ip_blocked(ip):
        return False, {'blocked': True, 'seconds': get_remaining_block_time(ip)}

    # 检查失败次数
    if ip in login_attempts:
        attempts = login_attempts[ip]['count']
        if attempts >= 5:
            # 超过最大尝试次数，封禁 IP
            blocked_ips[ip] = {
                'expire_time': datetime.now() + timedelta(minutes=30)
            }
            return False, {'blocked': True, 'seconds': 1800}
        else:
            remaining = 5 - attempts
            return True, {'remaining': remaining}

    return True, {'remaining': 5}


def login_rate_limit(f):
    """
    登录速率限制装饰器

    限制每个 IP 的登录尝试次数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = get_client_ip()
        allowed, info = check_login_attempts(ip)

        if not allowed:
            if info.get('blocked'):
                abort(429, description=f'登录尝试次数过多，请在 {info["seconds"] // 60} 分钟后重试')
            else:
                abort(429, description='登录尝试次数过多')

        return f(*args, **kwargs)
    return decorated_function


def clear_login_attempts(ip):
    """清除指定 IP 的登录失败记录"""
    if ip in login_attempts:
        del login_attempts[ip]
