"""
Application configuration, sourced entirely from environment variables.
No secrets are hardcoded — see .env.example for the variables this app expects.
"""

import os

from dotenv import load_dotenv

load_dotenv()  # reads a local .env file in development; no-op if absent


class Config:
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
    JWT_EXPIRES_HOURS = int(os.environ.get("JWT_EXPIRES_HOURS", "24"))
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
    AI_API_KEY = os.environ.get("AI_API_KEY", "")  # optional; falls back to rule-based engine
    PORT = int(os.environ.get("PORT", "5000"))
