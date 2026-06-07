# Phase 3.5 Developer Guide

**For:** Developers extending Iteration Until Clean

---

## Architecture Overview

### File Structure

```
codescanner/
├── api/
│   ├── services/
│   │   ├── agents/                    # Agent implementations
│   │   │   ├── __init__.py
│   │   │   ├── refactoring_agent.py   # Base class
│   │   │   ├── agent_a_simplicity.py  # Agent A
│   │   │   ├── agent_b_architecture.py # Agent B
│   │   │   ├── agent_c_performance.py  # Agent C
│   │   │   ├── evaluation_agent.py    # Scoring
│   │   │   └── validator_agent.py     # Validation
│   │   ├── iteration_clean_service.py # Main loop
│   │   └── ...
│   ├── routes/
│   │   └── iteration.py               # REST endpoints
│   ├── tasks/
│   │   └── iteration.py               # Celery tasks
│   ├── models/
│   │   ├── iteration_requests.py      # Request models
│   │   ├── iteration_responses.py     # Response models
│   │   └── ...
│   ├── db/
│   │   ├── models.py                  # ORM models
│   │   └── database.py                # DB config
│   └── main.py                        # FastAPI app
├── tests/
│   ├── test_agents.py                 # Agent tests
│   ├── test_iteration_service.py      # Service tests
│   └── test_iteration_api.py          # API tests
└── docs/
    ├── API_REFERENCE_ITERATION.md
    ├── DEPLOYMENT_GUIDE.md
    └── DEVELOPER_GUIDE.md (this file)
```

---

## Key Concepts

### Agents

Each agent inherits from `RefactoringAgent` and implements:

```python
class MyAgent(RefactoringAgent):
    def __init__(self):
        super().__init__()
        self.name = "My Agent"
        self.strategy = "My Strategy"
    
    async def suggest_refactoring(self, codebase_path: str, 
                                   issues: List[Issue]) -> Optional[Suggestion]:
        # Analyze issues
        # Generate suggestion
        return Suggestion(
            agent=f"{self.name} ({self.strategy})",
            description="What the fix does",
            changes=["List", "of", "changes"],
            complexity_reduction=50,  # 0-100
            risk_level="low",         # "low", "medium", "high"
            clarity_improvement="good", # "ok", "good", "excellent"
            estimated_time="quick"    # "quick", "medium", "slow"
        )
```

### Evaluation

The `EvaluationAgent` scores suggestions:

```python
evaluator = EvaluationAgent()

# Score all suggestions
scored = evaluator.score_all(suggestions)
# Returns: [
#   ScoredSuggestion(suggestion=..., score=78.5, breakdown={...}),
#   ScoredSuggestion(suggestion=..., score=65.0, breakdown={...}),
# ]

# Get the best
best = evaluator.pick_best(suggestions)
# Returns: Best Suggestion object
```

**Scoring Formula:**
```
score = (complexity × 0.30) + (risk × 0.40) + (clarity × 0.20) + (time × 0.10)
```

### Validation

The `ValidatorAgent` checks 5 points before applying:

```python
validator = ValidatorAgent()
result = await validator.validate(suggestion)
# Returns: ValidationResult(
#   approved=True/False,
#   checks=[
#     ValidationCheck(check_name="Syntax Check", passed=True, ...),
#     ValidationCheck(check_name="Import Validation", passed=True, ...),
#     ...
#   ],
#   summary="✅ APPROVED - 5/5 checks passed"
# )
```

### Main Loop

`IterationCleanService.fix_until_clean()` orchestrates:

```python
service = IterationCleanService()
result = await service.fix_until_clean(
    job_id="my_job",
    codebase_path="/code",
    target_grade="A",
    max_iterations=10
)
# Returns: IterationResult
```

---

## Extending the System

### Adding a New Agent

**1. Create Agent Class**

```python
# api/services/agents/agent_d_custom.py

from .refactoring_agent import RefactoringAgent, Suggestion, Issue
from typing import List, Optional

class AgentD_Custom(RefactoringAgent):
    """Custom refactoring strategy."""
    
    def __init__(self):
        super().__init__()
        self.name = "Agent D"
        self.strategy = "Custom Strategy"
    
    async def suggest_refactoring(self, codebase_path: str, 
                                   issues: List[Issue]) -> Optional[Suggestion]:
        """Generate custom suggestion."""
        
        if not issues:
            return None
        
        # Your logic here
        target_issue = self._find_most_complex_issue(issues)
        
        return Suggestion(
            agent=f"{self.name} ({self.strategy})",
            description="Your description",
            changes=["change1", "change2"],
            complexity_reduction=55,
            risk_level="low",
            clarity_improvement="good",
            estimated_time="quick"
        )
```

