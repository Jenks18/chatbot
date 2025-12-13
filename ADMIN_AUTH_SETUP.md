# Admin Dashboard Access Control

## Overview

The admin dashboard (`/admin`) now requires password authentication to prevent unauthorized access to user conversations and analytics.

## Setup

### 1. Set Admin Password

Add this environment variable to your Vercel project:

```bash
NEXT_PUBLIC_ADMIN_PASSWORD=your-secure-password-here
```

**In Vercel Dashboard:**
1. Go to your project settings
2. Environment Variables
3. Add: `NEXT_PUBLIC_ADMIN_PASSWORD` = `your-secure-password`
4. Redeploy

### 2. Default Password (Development)

If no environment variable is set, the default password is: `admin123`

⚠️ **Change this in production!**

## How It Works

1. User visits `/admin`
2. Login form appears
3. Password is checked against `NEXT_PUBLIC_ADMIN_PASSWORD`
4. On success, auth is stored in `sessionStorage`
5. User can access dashboard until they close the browser tab
6. "Logout" button clears authentication

## Security Notes

### Session-Based (Not Cookie)
- Uses `sessionStorage` (clears when tab closes)
- No cookies or JWT tokens
- Simple but effective for single admin user

### Frontend-Only Check
- ⚠️ This is **client-side only** authentication
- API endpoints are still accessible if someone knows the URLs
- Good enough for: Solo developer, private project, non-sensitive data
- NOT good enough for: Multiple admins, sensitive data, production apps with many users

### To Add Backend Auth

If you need real security, you'd need to:
1. Add auth headers to all API requests
2. Validate tokens on backend endpoints
3. Use Clerk or NextAuth for proper authentication
4. Add role-based access control (RBAC)

But for a personal medical chatbot where you're the only admin, this simple password check works fine.

## Features Removed

Cleaned up unused drug interaction features:

- ❌ "Fetch & Update References" pipeline button
- ❌ `interactions` table queries
- ❌ `/api/admin/interactions` endpoint
- ❌ `/api/admin/pipeline/fetch-references` endpoint

The app now focuses purely on conversational Q&A with PubMed references, not structured drug interaction storage.

## Testing

1. Visit `/admin`
2. Enter password
3. Access dashboard
4. Click "Logout" to test re-authentication
5. Close tab and reopen - should require password again
