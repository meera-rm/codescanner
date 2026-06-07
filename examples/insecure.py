# File with security issues
import os
import sys

# SECURITY ISSUE: Hardcoded secret
SECRET_API_KEY = "sk-abc123def456"
DATABASE_PASSWORD = "admin_password_123"

def process_request(user_id):
    # SECURITY ISSUE: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def authenticate_user(username, password):
    if username == "admin" and password == "password123":
        return True
    elif username == "user":
        if password == "123456":
            return True
        elif password == "pass":
            return True
    return False

def high_complexity_func(x):
    """This function has high cyclomatic complexity."""
    if x > 0:
        if x > 10:
            if x > 100:
                return "very large"
            else:
                return "large"
        else:
            return "positive"
    else:
        if x < 0:
            if x < -100:
                return "very negative"
            else:
                return "negative"
        else:
            return "zero"

# SECURITY ISSUE: Hardcoded another secret
API_TOKEN = "token_xyz_789"
