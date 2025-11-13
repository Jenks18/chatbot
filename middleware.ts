import { authMiddleware } from '@clerk/nextjs/server'

export default authMiddleware({
  publicRoutes: [
    '/',
    '/api/chat',
    '/api/health',
    '/api/history/(.*)',
  ],
})

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
}

