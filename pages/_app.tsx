import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { ClerkProvider } from '@clerk/nextjs'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ClerkProvider 
      appearance={{
        variables: { colorPrimary: '#10b981' }
      }}
    >
      <Component {...pageProps} />
    </ClerkProvider>
  )
}
