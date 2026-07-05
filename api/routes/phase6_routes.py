"""
Phase 6.3 - API Routes
REST endpoints for all Phase 6 services (ML, Integration, IDE Plugins)
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.codebase_learner import get_codebase_intelligence
from services.agent_finetuner import get_agent_finetuner
from services.predictive_analyzer import get_predictive_analyzer
from services.continuous_learner import get_continuous_learner
from services.github_integration import get_github_integration
from services.cicd_integration import get_cicd_integration
from services.git_hooks import get_git_hooks_manager
from services.ide_plugins import get_ide_plugin_manager

phase6_bp = Blueprint('phase6', __name__, url_prefix='/api/v1/phase6')


# ============ Codebase Learning Endpoints ============

@phase6_bp.route('/intelligence/patterns', methods=['GET'])
def get_patterns():
    """Get all extracted patterns"""
    intelligence = get_codebase_intelligence()
    patterns = [
        {
            'pattern_id': p.pattern_id,
            'name': p.name,
            'language': p.language,
            'type': p.pattern_type,
            'complexity': p.complexity,
            'occurrences': p.occurrences,
        }
        for p in intelligence.patterns.values()
    ]
    return jsonify({'patterns': patterns, 'total': len(patterns)})


@phase6_bp.route('/intelligence/patterns/<pattern_id>', methods=['GET'])
def get_pattern(pattern_id):
    """Get specific pattern details"""
    intelligence = get_codebase_intelligence()
    pattern = intelligence.patterns.get(pattern_id)
    
    if not pattern:
        return jsonify({'error': 'Pattern not found'}), 404
    
    return jsonify({
        'pattern_id': pattern.pattern_id,
        'name': pattern.name,
        'language': pattern.language,
        'type': pattern.pattern_type,
        'complexity': pattern.complexity,
        'occurrences': pattern.occurrences,
        'success_rate': intelligence._calculate_success_rate(pattern_id),
    })


@phase6_bp.route('/intelligence/semantic-search', methods=['POST'])
def semantic_search():
    """Search patterns semantically"""
    intelligence = get_codebase_intelligence()
    data = request.json

    query = data.get('query')
    language = data.get('language', 'python')
    limit = data.get('limit', 10)

    if not query:
        return jsonify({'error': 'Query required'}), 400

    try:
        results = intelligence.search_similar_patterns(query, language, limit)
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ Agent Fine-Tuning Endpoints ============

@phase6_bp.route('/agents/profiles', methods=['GET'])
def get_agent_profiles():
    """Get all agent profiles"""
    finetuner = get_agent_finetuner()
    profiles = [
        profile.to_dict()
        for profile in finetuner.agent_profiles.values()
    ]
    return jsonify({'agents': profiles, 'total': len(profiles)})


@phase6_bp.route('/agents/profiles', methods=['POST'])
def create_agent_profile():
    """Create new agent profile"""
    from services.agent_finetuner import AgentSpecialization

    finetuner = get_agent_finetuner()
    data = request.json

    agent_name = data.get('agent_name')
    specialization_str = data.get('specialization')
    language = data.get('language', 'python')

    if not agent_name or not specialization_str:
        return jsonify({'error': 'agent_name and specialization required'}), 400

    try:
        # Convert string to enum
        try:
            specialization = AgentSpecialization(specialization_str)
        except ValueError:
            return jsonify({'error': f'Invalid specialization: {specialization_str}'}), 400

        profile = finetuner.create_agent_profile(agent_name, specialization, language)
        return jsonify(profile.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@phase6_bp.route('/agents/<agent_name>/train', methods=['POST'])
def train_agent(agent_name):
    """Train agent on patterns"""
    finetuner = get_agent_finetuner()
    data = request.json
    
    language = data.get('language', 'python')
    
    result = finetuner.train_agent(agent_name, language)
    return jsonify(result)


@phase6_bp.route('/agents/<agent_name>/recommend', methods=['POST'])
def get_recommendation(agent_name):
    """Get personalized recommendation from agent"""
    finetuner = get_agent_finetuner()
    data = request.json
    
    pattern_id = data.get('pattern_id')
    original_code = data.get('original_code')
    language = data.get('language', 'python')
    
    if not pattern_id or not original_code:
        return jsonify({'error': 'pattern_id and original_code required'}), 400
    
    recommendation = finetuner.get_personalized_recommendation(
        agent_name, pattern_id, original_code, language
    )
    
    if not recommendation:
        return jsonify({'error': 'No recommendation available'}), 404
    
    return jsonify({
        'agent': agent_name,
        'pattern_id': pattern_id,
        'improvement_score': recommendation.improvement_score,
        'confidence': recommendation.confidence,
        'benefit_level': recommendation.benefit_level,
        'reasoning': recommendation.reasoning,
    })


@phase6_bp.route('/agents/<agent_name>/performance', methods=['GET'])
def get_agent_performance(agent_name):
    """Get agent performance metrics"""
    finetuner = get_agent_finetuner()
    performance = finetuner.get_agent_performance(agent_name)
    
    if not performance:
        return jsonify({'error': 'Agent not found'}), 404
    
    return jsonify(performance)


# ============ Predictive Analysis Endpoints ============

@phase6_bp.route('/predictions/quality/<pattern_id>', methods=['GET'])
def predict_quality(pattern_id):
    """Predict code quality improvement"""
    analyzer = get_predictive_analyzer()
    language = request.args.get('language', 'python')
    
    prediction = analyzer.predict_quality_improvement(pattern_id, language)
    
    if not prediction:
        return jsonify({'error': 'No prediction available'}), 404
    
    return jsonify({
        'pattern_id': pattern_id,
        'current_score': prediction.current_score,
        'predicted_score': prediction.predicted_score,
        'improvement_potential': prediction.improvement_potential,
        'confidence': prediction.confidence,
        'estimated_effort': prediction.estimated_effort,
        'roi_estimate': prediction.roi_estimate,
        'key_factors': prediction.key_factors,
    })


@phase6_bp.route('/predictions/risk/<pattern_id>', methods=['POST'])
def assess_risk(pattern_id):
    """Assess refactoring risk"""
    analyzer = get_predictive_analyzer()
    data = request.json
    
    refactored_code = data.get('refactored_code')
    if not refactored_code:
        return jsonify({'error': 'refactored_code required'}), 400
    
    assessment = analyzer.assess_refactoring_risk(pattern_id, refactored_code)
    
    if not assessment:
        return jsonify({'error': 'Pattern not found'}), 404
    
    return jsonify({
        'pattern_id': pattern_id,
        'risk_level': assessment.risk_level.value,
        'risk_score': assessment.risk_score,
        'breaking_risk': assessment.breaking_risk,
        'performance_risk': assessment.performance_risk,
        'compatibility_risk': assessment.compatibility_risk,
        'recommendations': assessment.recommendations,
        'mitigation_strategies': assessment.mitigation_strategies,
    })


@phase6_bp.route('/predictions/anomalies', methods=['GET'])
def detect_anomalies():
    """Detect anomalies in patterns"""
    analyzer = get_predictive_analyzer()
    language = request.args.get('language', 'python')
    
    anomalies = analyzer.detect_anomalies(language)
    
    return jsonify({
        'language': language,
        'anomalies': [
            {
                'anomaly_id': a.anomaly_id,
                'pattern_id': a.pattern_id,
                'type': a.anomaly_type.value,
                'severity': a.severity,
                'description': a.description,
                'confidence': a.confidence,
            }
            for a in anomalies
        ],
        'total': len(anomalies)
    })


@phase6_bp.route('/predictions/trends', methods=['GET'])
def analyze_trends():
    """Analyze trends over time"""
    analyzer = get_predictive_analyzer()
    language = request.args.get('language', 'python')
    
    trends = analyzer.analyze_trends(language)
    
    return jsonify({
        'language': language,
        'trends': [
            {
                'metric': t.metric_name,
                'current_value': t.current_value,
                'historical_average': t.historical_average,
                'direction': t.trend_direction,
                'strength': t.trend_strength,
                'forecast': t.forecast_next_period,
                'confidence': t.confidence,
            }
            for t in trends
        ]
    })


# ============ Continuous Learning Endpoints ============

@phase6_bp.route('/learning/experience', methods=['POST'])
def record_experience():
    """Record learning experience"""
    learner = get_continuous_learner()
    data = request.json
    
    required = ['pattern_id', 'original_code', 'refactored_code', 'agent_name', 'quality_improvement', 'language']
    if not all(k in data for k in required):
        return jsonify({'error': f'Required fields: {", ".join(required)}'}), 400
    
    experience = learner.record_experience(
        pattern_id=data['pattern_id'],
        original_code=data['original_code'],
        refactored_code=data['refactored_code'],
        agent_name=data['agent_name'],
        quality_improvement=data['quality_improvement'],
        language=data['language'],
        user_feedback=data.get('user_feedback'),
        auto_validation=data.get('auto_validation', False),
        metadata=data.get('metadata'),
    )
    
    return jsonify(experience.to_dict()), 201


@phase6_bp.route('/learning/metrics', methods=['GET'])
def get_learning_metrics():
    """Get learning metrics"""
    learner = get_continuous_learner()
    metrics = learner.get_learning_metrics()
    return jsonify(metrics)


@phase6_bp.route('/learning/report', methods=['GET'])
def get_learning_report():
    """Get continuous improvement report"""
    learner = get_continuous_learner()
    report = learner.get_continuous_improvement_report()
    return jsonify(report)


@phase6_bp.route('/learning/batches/<batch_id>/process', methods=['POST'])
def process_batch(batch_id):
    """Process learning batch"""
    learner = get_continuous_learner()
    result = learner.process_learning_batch(batch_id)
    return jsonify(result)


# ============ GitHub Integration Endpoints ============

@phase6_bp.route('/github/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook"""
    github = get_github_integration()
    data = request.json
    
    signature = request.headers.get('X-Hub-Signature-256')
    if not github.validate_webhook_signature(data, signature or ''):
        return jsonify({'error': 'Invalid signature'}), 401
    
    result = github.parse_webhook(data)
    return jsonify(result), 202


