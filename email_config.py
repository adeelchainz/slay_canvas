"""
Email configuration setup for Slay Canvas
Configure SMTP settings to send real emails
"""

# To enable real email sending, follow these steps:

# 1. For Gmail (recommended for development):
#    - Go to your Google Account settings
#    - Enable 2-factor authentication
#    - Generate an "App Password" for this application
#    - Use your Gmail address and the app password below

# 2. Add these to your .env file:
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"  # Use Gmail App Password, not regular password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# 3. Update your config.py to include these settings
# 4. The EmailService will automatically use these when available

# Example .env file content:
"""
# Email Configuration
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # Gmail App Password (spaces are normal)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
"""

# Alternative SMTP providers:
# 
# Outlook/Hotmail:
# SMTP_SERVER=smtp.live.com
# SMTP_PORT=587
#
# Yahoo:
# SMTP_SERVER=smtp.mail.yahoo.com  
# SMTP_PORT=587
#
# Custom SMTP:
# SMTP_SERVER=your-smtp-server.com
# SMTP_PORT=587 (or 465 for SSL)

print("📧 Email configuration guide created!")
print("📝 Edit this file and your .env to enable real email sending")
