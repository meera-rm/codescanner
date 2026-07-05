"""
Tests for File Modifier Service - Phase 4.2a
Tests basic file modification, import addition, and code insertion
"""

import pytest
import tempfile
from pathlib import Path
import asyncio
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.file_modifier_service import FileModifierService, ModificationResult


@pytest.fixture
def temp_codebase():
    """Create temporary codebase for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create sample Python files
        sample_py = tmppath / "sample.py"
        sample_py.write_text(
            """def original_function():
    \"\"\"Original function\"\"\"
    return 42

def other_function():
    return original_function()
"""
        )

        # Create file with imports
        imports_py = tmppath / "with_imports.py"
        imports_py.write_text(
            """import os
from pathlib import Path

def process_file(path):
    return os.path.exists(path)
"""
        )

        # Create subdirectory with file
        subdir = tmppath / "subdir"
        subdir.mkdir()
        sub_file = subdir / "nested.py"
        sub_file.write_text("# Empty module\nPASSED = True\n")

        yield tmppath


@pytest.mark.asyncio
async def test_modify_python_file_add_imports(temp_codebase):
    """Test adding imports to a Python file"""
    modifier = FileModifierService(str(temp_codebase))
    sample_file = temp_codebase / "sample.py"

    result = await modifier._modify_python_file(
        sample_file, new_imports=["ast", "json"], new_code="", dry_run=False
    )

    assert result is True
    content = sample_file.read_text()
    assert "import ast" in content
    assert "import json" in content


@pytest.mark.asyncio
async def test_modify_python_file_add_code(temp_codebase):
    """Test adding new code to a Python file"""
    modifier = FileModifierService(str(temp_codebase))
    sample_file = temp_codebase / "sample.py"

    new_code = """def new_function():
    \"\"\"New helper function\"\"\"
    return 100"""

    result = await modifier._modify_python_file(
        sample_file, new_imports=[], new_code=new_code, dry_run=False
    )

    assert result is True
    content = sample_file.read_text()
    assert "new_function" in content
    assert "New helper function" in content


@pytest.mark.asyncio
async def test_modify_python_file_dry_run(temp_codebase):
    """Test dry run doesn't modify files"""
    modifier = FileModifierService(str(temp_codebase))
    sample_file = temp_codebase / "sample.py"
    original_content = sample_file.read_text()

    result = await modifier._modify_python_file(
        sample_file, new_imports=["ast"], new_code="def new_func():\n    pass", dry_run=True
    )

    assert result is True
    # File should not be modified in dry run
    assert sample_file.read_text() == original_content


@pytest.mark.asyncio
async def test_apply_suggestion_success(temp_codebase):
    """Test applying a complete suggestion"""
    modifier = FileModifierService(str(temp_codebase))

    suggestion = {
        "agent": "Agent A",
        "description": "Extract helper function",
        "changes": ["New: check_valid()"],
        "new_imports": ["ast"],
        "modified_code": """def check_valid(code):
    \"\"\"Check if code is valid\"\"\"
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False""",
    }

    result = await modifier.apply_suggestion(str(temp_codebase), suggestion, dry_run=False)

    assert result.success
    assert len(result.files_modified) > 0
    assert "imports_added" in result.changes


@pytest.mark.asyncio
async def test_apply_suggestion_dry_run(temp_codebase):
    """Test dry run of suggestion"""
    modifier = FileModifierService(str(temp_codebase))
    original_count = sum(1 for _ in temp_codebase.rglob("*.py"))

    suggestion = {
        "agent": "Agent A",
        "description": "Test suggestion",
        "changes": [],
        "new_imports": [],
        "modified_code": "def test(): pass",
    }

    result = await modifier.apply_suggestion(str(temp_codebase), suggestion, dry_run=True)

    # Dry run should return success but no modified files
    assert result.success
    assert len(result.files_modified) == 0


