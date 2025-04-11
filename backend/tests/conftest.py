import os
from unittest.mock import patch
from dotenv import load_dotenv

load_dotenv(".env.test")

patch("firebase_admin.initialize_app").start()
patch("firebase_admin.credentials.Certificate").start()