**2. Register Agent**

```python
# api/services/iteration_clean_service.py

from .agents import AgentD_Custom  # Add import

class IterationCleanService:
    def __init__(self, scanner_service=None):
        # ... existing agents ...
        self.agent_d = AgentD_Custom()  # Add new agent
```

**3. Update `_get_suggestions()`**

```python
async def _get_suggestions(self, codebase_path: str, 
                          issues: List[Issue]) -> List[Suggestion]:
    """Get suggestions from all agents in parallel."""
    suggestions = await asyncio.gather(
        self.agent_a.suggest_refactoring(codebase_path, issues),
        self.agent_b.suggest_refactoring(codebase_path, issues),
        self.agent_c.suggest_refactoring(codebase_path, issues),
        self.agent_d.suggest_refactoring(codebase_path, issues),  # Add new agent
    )
    return [s for s in suggestions if s]
```

**4. Write Tests**

```python
# tests/test_agents.py

@pytest.mark.asyncio
async def test_agent_d_returns_suggestion(sample_issues):
    """Test Agent D generates suggestions."""
    agent_d = AgentD_Custom()
    suggestion = await agent_d.suggest_refactoring("/code", sample_issues)
    assert suggestion is not None
    assert suggestion.agent == "Agent D (Custom Strategy)"
```

---

### Customizing Validation

Add a new validation check:

```python
# api/services/agents/validator_agent.py

async def _check_custom(self, suggestion: Suggestion) -> None:
    """Custom validation check."""
    
    check_name = "Custom Check"
    
    # Your validation logic
    is_valid = len(suggestion.description) > 10
    
    self.check_results.append(
        ValidationCheck(
            check_name=check_name,
            passed=is_valid,
            details="Your message here"
        )
    )

# In validate() method, add:
# await self._check_custom(suggestion)
```

---

### Adding a New REST Endpoint

```python
# api/routes/iteration.py

@router.get(
    "/{job_id}/stats",
    response_model=dict,
    summary="Get iteration statistics"
)
async def get_iteration_stats(job_id: str, db: Session = Depends(get_db)):
    """Get advanced statistics for a job."""
    
    job = db.query(IterationJob).filter(IterationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Your logic here
    stats = {
        "job_id": job_id,
        "total_iterations": job.current_iteration,
        "avg_issues_fixed_per_iteration": 0,
        # ... more stats
    }
    
    return stats
```

Register in `api/main.py`:
```python
from api.routes import iteration
app.include_router(iteration.router)
```

---

## Testing Guidelines

### Unit Tests

Test individual components in isolation:

```python
@pytest.mark.asyncio
async def test_agent_specific_behavior():
    """Test agent-specific logic."""
    agent = MyAgent()
    suggestion = await agent.suggest_refactoring("/code", [])
    assert suggestion is None  # Empty issues = no suggestion
```

### Integration Tests

Test the full loop:

```python
@pytest.mark.asyncio
async def test_full_iteration_loop():
    """Test complete iteration until clean."""
    service = IterationCleanService()
    result = await service.fix_until_clean(
        job_id="test_1",
        codebase_path="/code",
        target_grade="A",
        max_iterations=5
    )
    assert result.status in ["completed", "failed"]
```

### API Tests

Test REST endpoints:

```python
def test_start_iteration(client, db):
    """Test starting an iteration job."""
    response = client.post(
        "/api/v1/iteration/fix-until-clean",
        json={"directory_path": "/code"}
    )
    assert response.status_code == 202
    assert "job_id" in response.json()
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_agents.py::test_agent_a_returns_suggestion -v

# With coverage
pytest tests/ --cov=api --cov-report=html
```

---

## Database Migrations

When adding new fields to models:

```python
# 1. Update ORM model in api/db/models.py
class IterationJob(Base):
    # ... existing fields ...
    new_field = Column(String, default="")  # Add new field

# 2. Create migration (if using Alembic)
alembic revision --autogenerate -m "Add new_field to IterationJob"
alembic upgrade head

# 3. Or manually update tables
from api.db.database import Base, engine
Base.metadata.create_all(bind=engine)
```

---

## Performance Optimization

