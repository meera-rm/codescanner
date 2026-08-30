"""
Tests for Phase 6.3 - API Routes
"""

import pytest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.routes.phase6_routes import phase6_bp
from flask import Flask


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.register_blueprint(phase6_bp)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestPhase6Routes:
    """Test Phase 6 API routes"""

    # ========== Codebase Learning Tests ==========

    def test_get_patterns(self, client):
        """Test getting patterns endpoint"""
        response = client.get('/api/v1/phase6/intelligence/patterns')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'patterns' in data
        assert 'total' in data

    def test_get_nonexistent_pattern(self, client):
        """Test getting nonexistent pattern"""
        response = client.get('/api/v1/phase6/intelligence/patterns/invalid_id')
        
        assert response.status_code == 404

    def test_semantic_search_no_query(self, client):
        """Test semantic search without query"""
        response = client.post(
            '/api/v1/phase6/intelligence/semantic-search',
            json={}
        )
        
        assert response.status_code == 400

    def test_semantic_search_with_query(self, client):
        """Test semantic search with query"""
        response = client.post(
            '/api/v1/phase6/intelligence/semantic-search',
            json={'query': 'function definition', 'language': 'python'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'query' in data
        assert 'results' in data

    # ========== Agent Fine-Tuning Tests ==========

    def test_get_agent_profiles(self, client):
        """Test getting agent profiles"""
        response = client.get('/api/v1/phase6/agents/profiles')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'agents' in data
        assert 'total' in data

    def test_create_agent_profile(self, client):
        """Test creating agent profile"""
        response = client.post(
            '/api/v1/phase6/agents/profiles',
            json={
                'agent_name': 'TestAgent',
                'specialization': 'security',
                'language': 'python'
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['agent_name'] == 'TestAgent'

    def test_create_agent_missing_fields(self, client):
        """Test creating agent without required fields"""
        response = client.post(
            '/api/v1/phase6/agents/profiles',
            json={'agent_name': 'TestAgent'}
        )
        
        assert response.status_code == 400

    def test_get_agent_performance(self, client):
        """Test getting agent performance"""
        # Create agent first
        client.post(
            '/api/v1/phase6/agents/profiles',
            json={
                'agent_name': 'PerfAgent',
                'specialization': 'performance',
                'language': 'python'
            }
        )
        
        response = client.get('/api/v1/phase6/agents/PerfAgent/performance')
        
        assert response.status_code == 200

    # ========== Predictive Analysis Tests ==========

    def test_predict_quality_no_pattern(self, client):
        """Test quality prediction with nonexistent pattern"""
        response = client.get(
            '/api/v1/phase6/predictions/quality/invalid_pattern',
            query_string={'language': 'python'}
        )
        
        assert response.status_code == 404

    def test_assess_risk_no_code(self, client):
        """Test risk assessment without refactored code"""
        response = client.post(
            '/api/v1/phase6/predictions/risk/pattern_123',
            json={}
        )
        
        assert response.status_code == 400

    def test_detect_anomalies(self, client):
        """Test anomaly detection endpoint"""
        response = client.get(
            '/api/v1/phase6/predictions/anomalies',
            query_string={'language': 'python'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'language' in data
        assert 'anomalies' in data

    def test_analyze_trends(self, client):
        """Test trend analysis endpoint"""
        response = client.get(
            '/api/v1/phase6/predictions/trends',
            query_string={'language': 'python'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'language' in data
        assert 'trends' in data

    # ========== Continuous Learning Tests ==========

    def test_record_experience(self, client):
        """Test recording learning experience"""
        response = client.post(
            '/api/v1/phase6/learning/experience',
            json={
                'pattern_id': 'pat_123',
                'original_code': 'def foo(): pass',
                'refactored_code': 'def foo() -> None: pass',
                'agent_name': 'DocGenerator',
                'quality_improvement': 0.2,
                'language': 'python'
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'experience_id' in data

    def test_record_experience_missing_fields(self, client):
        """Test recording experience with missing fields"""
        response = client.post(
            '/api/v1/phase6/learning/experience',
            json={'pattern_id': 'pat_123'}
        )
        
        assert response.status_code == 400

    def test_get_learning_metrics(self, client):
        """Test getting learning metrics"""
        response = client.get('/api/v1/phase6/learning/metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_experiences' in data

    def test_get_learning_report(self, client):
        """Test getting learning report"""
        response = client.get('/api/v1/phase6/learning/report')
        
        assert response.status_code == 200

    # ========== GitHub Integration Tests ==========

    def test_analyze_pr(self, client):
        """Test PR analysis endpoint"""
        response = client.post(
            '/api/v1/phase6/github/pr/123/analyze',
            json={'repo': 'owner/repo'}
        )
        
        assert response.status_code in [200, 202]

    def test_analyze_pr_no_repo(self, client):
        """Test PR analysis without repo"""
        response = client.post(
            '/api/v1/phase6/github/pr/123/analyze',
            json={}
        )
        
        assert response.status_code == 400

    def test_get_webhook_logs(self, client):
        """Test getting webhook logs"""
        response = client.get('/api/v1/phase6/github/webhook-logs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'logs' in data


    # ========== Git Hooks Tests ==========

    def test_configure_hook(self, client):
        """Test configuring hook"""
        response = client.post(
            '/api/v1/phase6/hooks/config',
            json={
                'hook_type': 'pre-commit',
                'enabled': True,
                'quality_threshold': 75.0
            }
        )
        
        assert response.status_code == 201

    def test_configure_hook_no_type(self, client):
        """Test configuring hook without type"""
        response = client.post(
            '/api/v1/phase6/hooks/config',
            json={'enabled': True}
        )
        
        assert response.status_code == 400

    def test_get_hooks_history(self, client):
        """Test getting hook history"""
        response = client.get('/api/v1/phase6/hooks/history')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'executions' in data

    def test_get_hooks_status(self, client):
        """Test getting hooks status"""
        response = client.get('/api/v1/phase6/hooks/status')
        
        assert response.status_code == 200

    # ========== IDE Plugin Tests ==========

    def test_register_plugin(self, client):
        """Test registering IDE plugin"""
        response = client.post(
            '/api/v1/phase6/plugins/register',
            json={
                'ide_type': 'vscode',
                'version': '1.0.0'
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'session_id' in data

    def test_register_plugin_missing_fields(self, client):
        """Test registering plugin without required fields"""
        response = client.post(
            '/api/v1/phase6/plugins/register',
            json={'ide_type': 'vscode'}
        )
        
        assert response.status_code == 400

    def test_analyze_file(self, client):
        """Test analyzing file from IDE"""
        # Register plugin first
        reg_response = client.post(
            '/api/v1/phase6/plugins/register',
            json={'ide_type': 'vscode', 'version': '1.0.0'}
        )
        session_id = json.loads(reg_response.data)['session_id']
        
        # Analyze file
        response = client.post(
            f'/api/v1/phase6/plugins/{session_id}/analyze',
            json={
                'file_path': 'test.py',
                'code': 'x = 1',
                'language': 'python'
            }
        )
        
        assert response.status_code == 201

    def test_quick_feedback(self, client):
        """Test quick feedback endpoint"""
        # Register plugin first
        reg_response = client.post(
            '/api/v1/phase6/plugins/register',
            json={'ide_type': 'vscode', 'version': '1.0.0'}
        )
        session_id = json.loads(reg_response.data)['session_id']
        
        response = client.post(
            f'/api/v1/phase6/plugins/{session_id}/quick-feedback',
            json={
                'file_path': 'test.py',
                'code': 'x = 1',
                'language': 'python'
            }
        )
        
        assert response.status_code == 200

    def test_get_plugin_statistics(self, client):
        """Test getting plugin statistics"""
        response = client.get('/api/v1/phase6/plugins/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_analyses' in data

    # ========== Health Check ==========

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/v1/phase6/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'services' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
