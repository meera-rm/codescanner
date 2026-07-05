"""
Enterprise API Routes - Phase 6.4
API key management, subscriptions, rate limiting, audit logs
"""

from flask import Blueprint, request, jsonify
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.enterprise import get_enterprise_manager, PlanType, AuditAction

enterprise_bp = Blueprint('enterprise', __name__, url_prefix='/api/v1/enterprise')


# ============ API Key Management ============

@enterprise_bp.route('/keys', methods=['POST'])
def create_api_key():
    """Create new API key"""
    manager = get_enterprise_manager()
    data = request.json

    user_id = data.get('user_id')
    name = data.get('name')
    expires_in_days = data.get('expires_in_days')

    if not user_id or not name:
        return jsonify({'error': 'user_id and name required'}), 400

    try:
        raw_key, api_key = manager.create_api_key(
            user_id=user_id,
            name=name,
            expires_in_days=expires_in_days,
            permissions=data.get('permissions', ['read', 'write'])
        )

        return jsonify({
            'key': raw_key,
            'key_info': api_key.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@enterprise_bp.route('/keys', methods=['GET'])
def list_api_keys():
    """List user's API keys"""
    manager = get_enterprise_manager()
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    keys = manager.list_api_keys(user_id)

    return jsonify({
        'keys': [k.to_dict() for k in keys],
        'total': len(keys)
    })


@enterprise_bp.route('/keys/<key_id>/revoke', methods=['POST'])
def revoke_api_key(key_id):
    """Revoke API key"""
    manager = get_enterprise_manager()
    data = request.json

    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    success = manager.revoke_api_key(key_id, user_id)

    if not success:
        return jsonify({'error': 'Key not found or unauthorized'}), 404

    return jsonify({'status': 'revoked'})


# ============ Subscription Management ============

@enterprise_bp.route('/subscriptions', methods=['POST'])
def create_subscription():
    """Create subscription for user"""
    manager = get_enterprise_manager()
    data = request.json

    user_id = data.get('user_id')
    plan_type = data.get('plan_type')

    if not user_id or not plan_type:
        return jsonify({'error': 'user_id and plan_type required'}), 400

    try:
        plan = PlanType(plan_type)
        subscription = manager.create_subscription(user_id, plan)

        return jsonify(subscription.to_dict()), 201
    except ValueError:
        return jsonify({'error': f'Invalid plan_type: {plan_type}'}), 400


@enterprise_bp.route('/subscriptions/<user_id>', methods=['GET'])
def get_subscription(user_id):
    """Get user subscription"""
    manager = get_enterprise_manager()

    subscription = manager.get_subscription(user_id)

    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404

    return jsonify(subscription.to_dict())


@enterprise_bp.route('/subscriptions/<user_id>/upgrade', methods=['POST'])
def upgrade_plan(user_id):
    """Upgrade user plan"""
    manager = get_enterprise_manager()
    data = request.json

    new_plan = data.get('plan_type')
    if not new_plan:
        return jsonify({'error': 'plan_type required'}), 400

    try:
        plan = PlanType(new_plan)
        success = manager.upgrade_plan(user_id, plan)

        if not success:
            return jsonify({'error': 'Subscription not found'}), 404

        subscription = manager.get_subscription(user_id)
        return jsonify(subscription.to_dict())
    except ValueError:
        return jsonify({'error': f'Invalid plan_type: {new_plan}'}), 400


@enterprise_bp.route('/subscriptions/<user_id>/limits', methods=['GET'])
def get_plan_limits(user_id):
    """Get plan limits"""
    manager = get_enterprise_manager()

    limits = manager.get_plan_limits(user_id)

    return jsonify({
        'user_id': user_id,
        'limits': limits
    })


# ============ Usage Tracking ============

@enterprise_bp.route('/usage/<user_id>/metrics', methods=['GET'])
def get_usage_metrics(user_id):
    """Get usage metrics"""
    manager = get_enterprise_manager()

    metrics = manager.get_usage_metrics(user_id)

    if not metrics:
        return jsonify({'error': 'No metrics available'}), 404

    return jsonify(metrics.to_dict())


@enterprise_bp.route('/usage/<user_id>/track/api-call', methods=['POST'])
def track_api_call(user_id):
    """Track API call"""
    manager = get_enterprise_manager()

    success = manager.track_api_call(user_id)

    if not success:
        return jsonify({'error': 'Rate limit exceeded'}), 429

    return jsonify({'status': 'tracked'})


@enterprise_bp.route('/usage/<user_id>/track/analysis', methods=['POST'])
def track_analysis(user_id):
    """Track analysis run"""
    manager = get_enterprise_manager()
    data = request.json

    files_count = data.get('files_count', 0)
    patterns_count = data.get('patterns_count', 0)
    compute_seconds = data.get('compute_seconds', 0)

    success = manager.track_analysis(
        user_id=user_id,
        files_count=files_count,
        patterns_count=patterns_count,
        compute_seconds=compute_seconds
    )

    if not success:
        return jsonify({'error': 'Failed to track analysis'}), 400

    return jsonify({'status': 'tracked'})


# ============ Rate Limiting ============

@enterprise_bp.route('/rate-limits/<user_id>', methods=['GET'])
def get_rate_limit(user_id):
    """Get rate limit"""
    manager = get_enterprise_manager()

    rate_limit = manager.get_rate_limit(user_id)

    if not rate_limit:
        return jsonify({'error': 'Rate limit not found'}), 404

    return jsonify(rate_limit.to_dict())


# ============ Audit Logging ============

@enterprise_bp.route('/audit/<user_id>/logs', methods=['GET'])
def get_audit_logs(user_id):
    """Get audit logs"""
    manager = get_enterprise_manager()

    limit = request.args.get('limit', 100, type=int)
    action_filter = request.args.get('action')

    try:
        action = AuditAction(action_filter) if action_filter else None
    except ValueError:
        return jsonify({'error': f'Invalid action: {action_filter}'}), 400

    logs = manager.get_audit_logs(user_id, limit=limit, action_filter=action)

    return jsonify({
        'user_id': user_id,
        'logs': [log.to_dict() for log in logs],
        'total': len(logs)
    })


# ============ Authentication Middleware ============

@enterprise_bp.before_request
def check_api_key():
    """Check API key for authentication"""
    manager = get_enterprise_manager()

    api_key = request.headers.get('X-API-Key')

    if not api_key:
        # Skip for health check
        if request.endpoint == 'enterprise.health_check':
            return

        return jsonify({'error': 'API key required'}), 401

    result = manager.verify_api_key(api_key)

    if not result:
        return jsonify({'error': 'Invalid API key'}), 401

    # Store user_id in request context
    user_id, key_obj = result
    request.user_id = user_id
    request.api_key = key_obj


# ============ Health Check ============

@enterprise_bp.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'version': '6.4.0',
        'service': 'enterprise'
    })