@phase6_bp.route('/github/pr/<int:pr_number>/analyze', methods=['POST'])
def analyze_pr(pr_number):
    """Analyze pull request"""
    github = get_github_integration()
    data = request.json
    
    repo = data.get('repo')
    if not repo:
        return jsonify({'error': 'repo required'}), 400
    
    result = github.analyze_pull_request(repo, pr_number)
    return jsonify(result)


@phase6_bp.route('/github/webhook-logs', methods=['GET'])
def get_webhook_logs():
    """Get webhook logs"""
    github = get_github_integration()
    limit = request.args.get('limit', 20, type=int)
    
    logs = github.get_webhook_logs(limit)
    return jsonify({'logs': logs, 'count': len(logs)})


# ============ CI/CD Integration Endpoints ============

@phase6_bp.route('/cicd/pipelines', methods=['GET'])
def list_pipelines():
    """List available pipelines"""
    cicd = get_cicd_integration()
    pipelines = cicd.get_pipeline_templates()
    
    return jsonify({
        'pipelines': [
            {
                'type': p,
                'template': cicd.generate_github_actions_workflow() if p == 'github_actions' else '',
            }
            for p in ['github_actions', 'gitlab_ci', 'jenkins']
        ]
    })


@phase6_bp.route('/cicd/pipelines/<pipeline_type>', methods=['GET'])
def get_pipeline_template(pipeline_type):
    """Get pipeline template"""
    cicd = get_cicd_integration()
    
    if pipeline_type == 'github_actions':
        template = cicd.generate_github_actions_workflow()
    elif pipeline_type == 'gitlab_ci':
        template = cicd.generate_gitlab_ci_pipeline()
    elif pipeline_type == 'jenkins':
        template = cicd.generate_jenkins_pipeline()
    else:
        return jsonify({'error': 'Unknown pipeline type'}), 400
    
    return jsonify({'type': pipeline_type, 'template': template})


