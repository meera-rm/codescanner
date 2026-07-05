"""
Tests for Frontend React Components - Phase 9
"""

import pytest
from pathlib import Path


class TestFrontendComponents:
    """Test frontend React component files"""

    def test_dashboard_page_exists(self):
        """Test Dashboard page exists"""
        path = Path(__file__).parent.parent / "frontend/src/pages/Dashboard.tsx"
        assert path.exists()

    def test_dashboard_summary_component_exists(self):
        """Test DashboardSummary component exists"""
        path = Path(__file__).parent.parent / "frontend/src/components/DashboardSummary.tsx"
        assert path.exists()

    def test_ai_insights_widget_exists(self):
        """Test AIInsightsWidget component exists"""
        path = Path(__file__).parent.parent / "frontend/src/components/widgets/AIInsightsWidget.tsx"
        assert path.exists()

    def test_system_health_widget_exists(self):
        """Test SystemHealthWidget component exists"""
        path = Path(__file__).parent.parent / "frontend/src/components/widgets/SystemHealthWidget.tsx"
        assert path.exists()

    def test_alerts_widget_exists(self):
        """Test AlertsWidget component exists"""
        path = Path(__file__).parent.parent / "frontend/src/components/widgets/AlertsWidget.tsx"
        assert path.exists()

    def test_activity_widget_exists(self):
        """Test ActivityWidget component exists"""
        path = Path(__file__).parent.parent / "frontend/src/components/widgets/ActivityWidget.tsx"
        assert path.exists()

    def test_usage_widget_exists(self):
        """Test UsageWidget component exists"""
        path = Path(__file__).parent.parent / "frontend/src/components/widgets/UsageWidget.tsx"
        assert path.exists()

    def test_analytics_panel_exists(self):
        """Test AnalyticsPanel component exists"""
        path = Path(__file__).parent.parent / "frontend/src/components/AnalyticsPanel.tsx"
        assert path.exists()

    def test_dashboard_page_imports_widgets(self):
        """Test Dashboard imports widget components"""
        path = Path(__file__).parent.parent / "frontend/src/pages/Dashboard.tsx"
        content = path.read_text()
        
        required_imports = [
            "AIInsightsWidget",
            "SystemHealthWidget",
            "AlertsWidget",
            "ActivityWidget",
            "UsageWidget"
        ]
        
        for import_name in required_imports:
            assert import_name in content

    def test_dashboard_has_tabs(self):
        """Test Dashboard has tab navigation"""
        path = Path(__file__).parent.parent / "frontend/src/pages/Dashboard.tsx"
        content = path.read_text()
        
        assert "overview" in content
        assert "analytics" in content
        assert "health" in content

    def test_dashboard_fetches_data(self):
        """Test Dashboard fetches data from API"""
        path = Path(__file__).parent.parent / "frontend/src/pages/Dashboard.tsx"
        content = path.read_text()
        
        assert "fetch" in content
        assert "/api/v1/dashboard" in content

    def test_widgets_fetch_from_api(self):
        """Test widgets fetch from API endpoints"""
        widget_files = [
            "frontend/src/components/widgets/AIInsightsWidget.tsx",
            "frontend/src/components/widgets/SystemHealthWidget.tsx",
            "frontend/src/components/widgets/AlertsWidget.tsx",
        ]
        
        for widget_file in widget_files:
            path = Path(__file__).parent.parent / widget_file
            if path.exists():
                content = path.read_text()
                assert "fetch" in content
                assert "/api/v1/dashboard" in content

    def test_dashboard_uses_material_ui(self):
        """Test Dashboard uses Material-UI components"""
        path = Path(__file__).parent.parent / "frontend/src/pages/Dashboard.tsx"
        content = path.read_text()
        
        assert "Container" in content or "@mui/material" in content

    def test_dashboard_summary_displays_metrics(self):
        """Test DashboardSummary displays key metrics"""
        path = Path(__file__).parent.parent / "frontend/src/components/DashboardSummary.tsx"
        content = path.read_text()
        
        assert "System Health" in content
        assert "API Health" in content
        assert "Patterns Found" in content

    def test_analytics_panel_has_charts(self):
        """Test AnalyticsPanel includes chart components"""
        path = Path(__file__).parent.parent / "frontend/src/components/AnalyticsPanel.tsx"
        content = path.read_text()
        
        assert "BarChart" in content or "LineChart" in content
        assert "ResponsiveContainer" in content

    def test_components_handle_loading_state(self):
        """Test components handle loading states"""
        path = Path(__file__).parent.parent / "frontend/src/pages/Dashboard.tsx"
        content = path.read_text()
        
        assert "loading" in content.lower()
        assert "CircularProgress" in content or "progress" in content.lower()

    def test_components_handle_errors(self):
        """Test components handle error states"""
        path = Path(__file__).parent.parent / "frontend/src/pages/Dashboard.tsx"
        content = path.read_text()
        
        assert "error" in content.lower()
        assert "Alert" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
