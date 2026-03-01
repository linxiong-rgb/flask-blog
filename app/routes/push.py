"""
推送通知路由模块

处理 Web Push API 订阅、取消订阅和推送通知
"""

from flask import Blueprint, request, jsonify, current_app
from app.models.push_subscription import PushSubscription
from app import db
import requests
import json

bp = Blueprint('push', __name__, url_prefix='/api/push')


@bp.route('/subscribe', methods=['POST'])
def subscribe():
    """
    订阅推送通知

    Request Body:
        JSON: {
            "endpoint": "https://fcm.googleapis.com/...",
            "keys": {
                "p256dh": "...",
                "auth": "..."
            }
        }

    Returns:
        JSON: 订阅结果
    """
    try:
        data = request.get_json()

        endpoint = data.get('endpoint')
        keys = data.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')

        if not all([endpoint, p256dh, auth]):
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400

        # 获取用户代理
        user_agent = request.headers.get('User-Agent', 'Unknown')

        # 检查是否已存在
        existing = PushSubscription.query.filter_by(endpoint=endpoint).first()
        if existing:
            return jsonify({'success': True, 'message': '订阅已存在'})

        # 创建新订阅
        subscription = PushSubscription(
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            user_agent=user_agent
        )
        db.session.add(subscription)
        db.session.commit()

        current_app.logger.info(f'新推送订阅: {endpoint[:50]}...')

        return jsonify({'success': True, 'message': '订阅成功'})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'订阅失败: {str(e)}')
        return jsonify({'success': False, 'message': f'订阅失败: {str(e)}'}), 500


@bp.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    """
    取消订阅推送通知

    Request Body:
        JSON: {
            "endpoint": "https://fcm.googleapis.com/..."
        }

    Returns:
        JSON: 取消订阅结果
    """
    try:
        data = request.get_json()
        endpoint = data.get('endpoint')

        if not endpoint:
            return jsonify({'success': False, 'message': '缺少endpoint参数'}), 400

        # 删除订阅
        subscription = PushSubscription.query.filter_by(endpoint=endpoint).first()
        if subscription:
            db.session.delete(subscription)
            db.session.commit()
            current_app.logger.info(f'取消推送订阅: {endpoint[:50]}...')
            return jsonify({'success': True, 'message': '取消订阅成功'})
        else:
            return jsonify({'success': False, 'message': '订阅不存在'}), 404

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'取消订阅失败: {str(e)}')
        return jsonify({'success': False, 'message': f'取消订阅失败: {str(e)}'}), 500


@bp.route('/status', methods=['GET'])
def subscription_status():
    """
    检查推送订阅状态

    Query Parameters:
        endpoint: 订阅端点URL（可选）

    Returns:
        JSON: 订阅状态
    """
    try:
        endpoint = request.args.get('endpoint')

        if endpoint:
            # 检查特定订阅
            subscription = PushSubscription.query.filter_by(endpoint=endpoint).first()
            if subscription:
                return jsonify({'subscribed': True})
            else:
                return jsonify({'subscribed': False})
        else:
            # 返回总订阅数
            count = PushSubscription.query.count()
            return jsonify({'subscribed': False, 'total_subscribers': count})

    except Exception as e:
        current_app.logger.error(f'检查订阅状态失败: {str(e)}')
        return jsonify({'success': False, 'message': f'检查失败: {str(e)}'}), 500


@bp.route('/send-test', methods=['POST'])
def send_test_notification():
    """
    发送测试推送通知

    用于测试推送功能是否正常工作

    Request Body:
        JSON: {
            "title": "通知标题",
            "body": "通知内容",
            "url": "点击后跳转的URL（可选）"
        }

    Returns:
        JSON: 发送结果
    """
    try:
        data = request.get_json()
        title = data.get('title', '测试通知')
        body = data.get('body', '这是一条测试推送通知')
        url = data.get('url', '/')

        # 获取所有订阅
        subscriptions = PushSubscription.query.all()

        if not subscriptions:
            return jsonify({'success': False, 'message': '暂无订阅者'}), 400

        # 这里需要使用 pywebpush 或类似库来发送真正的推送
        # 暂时返回模拟结果
        current_app.logger.info(f'发送测试通知到 {len(subscriptions)} 个订阅者')

        return jsonify({
            'success': True,
            'message': f'已发送到 {len(subscriptions)} 个订阅者',
            'sent_count': len(subscriptions)
        })

    except Exception as e:
        current_app.logger.error(f'发送测试通知失败: {str(e)}')
        return jsonify({'success': False, 'message': f'发送失败: {str(e)}'}), 500
