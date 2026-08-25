"""Shared pytest fixtures for all tests."""

import tempfile
from pathlib import Path
import pytest
import sys

# Add scanner to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Lazy import RepoMetrics to avoid circular imports
# (metrics_aggregator → scanner → creative_suite → caqi → metrics_aggregator)
RepoMetrics = None


@pytest.fixture
def temp_dir():
    """Provide a temporary directory that's cleaned up after test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_clean_file():
    """Sample clean Python file with good practices."""
    return '''
"""Module with clean code."""

def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b


def calculate_product(x, y):
    """Calculate product of two numbers."""
    return x * y


class Calculator:
    """Simple calculator class."""

    def __init__(self):
        """Initialize calculator."""
        self.result = 0

    def add(self, x):
        """Add value to result."""
        self.result += x
        return self.result

    def multiply(self, x):
        """Multiply result by value."""
        self.result *= x
        return self.result
'''


@pytest.fixture
def sample_smelly_file():
    """Sample Python file with code smells."""
    return '''
def long_function_with_many_lines(a, b, c, d, e, f, g):
    """This function is too long and has too many parameters."""
    x = a + b
    y = c + d
    z = e + f
    result = g
    for i in range(10):
        x += i
    for j in range(10):
        y += j
    for k in range(10):
        z += k
    if result > 0:
        if x > 0:
            if y > 0:
                if z > 0:
                    if result > 100:
                        return x + y + z
    return 0
'''


@pytest.fixture
def sample_insecure_file():
    """Sample Python file with security issues."""
    return '''
"""File with security vulnerabilities."""

api_key = "REDACTED_FOR_TEST"
password = "MyPassword123"
db_user = "admin"
db_password = "admin123"
aws_secret = "REDACTED_FOR_TEST"

def connect_database():
    """Connect to database with hardcoded credentials."""
    # User: admin, Password: password123
    return None
'''


@pytest.fixture
def sample_undocumented_file():
    """Sample Python file with missing documentation."""
    return '''
def calculate(x, y):
    return x + y

def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

class DataProcessor:
    def __init__(self):
        self.data = []

    def add(self, item):
        self.data.append(item)

    def get_all(self):
        return self.data
'''


@pytest.fixture
def sample_duplicated_code():
    """Sample Python with duplicated functions."""
    code = '''
def process_list_a(items):
    """Process a list."""
    result = []
    for item in items:
        result.append(item * 2)
    return result

def process_list_b(items):
    """Process another list."""
    result = []
    for item in items:
        result.append(item * 2)
    return result

def process_list_c(items):
    """Process yet another list."""
    result = []
    for item in items:
        result.append(item * 2)
    return result
'''
    return code


@pytest.fixture
def sample_coupled_files():
    """Fixture providing two coupled Python files."""
    return {
        "module_a.py": '''
"""Module A - depends on B."""
import module_b

def func_a():
    """Use module B."""
    return module_b.func_b()
''',
        "module_b.py": '''
"""Module B - depends on A."""
import module_a

def func_b():
    """Use module A."""
    return module_a.func_a()
''',
    }


@pytest.fixture
def sample_repo_metrics():
    """Sample RepoMetrics for testing CAQI calculation."""
    # Lazy import to avoid circular import issues
    from metrics_aggregator import RepoMetrics

    return RepoMetrics(
        avg_complexity=5.0,
        max_complexity=12.0,
        security_high_count=2,
        security_medium_count=3,
        smell_count=4,
        doc_coverage_ratio=0.80,
        duplication_percentage=5.0,
        avg_imports_per_file=2.5,
        has_circular_deps=False,
        files_analyzed=10,
        total_lines=500,
        per_file_metrics={
            "app.py": {
                "lines": 100,
                "security_issues": 1,
                "smells": 2,
                "doc_coverage": 0.75,
                "functions": 8,
                "documented_functions": 6,
            },
            "utils.py": {
                "lines": 80,
                "security_issues": 0,
                "smells": 1,
                "doc_coverage": 0.90,
                "functions": 5,
                "documented_functions": 5,
            },
        },
    )


@pytest.fixture
def create_python_file(temp_dir):
    """Factory fixture to create Python files in temp directory."""
    def _create_file(filename, content):
        path = Path(temp_dir) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return str(path)
    return _create_file


@pytest.fixture
def create_project(temp_dir):
    """Factory fixture to create a complete project structure."""
    def _create_project(files_dict):
        """Create multiple files from dict: {filename: content}."""
        paths = {}
        for filename, content in files_dict.items():
            path = Path(temp_dir) / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            paths[filename] = str(path)
        return temp_dir, paths
    return _create_project


# Phase I+1 Test Fixtures

class MockMetric:
    """Mock Metric for developer drill-down testing."""
    def __init__(self, developer_id, team_id, security, complexity, documentation,
                 testing, dependencies, maintainability, recorded_at):
        self.developer_id = developer_id
        self.team_id = team_id
        self.security = security
        self.complexity = complexity
        self.documentation = documentation
        self.testing = testing
        self.dependencies = dependencies
        self.maintainability = maintainability
        self.recorded_at = recorded_at


class MockTeamMember:
    """Mock TeamMember for testing."""
    def __init__(self, team_id, developer_id):
        self.team_id = team_id
        self.developer_id = developer_id


class MockTeamScore:
    """Mock TeamScore for testing."""
    def __init__(self, team_id, team_name, overall_caqi, security, complexity,
                 documentation, testing, dependencies, maintainability, calculated_at):
        self.team_id = team_id
        self.team_name = team_name
        self.overall_caqi = overall_caqi
        self.security = security
        self.complexity = complexity
        self.documentation = documentation
        self.testing = testing
        self.dependencies = dependencies
        self.maintainability = maintainability
        self.calculated_at = calculated_at


class MockDatabase:
    """Mock database for testing without real database."""
    def __init__(self):
        self.teams = {}
        self.members = {}
        self.metrics = {}
        self.anomalies = {}
        self.peer_groups = {}
        self.benchmarks = {}
        self.query_results = {}

    def query(self, model_class):
        """Mock query interface."""
        return MockQuery(self, model_class)

    def add(self, obj):
        """Mock add."""
        pass

    def add_all(self, objs):
        """Mock add_all."""
        pass

    def commit(self):
        """Mock commit."""
        pass

    def close(self):
        """Mock close."""
        pass


class MockQuery:
    """Mock query builder for testing."""
    def __init__(self, db, model_class):
        self.db = db
        self.model_class = model_class
        self._filter_conditions = []
        self._results = []

    def filter(self, *conditions):
        """Mock filter - just store conditions, don't try to parse them."""
        self._filter_conditions.extend(conditions)
        return self

    def all(self):
        """Return all results."""
        return self._results

    def first(self):
        """Return first result."""
        return self._results[0] if self._results else None

    def order_by(self, field):
        """Mock order_by - sort by field if it exists."""
        if self._results and hasattr(self._results[0], 'recorded_at'):
            self._results = sorted(self._results, key=lambda x: x.recorded_at)
        return self

    def in_(self, values):
        """Mock in_ for WHERE IN clauses."""
        return self

    def __iter__(self):
        """Allow iteration over query results."""
        return iter(self._results)


