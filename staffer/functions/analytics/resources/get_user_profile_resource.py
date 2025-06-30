"""User profile resource implementation (legacy)."""

from ..models.schemas import UserProfile
from typing import Dict, Any, Optional
from google.genai import types


def get_user_profile(working_directory: str, user_id: str) -> dict:
    """Get user profile by ID."""
    # In production, this would fetch from a database
    profile = UserProfile(
        id=user_id,
        name=f"User {user_id}",
        email=f"user{user_id}@example.com",
        status="active",
        preferences={
            "theme": "dark",
            "notifications": True,
            "language": "en"
        }
    )
    
    return profile.model_dump()


# Gemini function schema
schema_get_user_profile = types.FunctionDeclaration(
    name="get_user_profile",
    description="Get user profile by ID",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "user_id": types.Schema(
                type=types.Type.STRING,
                description="User ID to fetch profile for",
            ),
        },
        required=["user_id"],
    ),
)