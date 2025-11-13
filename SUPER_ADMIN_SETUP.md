# Super Admin Setup Guide

## Overview

The chatbot now supports two tiers of user access:

1. **Regular Users**: Can only see their own chat sessions when they log in
2. **Super Admin**: Can see ALL chat sessions from all users

## How It Works

### User Authentication
- User ID from Clerk is automatically stored with each chat message
- Sessions are filtered based on the logged-in user's ID
- Admin page loads only user-specific sessions by default

### Super Admin Role
- Super admin status is determined by checking: `user.publicMetadata.role === 'admin'`
- Super admins bypass the user_id filter and see all sessions
- Visual indicator shows "Viewing All Users" for super admins

## Setting Up a Super Admin

### Option 1: Clerk Dashboard (Recommended)

1. Go to your Clerk Dashboard: https://dashboard.clerk.com
2. Navigate to **Users**
3. Click on the user you want to make a super admin
4. Scroll to **Public Metadata** section
5. Click **Edit**
6. Add the following JSON:
   ```json
   {
     "role": "admin"
   }
   ```
7. Click **Save**

### Option 2: Clerk API

You can programmatically set this using the Clerk Backend API:

```javascript
import { clerkClient } from '@clerk/nextjs/server';

await clerkClient.users.updateUserMetadata(userId, {
  publicMetadata: {
    role: 'admin'
  }
});
```

## Testing

### Test Regular User Access
1. Log in with a regular user account (no admin role)
2. Go to `/admin` page
3. You should see:
   - Header: "Kandih ToxWiki — Admin"
   - Subtitle: "Welcome, [Name] • Your Sessions Only"
   - Only sessions you created appear in the list

### Test Super Admin Access
1. Log in with a user that has `publicMetadata.role = "admin"`
2. Go to `/admin` page
3. You should see:
   - Header: "Kandih ToxWiki — Super Admin"
   - Subtitle: "Welcome, [Name] • Viewing All Users"
   - ALL sessions from all users appear in the list

## Security Notes

- **publicMetadata** is readable by the frontend, so users can see their own role
- This is intentional - we want them to know if they're an admin
- The actual authorization happens server-side: the backend filters sessions based on user_id
- Super admins cannot modify other users' data, only view it

## Removing Super Admin Access

To remove super admin access from a user:

1. Go to Clerk Dashboard > Users > Select User
2. Edit Public Metadata
3. Remove the `"role": "admin"` field or set it to a different value
4. User will immediately lose super admin privileges on next page load

## Future Enhancements

Potential improvements:
- Add more granular roles (e.g., "moderator", "analyst")
- Add user management UI for admins to promote/demote users
- Add audit logging for admin actions
- Add session export/download functionality for admins
