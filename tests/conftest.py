import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_db() -> AsyncMock:
    db = AsyncMock()
    return db
