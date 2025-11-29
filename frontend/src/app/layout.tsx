import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Paper2Video - Transform Research Papers into Videos',
  description: 'Convert your research papers into engaging video presentations with AI-powered summarization, narration, and avatars.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
          <nav className="border-b border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <a href="/" className="flex items-center space-x-2">
                    <svg className="w-8 h-8 text-primary-600" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M4 8L12 4L20 8V16L12 20L4 16V8Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M12 12L12 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      <path d="M12 12L20 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      <path d="M12 12L4 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      <circle cx="12" cy="12" r="2" fill="currentColor"/>
                    </svg>
                    <span className="text-xl font-bold text-slate-900 dark:text-white">Paper2Video</span>
                  </a>
                </div>
                <div className="flex items-center space-x-4">
                  <a href="/" className="text-slate-600 hover:text-primary-600 dark:text-slate-300 dark:hover:text-primary-400 font-medium">
                    Home
                  </a>
                  <a href="/dashboard" className="text-slate-600 hover:text-primary-600 dark:text-slate-300 dark:hover:text-primary-400 font-medium">
                    Dashboard
                  </a>
                </div>
              </div>
            </div>
          </nav>
          <main>{children}</main>
          <footer className="border-t border-slate-200 dark:border-slate-700 py-8 mt-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-500 dark:text-slate-400">
              <p>© 2024 Paper2Video. Transform your research into engaging presentations.</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
