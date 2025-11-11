# Clerk Authentication Setup Guide

This guide will help you set up Clerk authentication for the Kandih ToxWiki admin panel.

## 🔐 What You Need

1. **Clerk Account** - Sign up at [https://clerk.com](https://clerk.com) (free tier available)
2. **API Keys** from your Clerk dashboard

## 📋 Step-by-Step Setup

### 1. Create a Clerk Application

1. Go to [https://dashboard.clerk.com](https://dashboard.clerk.com)
2. Click **"+ Create application"**
3. Name it: **"Kandih ToxWiki"**
4. Choose authentication options:
   - ✅ Email
   - ✅ Google (optional)
   - ✅ GitHub (optional)
5. Click **"Create application"**

### 2. Get Your API Keys

After creating your application, you'll see your API keys:

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx...
CLERK_SECRET_KEY=sk_test_xxxxx...
```

### 3. Add Keys to Local Environment

Update your `.env.local` file:

```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_secret_here
```

### 4. Add Keys to Vercel (Production)

1. Go to your Vercel project dashboard
2. Navigate to **Settings → Environment Variables**
3. Add these variables:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_live_xxxxx...` | Production, Preview, Development |
| `CLERK_SECRET_KEY` | `sk_live_xxxxx...` | Production, Preview, Development |

⚠️ **Important**: Use **live** keys (`pk_live_` and `sk_live_`) for production!

### 5. Configure Clerk Domain Settings

In your Clerk dashboard:

1. Go to **Configure → Domains**
2. Add your production domain:
   - `https://your-app.vercel.app`
3. Click **"Save"**

### 6. Test Authentication

1. **Local Development**:
   ```bash
   npm run dev
   ```
   Visit `http://localhost:3000` and click **"Sign Up"**

2. **Production**:
   Deploy to Vercel and test the Sign Up/Log In buttons

## 🎨 OpenEvidence-Style UI

The authentication buttons match the OpenEvidence design from your screenshot:

- **Log In**: White button with border (`bg-white border border-slate-300`)
- **Sign Up**: Orange button (`bg-orange-500`)
- **User Button**: Displays avatar when logged in

## 🔒 Protected Routes

The following routes require authentication:

- `/admin` - Admin dashboard (protected by middleware)
- `/admin/*` - Any admin sub-routes

## 🧪 Testing

1. **Sign Up**: Create a test account
2. **Log In**: Verify you can access `/admin`
3. **Log Out**: Click user avatar → Sign Out
4. **Try Admin**: Visit `/admin` while logged out → should redirect to sign in

## 🛠️ Customization

### Change Button Styles

Edit `pages/index.tsx`:

```tsx
<SignInButton mode="modal">
  <button className="your-custom-classes">
    Log In
  </button>
</SignInButton>
```

### Customize Sign-In/Up Pages

In Clerk dashboard → **Customize → Appearance**, you can:
- Change colors
- Add logo
- Modify layout
- Add custom CSS

### Add More Auth Providers

In Clerk dashboard → **Configure → Social Connections**:
- Google
- GitHub
- Microsoft
- Apple
- And more...

## 📚 Additional Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Next.js Integration Guide](https://clerk.com/docs/quickstarts/nextjs)
- [Clerk Components](https://clerk.com/docs/components/overview)

## 🐛 Troubleshooting

### "Invalid publishable key"
- Make sure you copied the full key including `pk_test_` or `pk_live_`
- Check `.env.local` for typos
- Restart your dev server: `npm run dev`

### "Clerk: Network Error"
- Check your internet connection
- Verify domain is added in Clerk dashboard
- Clear browser cache and cookies

### Can't access admin page
- Verify you're signed in (check for user avatar)
- Check browser console for errors
- Ensure middleware.ts is in the root directory

## ✅ Success Checklist

- [ ] Clerk application created
- [ ] API keys added to `.env.local`
- [ ] API keys added to Vercel
- [ ] Domain configured in Clerk dashboard
- [ ] Sign Up works locally
- [ ] Log In works locally
- [ ] Admin page protected
- [ ] User button displays avatar
- [ ] Sign Out works
- [ ] Production deployment tested

---

**Need Help?** 
- Clerk Support: [https://clerk.com/support](https://clerk.com/support)
- Discord: [https://clerk.com/discord](https://clerk.com/discord)
