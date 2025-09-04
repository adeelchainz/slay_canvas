"""
Quick Email Setup for Slay Canvas
"""

print("📧 Email Configuration Setup")
print("=" * 50)
print()
print("To receive OTPs in your email inbox:")
print()
print("1. Create a .env file in your project root")
print("2. Add these lines to .env:")
print()
print("   SMTP_USERNAME=your-email@gmail.com")
print("   SMTP_PASSWORD=your-gmail-app-password")
print()
print("3. For Gmail App Password:")
print("   - Go to Google Account settings")
print("   - Security → 2-Step Verification")
print("   - App passwords → Generate new password")
print("   - Use that 16-character password in .env")
print()
print("4. Restart your server")
print()
print("=" * 50)
print("🚀 For now, check the server console for OTP!")

# Let's also show current server status
import requests
try:
    response = requests.get("http://localhost:8000/api/auth/health")
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Server Status: {data.get('status', 'unknown')}")
        print(f"📧 Email Service: {'✅ Configured' if data.get('services', {}).get('email_service_configured') else '⚠️ Not configured'}")
    else:
        print("⚠️ Server not running on port 8000")
except:
    print("⚠️ Could not connect to server")
