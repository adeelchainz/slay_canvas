"""
Generate secure SECRET_KEY for Slay Canvas
"""

import secrets
import os
from pathlib import Path

def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(32)

def update_env_file():
    """Update .env file with a secure secret key"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found!")
        return
    
    # Generate secure key
    new_secret = generate_secret_key()
    
    # Read current .env file
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Replace the placeholder secret key
    if "your-super-secret-key-here-generate-a-random-one" in content:
        content = content.replace(
            "your-super-secret-key-here-generate-a-random-one",
            new_secret
        )
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ SECRET_KEY updated successfully!")
        print(f"🔑 New SECRET_KEY: {new_secret[:20]}...")
    else:
        print("⚠️  SECRET_KEY already seems to be configured")
        print(f"💡 If you want a new one, use this: {new_secret}")

if __name__ == "__main__":
    print("🔐 Generating secure SECRET_KEY...")
    update_env_file()
