import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Yoyo Shorts - AI Video Generator',
  description: 'Generate YouTube Shorts from any topic using AI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0a0a0a] text-white">
        {children}
      </body>
    </html>
  );
}