@phase6_bp.route('/cicd/runs', methods=['GET'])
def get_pipeline_runs():
    """Get pipeline run history"""
    cicd = get_cicd_integration()
    runs = list(cicd.pipeline_runs.values())
    
    return jsonify({
        'runs': [r.to_dict() if hasattr(r, 'to_dict') else r for r in runs[-20:]],
        'total': len(runs)
    })


# ============ Git Hooks Endpoints ============

@phase6_bp.route('/hooks/config', methods=['POST'])
def configure_hook():
    """Configure git hook"""
    hooks = get_git_hooks_manager()
    data = request.json
    
    hook_type = data.get('hook_type')
    if not hook_type:
        return jsonify({'error': 'hook_type required'}), 400
    
    config = hooks.configure_hook(
        hook_type=hook_type,
        enabled=data.get('enabled', True),
        fail_on_error=data.get('fail_on_error', False),
        quality_threshold=data.get('quality_threshold', 70.0),
        auto_fix=data.get('auto_fix', False)
    )
    
    return jsonify(config.to_dict()), 201


@phase6_bp.route('/hooks/history', methods=['GET'])
def get_hooks_history():
    """Get hook execution history"""
    hooks = get_git_hooks_manager()
    hook_type = request.args.get('hook_type')
    limit = request.args.get('limit', 20, type=int)
    
    history = hooks.get_execution_history(hook_type=hook_type, limit=limit)
    
    return jsonify({
        'executions': [e.to_dict() for e in history],
        'total': len(history)
    })


