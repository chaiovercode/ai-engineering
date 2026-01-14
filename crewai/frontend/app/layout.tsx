import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'zensar research',
  description: 'ai-powered research writeups',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
