# Google OAuth Setup Guide for MediaBoard AI

## 🎯 Quick Setup Checklist

- [ ] Create Google Cloud Project
- [ ] Enable APIs (Google+ API, OAuth2 API)
- [ ] Configure OAuth Consent Screen
- [ ] Create OAuth 2.0 Credentials
- [ ] Update .env file
- [ ] Test the integration

## 📋 Detailed Steps

### 1. Google Cloud Console Setup

#### Create Project
1. Go to: https://console.cloud.google.com/
2. Click project dropdown → "New Project"
3. Project name: `MediaBoard AI`
4. Click "Create"

#### Enable APIs
1. Navigate: APIs & Services → Library
2. Search and enable:
   - **Google+ API**
   - **Google OAuth2 API**
   - **Google People API** (recommended)

### 2. OAuth Consent Screen Configuration

#### Basic Information
```
App name: MediaBoard AI
User support email: your-email@gmail.com
Developer contact: your-email@gmail.com
```

#### App Domain (Development)
```
Application home page: http://localhost:3000
Privacy policy: http://localhost:3000/privacy (optional)
Terms of service: http://localhost:3000/terms (optional)
```

#### Authorized Domains
```
localhost
```

#### Scopes (Required)
- `../auth/userinfo.email`
- `../auth/userinfo.profile`
- `openid`

#### Test Users (Development)
Add your Gmail addresses for testing

### 3. Create OAuth 2.0 Credentials

#### Application Type
- **Web application**

#### Authorized JavaScript Origins
```
http://localhost:3000
http://localhost:8000
```

#### Authorized Redirect URIs
```
http://localhost:8000/api/auth/google/callback
```

### 4. Update Environment Variables

Copy your credentials to `.env`:

```env
# Replace with your actual values from Google Cloud Console
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

### 5. Generate Secure Secret Key

For the SECRET_KEY, generate a secure random string:

#### Option 1: Python
```python
import secrets
print(secrets.token_urlsafe(32))
```

#### Option 2: OpenSSL
```bash
openssl rand -base64 32
```

#### Option 3: Online Generator
Use: https://generate.plus/en/base64 (32 bytes)

### 6. Test OAuth Flow

#### Start Your Server
```bash
uvicorn app.main:app --reload
```

#### Test Endpoints
1. **API Docs**: http://localhost:8000/docs
2. **Google Login**: http://localhost:8000/api/auth/google/login
3. **Health Check**: http://localhost:8000/api/ai/health

#### OAuth Flow Test
1. Visit: `GET /api/auth/google/login`
2. Should redirect to Google OAuth
3. After approval, redirects to callback
4. Returns JWT token and user info

## 🔧 Common Issues & Solutions

### Issue: "redirect_uri_mismatch"
**Solution**: Ensure redirect URI in Google Console exactly matches:
```
http://localhost:8000/api/auth/google/callback
```

### Issue: "access_blocked"
**Solution**: 
- Add your email to "Test users" in OAuth consent screen
- Make sure scopes are correctly configured

### Issue: "invalid_client"
**Solution**: 
- Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
- Ensure no extra spaces or quotes

### Issue: "origin_mismatch"
**Solution**: Add to Authorized JavaScript origins:
```
http://localhost:8000
http://localhost:3000
```

## 🚀 Production Setup

For production deployment:

#### Update OAuth Consent Screen
- Change to "Production" status
- Remove test users restriction

#### Add Production Domains
```
Authorized JavaScript origins:
https://yourdomain.com
https://api.yourdomain.com

Authorized redirect URIs:
https://yourdomain.com/api/auth/google/callback
```

#### Environment Variables
```env
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback
FRONTEND_ORIGIN=https://yourdomain.com
ENVIRONMENT=production
```

## 📱 Frontend Integration

If you're building a frontend, here's how to integrate:

#### JavaScript Example
```javascript
// Initiate Google OAuth
const initiateGoogleAuth = async () => {
  const response = await fetch('/api/auth/google/login');
  const data = await response.json();
  window.location.href = data.authorization_url;
};

// Handle callback (if using SPA)
const handleCallback = async (code) => {
  const response = await fetch(`/api/auth/google/callback?code=${code}`);
  const data = await response.json();
  
  // Store token
  localStorage.setItem('token', data.access_token);
  
  // Use token for API calls
  const apiCall = await fetch('/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${data.access_token}`
    }
  });
};
```

## 🔐 Security Best Practices

1. **Never commit credentials** to version control
2. **Use HTTPS** in production
3. **Rotate secrets** regularly
4. **Implement rate limiting**
5. **Validate JWT tokens** properly
6. **Use secure session storage**

## 📞 Support

If you encounter issues:
1. Check Google Cloud Console logs
2. Verify API quotas and billing
3. Review OAuth consent screen status
4. Test with different browsers/incognito mode

---

**Ready to test?** Run your setup script and try the OAuth flow!
