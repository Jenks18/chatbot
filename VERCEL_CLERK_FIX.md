# Fix Vercel Clerk Middleware Error

## Error
```
500: INTERNAL_SERVER_ERROR
Code: MIDDLEWARE_INVOCATION_FAILED
```

This happens when clicking the Admin button because Clerk authentication isn't configured on Vercel.

## Quick Fix (5 minutes)

### Step 1: Get Your Clerk Keys

1. Go to https://dashboard.clerk.com
2. Select your application
3. Click **API Keys** in the left sidebar
4. Copy both keys:
   - **Publishable Key** (starts with `pk_test_` or `pk_live_`)
   - **Secret Key** (starts with `sk_test_` or `sk_live_`)

### Step 2: Add Keys to Vercel

1. Go to https://vercel.com/dashboard
2. Click your `chatbot` project
3. Go to **Settings** → **Environment Variables**
4. Add these two variables:

   **Variable 1:**
   ```
   Name: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
   Value: pk_test_xxxxxxxxx... (your publishable key)
   Environments: ✓ Production ✓ Preview ✓ Development
   ```

   **Variable 2:**
   ```
   Name: CLERK_SECRET_KEY
   Value: sk_test_xxxxxxxxx... (your secret key)
   Environments: ✓ Production ✓ Preview ✓ Development
   ```

5. Click **Save** for each

### Step 3: Redeploy

1. Go to **Deployments** tab
2. Click the **︙** (three dots) on the latest deployment
3. Click **Redeploy**
4. Wait ~30 seconds for deployment to complete

### Step 4: Test

1. Go to your live site (e.g., `https://chatbot.vercel.app`)
2. Click the **Admin** button in top-right
3. You should now see the Clerk sign-in page (not a 500 error)

## Why This Happens

The middleware runs on Vercel but can't find Clerk API keys, so it crashes with:
```
MIDDLEWARE_INVOCATION_FAILED
```

Once you add the keys, Clerk middleware will work properly and redirect users to sign in.

## What Works After Fix

- ✅ Homepage works normally (no auth required)
- ✅ Chat works without login (no auth required)
- ✅ Admin button → redirects to Clerk sign-in
- ✅ After login → shows admin dashboard
- ✅ Regular users see only their chat history
- ✅ Super admins (with `role: "admin"` in publicMetadata) see all users' history

## Still Having Issues?

Check if keys are actually set:
1. Vercel → Settings → Environment Variables
2. Look for both `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY`
3. Make sure they're checked for **Production**
4. Make sure you clicked **Redeploy** (just saving env vars isn't enough)
