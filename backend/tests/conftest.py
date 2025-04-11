import os
import pytest
from unittest.mock import patch

from dotenv import load_dotenv

load_dotenv(".env.test")


@pytest.fixture(autouse=True, scope="session")
def mock_firebase():
    with patch("firebase_admin.initialize_app"), patch(
        "firebase_admin.credentials.Certificate"
    ):
        yield