@pytest.mark.asyncio
async def test_validate_suggestion_valid(temp_codebase):
    """Test validating a valid suggestion"""
    modifier = FileModifierService(str(temp_codebase))

    suggestion = {
        "agent": "Agent A",
        "description": "Valid suggestion",
        "changes": ["New function"],
        "new_imports": ["ast"],
        "modified_code": "def new_func():\n    pass",
    }

    errors = modifier.validate_suggestion(suggestion)
    assert len(errors) == 0


@pytest.mark.asyncio
async def test_validate_suggestion_missing_fields(temp_codebase):
    """Test validating suggestion with missing fields"""
    modifier = FileModifierService(str(temp_codebase))

    # Missing description
    suggestion = {
        "agent": "Agent A",
        "changes": [],
    }

    errors = modifier.validate_suggestion(suggestion)
    assert len(errors) > 0
    assert any("description" in e for e in errors)


@pytest.mark.asyncio
async def test_validate_suggestion_invalid_type(temp_codebase):
    """Test validating suggestion with invalid types"""
    modifier = FileModifierService(str(temp_codebase))

    suggestion = {
        "agent": "Agent A",
        "description": "Test",
        "changes": [],
        "new_imports": "should be list",  # Should be list
    }

    errors = modifier.validate_suggestion(suggestion)
    assert len(errors) > 0
    assert any("new_imports" in e for e in errors)


@pytest.mark.asyncio
async def test_modification_result_structure(temp_codebase):
    """Test ModificationResult data structure"""
    result = ModificationResult(
        success=True,
        files_modified=["file1.py", "file2.py"],
        files_failed=[],
        changes={"files": 2, "lines_added": 50},
        diff="unified diff here",
    )

    assert result.success
    assert len(result.files_modified) == 2
    assert result.diff is not None


@pytest.mark.asyncio
async def test_file_with_existing_imports(temp_codebase):
    """Test modifying file that already has imports"""
    modifier = FileModifierService(str(temp_codebase))
    imports_file = temp_codebase / "with_imports.py"
    original = imports_file.read_text()

    result = await modifier._modify_python_file(
        imports_file, new_imports=["typing"], new_code="", dry_run=False
    )

    assert result is True
    content = imports_file.read_text()
    # Should have both original and new imports
    assert "import os" in content
    assert "from pathlib import Path" in content
    assert "import typing" in content


@pytest.mark.asyncio
async def test_rollback_changes(temp_codebase):
    """Test rolling back modifications"""
    modifier = FileModifierService(str(temp_codebase))
    sample_file = temp_codebase / "sample.py"
    original_content = sample_file.read_text()

    # Modify file
    await modifier._modify_python_file(
        sample_file, new_imports=["ast"], new_code="", dry_run=False
    )

    # Verify it was modified
    modified_content = sample_file.read_text()
    assert modified_content != original_content

    # Rollback
    await modifier._rollback_changes()

    # Verify it was rolled back
    assert sample_file.read_text() == original_content


@pytest.mark.asyncio
async def test_modify_nested_file(temp_codebase):
    """Test modifying file in subdirectory"""
    modifier = FileModifierService(str(temp_codebase))
    nested_file = temp_codebase / "subdir" / "nested.py"

    result = await modifier._modify_python_file(
        nested_file, new_imports=["sys"], new_code="", dry_run=False
    )

    assert result is True
    content = nested_file.read_text()
    assert "import sys" in content


@pytest.mark.asyncio
async def test_suggestion_with_complex_imports(temp_codebase):
    """Test suggestion with complex import statements"""
    modifier = FileModifierService(str(temp_codebase))

    suggestion = {
        "agent": "Agent B",
        "description": "Add complex imports",
        "changes": [],
        "new_imports": ["typing.Dict", "typing.List"],
        "modified_code": "",
    }

    result = await modifier.apply_suggestion(str(temp_codebase), suggestion, dry_run=False)

    assert result.success


@pytest.mark.asyncio
async def test_modification_result_with_error(temp_codebase):
    """Test ModificationResult with error"""
    result = ModificationResult(
        success=False,
        files_modified=[],
        files_failed=["bad_file.py"],
        changes={"error": "File not found"},
        error_message="File not found",
    )

    assert not result.success
    assert result.error_message is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