@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    return MockDatabase()


@pytest.fixture
def team_with_developers(mock_db):
    """Create sample team with members and metrics."""
    from datetime import datetime, timedelta

    # Create team
    team = MockTeamScore(
        team_id="test-team",
        team_name="Test Team",
        overall_caqi=350,
        security=75,
        complexity=70,
        documentation=65,
        testing=80,
        dependencies=60,
        maintainability=75,
        calculated_at=datetime.utcnow()
    )

    # Create members
    members = [
        MockTeamMember("test-team", "dev-1"),
        MockTeamMember("test-team", "dev-2"),
        MockTeamMember("test-team", "dev-3"),
    ]

    # Create metrics - setup for MockQuery to return them
    today = datetime.utcnow()
    metrics = []
    for i in range(3):  # 3 days of data
        for j, dev_id in enumerate(["dev-1", "dev-2", "dev-3"]):
            metric = MockMetric(
                developer_id=dev_id,
                team_id="test-team",
                security=75 + (j * 5),
                complexity=70 + (j * 3),
                documentation=65 + (j * 4),
                testing=80 + (j * 2),
                dependencies=60 + (j * 6),
                maintainability=75 + (j * 3),
                recorded_at=today - timedelta(days=i)
            )
            metrics.append(metric)

    # Store data on the mock_db for later access
    mock_db._team = team
    mock_db._members = members
    mock_db._metrics = metrics

    # Setup MockDatabase to return proper query results
    original_query = mock_db.query

    def query_with_results(model_class):
        q = original_query(model_class)
        if model_class.__name__ == 'TeamMember':
            q._results = members
        elif model_class.__name__ == 'Metric':
            q._results = metrics
        elif model_class.__name__ == 'TeamScore':
            q._results = [team]
        return q

    mock_db.query = query_with_results

    return team, members, metrics
