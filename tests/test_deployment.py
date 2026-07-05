"""
Tests for Deployment & Infrastructure - Phase 8
"""

import pytest
import os
from pathlib import Path


class TestDeploymentSetup:
    """Test deployment configuration"""

    def test_dockerfile_exists(self):
        """Test Dockerfile exists"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        assert dockerfile_path.exists()

    def test_docker_compose_exists(self):
        """Test docker-compose.yml exists"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        assert compose_path.exists()

    def test_env_example_exists(self):
        """Test .env.example exists"""
        env_path = Path(__file__).parent.parent / ".env.example"
        assert env_path.exists()

    def test_deployment_guide_exists(self):
        """Test DEPLOYMENT.md exists"""
        guide_path = Path(__file__).parent.parent / "DEPLOYMENT.md"
        assert guide_path.exists()

    def test_k8s_manifests_exist(self):
        """Test Kubernetes manifests exist"""
        k8s_dir = Path(__file__).parent.parent / "k8s"
        
        required_files = [
            "namespace.yaml",
            "api-deployment.yaml",
            "postgres-statefulset.yaml"
        ]
        
        for filename in required_files:
            filepath = k8s_dir / filename
            assert filepath.exists(), f"Missing {filename}"

    def test_dockerfile_has_healthcheck(self):
        """Test Dockerfile includes health check"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        content = dockerfile_path.read_text()
        
        assert "HEALTHCHECK" in content

    def test_dockerfile_uses_nonroot_user(self):
        """Test Dockerfile runs as non-root user"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        content = dockerfile_path.read_text()
        
        assert "useradd" in content
        assert "USER codepulse" in content

    def test_docker_compose_has_all_services(self):
        """Test docker-compose includes all services"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        content = compose_path.read_text()
        
        required_services = ["api", "postgres", "redis", "frontend"]
        for service in required_services:
            assert service in content, f"Missing service: {service}"

    def test_k8s_api_deployment_has_replicas(self):
        """Test K8s API deployment has replicas configured"""
        manifest_path = Path(__file__).parent.parent / "k8s" / "api-deployment.yaml"
        content = manifest_path.read_text()
        
        assert "replicas: 3" in content

    def test_k8s_api_deployment_has_hpa(self):
        """Test K8s API deployment includes HPA"""
        manifest_path = Path(__file__).parent.parent / "k8s" / "api-deployment.yaml"
        content = manifest_path.read_text()
        
        assert "HorizontalPodAutoscaler" in content
        assert "minReplicas: 3" in content
        assert "maxReplicas: 10" in content

    def test_k8s_has_health_probes(self):
        """Test K8s deployment has liveness and readiness probes"""
        manifest_path = Path(__file__).parent.parent / "k8s" / "api-deployment.yaml"
        content = manifest_path.read_text()
        
        assert "livenessProbe" in content
        assert "readinessProbe" in content

    def test_k8s_has_resource_limits(self):
        """Test K8s deployment specifies resource limits"""
        manifest_path = Path(__file__).parent.parent / "k8s" / "api-deployment.yaml"
        content = manifest_path.read_text()
        
        assert "resources:" in content
        assert "requests:" in content
        assert "limits:" in content

    def test_env_example_has_required_vars(self):
        """Test .env.example includes required variables"""
        env_path = Path(__file__).parent.parent / ".env.example"
        content = env_path.read_text()
        
        required_vars = [
            "FLASK_ENV",
            "DATABASE_URL",
            "REDIS_URL",
            "SECRET_KEY",
            "LOG_LEVEL"
        ]
        
        for var in required_vars:
            assert var in content, f"Missing {var}"

    def test_docker_compose_has_volumes(self):
        """Test docker-compose includes persistent volumes"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        content = compose_path.read_text()
        
        assert "volumes:" in content
        assert "postgres_data:" in content or "postgres_data" in content

    def test_deployment_guide_has_sections(self):
        """Test deployment guide has all required sections"""
        guide_path = Path(__file__).parent.parent / "DEPLOYMENT.md"
        content = guide_path.read_text()
        
        required_sections = [
            "Local Development",
            "Docker",
            "Kubernetes",
            "Production Checklist",
            "Monitoring"
        ]
        
        for section in required_sections:
            assert section in content, f"Missing section: {section}"

    def test_k8s_postgres_has_persistence(self):
        """Test K8s PostgreSQL uses StatefulSet with persistence"""
        manifest_path = Path(__file__).parent.parent / "k8s" / "postgres-statefulset.yaml"
        content = manifest_path.read_text()
        
        assert "StatefulSet" in content
        assert "PersistentVolumeClaim" in content
        assert "volumeClaimTemplates:" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
