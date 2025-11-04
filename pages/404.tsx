import React from 'react';
import Head from 'next/head';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <Head>
        <title>Page not found</title>
      </Head>
      <div className="max-w-lg text-center p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
        <h1 className="text-3xl font-bold mb-2 text-gray-900 dark:text-white">404 — Page not found</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">The page you requested could not be found.</p>
        <a href="/" className="inline-block px-4 py-2 bg-primary-600 text-white rounded">Go home</a>
      </div>
    </div>
  );
}