### Database Queries

Use SQLAlchemy efficiently:

```python
# ❌ N+1 problem
jobs = db.query(IterationJob).all()
for job in jobs:
    history = db.query(IterationHistory).filter(...)  # Multiple queries

# ✅ Use eager loading
jobs = db.query(IterationJob).options(
    joinedload(IterationJob.iteration_history)
).all()
for job in jobs:
    history = job.iteration_history  # Single query
```

### Async Operations

Use async/await for parallel work:

```python
# ❌ Sequential
results = []
for agent in agents:
    suggestion = await agent.suggest_refactoring(path, issues)
    results.append(suggestion)

# ✅ Parallel
results = await asyncio.gather(
    *[agent.suggest_refactoring(path, issues) for agent in agents]
)
```

### Caching

Cache expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_grade(issues_count: int) -> str:
    """Cache grade calculations."""
    if issues_count < 5:
        return "A"
    # ... more logic
```

---

## Error Handling

### Custom Exceptions

```python
class IterationError(Exception):
    """Base exception for iteration errors."""
    pass

class ValidationError(IterationError):
    """Raised when validation fails."""
    pass

class AgentError(IterationError):
    """Raised when agent fails to generate suggestion."""
    pass
```

### Try-Except Patterns

```python
try:
    result = await service.fix_until_clean(...)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    # Handle gracefully
except IterationError as e:
    logger.error(f"Iteration error: {e}")
    # Handle gracefully
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Log and re-raise
    raise
```

---

## Logging

Add logging throughout:

```python
import logging

logger = logging.getLogger(__name__)

async def fix_until_clean(self, job_id: str, ...):
    """Main iteration loop with logging."""
    logger.info(f"Starting job {job_id}")
    
    try:
        for iteration in range(max_iterations):
            logger.debug(f"Iteration {iteration + 1}/{max_iterations}")
            
            # ... iteration logic ...
            
            logger.info(f"Iteration {iteration + 1} completed: {new_grade}")
    
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        raise
    
    logger.info(f"Job {job_id} completed successfully")
```

---

## Type Hints

Always use type hints:

```python
from typing import Optional, List, Dict, Any

async def suggest_refactoring(
    self,
    codebase_path: str,  # Parameter type
    issues: List[Issue]  # Parameter type
) -> Optional[Suggestion]:  # Return type
    """Generate suggestion."""
    ...
```

---

## Code Style

Follow PEP 8:

```bash
# Format code
black api/ tests/

# Check style
flake8 api/ tests/

# Type check
mypy api/ --ignore-missing-imports
```

---

## Common Tasks

### Debugging a Stuck Job

```python
from api.db.database import SessionLocal
from api.db.models import IterationJob

db = SessionLocal()
job = db.query(IterationJob).filter(IterationJob.id == "stuck_job").first()

print(f"Status: {job.status}")
print(f"Iterations: {job.current_iteration}")
print(f"Error: {job.error_message}")

# Mark as failed
job.status = "failed"
job.error_message = "Manual intervention"
db.commit()
```

### Finding Memory Leaks

```python
import tracemalloc

tracemalloc.start()

# ... run iteration ...

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f} MB")
print(f"Peak: {peak / 1024 / 1024:.2f} MB")
tracemalloc.stop()
```

### Profiling Performance

```bash
# Profile a function
python -m cProfile -s cumtime api/main.py

# Or use py-spy
pip install py-spy
py-spy record -o profile.svg -- python api/main.py
```

---

## Contributing

### Pull Request Process

1. Create feature branch: `git checkout -b feature/my-feature`
2. Write tests first (TDD)
3. Implement feature
4. Run tests: `pytest tests/ -v`
5. Format code: `black api/ tests/`
6. Create PR with clear description
7. Wait for review
8. Merge when approved

### Code Review Checklist

- [ ] Tests pass locally
- [ ] Code follows PEP 8
- [ ] Type hints present
- [ ] Docstrings clear
- [ ] No breaking changes
- [ ] Documentation updated
- [ ] No security issues

---

## Resources

- **API Spec:** `docs/API_REFERENCE_ITERATION.md`
- **Deployment:** `docs/DEPLOYMENT_GUIDE.md`
- **Architecture:** `PHASE_35_ITERATION_UNTIL_CLEAN_IMPLEMENTATION_COMPLETE.md`
- **Memory:** `[[iteration-until-clean-skill]]`

---

**Happy Developing! 🚀**