@phase6_bp.route('/hooks/status', methods=['GET'])
def get_hooks_status():
    """Get overall hook status"""
    hooks = get_git_hooks_manager()
    status = hooks.get_hook_status()
    return jsonify(status)


# ============ IDE Plugin Endpoints ============

@phase6_bp.route('/plugins/register', methods=['POST'])
def register_plugin():
    """Register IDE plugin"""
    manager = get_ide_plugin_manager()
    data = request.json
    
    ide_type = data.get('ide_type')
    version = data.get('version')
    
    if not ide_type or not version:
        return jsonify({'error': 'ide_type and version required'}), 400
    
    try:
        session = manager.register_plugin(
            ide_type=ide_type,
            version=version,
            user_id=data.get('user_id'),
            project_path=data.get('project_path')
        )
        return jsonify(session.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@phase6_bp.route('/plugins/<session_id>/analyze', methods=['POST'])
def analyze_file(session_id):
    """Analyze file from IDE"""
    manager = get_ide_plugin_manager()
    data = request.json
    
    required = ['file_path', 'code', 'language']
    if not all(k in data for k in required):
        return jsonify({'error': f'Required: {", ".join(required)}'}), 400
    
    result = manager.analyze_file(
        session_id=session_id,
        file_path=data['file_path'],
        code=data['code'],
        language=data['language']
    )
    
    if not result:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(result.to_dict()), 201


@phase6_bp.route('/plugins/<session_id>/quick-feedback', methods=['POST'])
def quick_feedback(session_id):
    """Get quick feedback without full analysis"""
    manager = get_ide_plugin_manager()
    data = request.json
    
    required = ['file_path', 'code', 'language']
    if not all(k in data for k in required):
        return jsonify({'error': f'Required: {", ".join(required)}'}), 400
    
    feedback = manager.get_quick_feedback(
        session_id=session_id,
        file_path=data['file_path'],
        code=data['code'],
        language=data['language']
    )
    
    return jsonify(feedback)


@phase6_bp.route('/plugins/<session_id>/status', methods=['GET'])
def get_plugin_status(session_id):
    """Get plugin session status"""
    manager = get_ide_plugin_manager()
    status = manager.get_session_status(session_id)
    
    if not status:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(status)


@phase6_bp.route('/plugins/statistics', methods=['GET'])
def get_plugin_statistics():
    """Get plugin statistics"""
    manager = get_ide_plugin_manager()
    stats = manager.get_statistics()
    return jsonify(stats)


@phase6_bp.route('/plugins/<session_id>/heartbeat', methods=['POST'])
def plugin_heartbeat(session_id):
    """Update plugin heartbeat"""
    manager = get_ide_plugin_manager()
    success = manager.heartbeat(session_id)
    
    if not success:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({'status': 'ok'})


# ============ Health Check ============

@phase6_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for Phase 6 services"""
    return jsonify({
        'status': 'healthy',
        'version': '6.3.0',
        'services': {
            'codebase_learning': 'available',
            'agent_finetuning': 'available',
            'predictive_analysis': 'available',
            'continuous_learning': 'available',
            'github_integration': 'available',
            'cicd_integration': 'available',
            'git_hooks': 'available',
            'ide_plugins': 'available',
        }
    })
