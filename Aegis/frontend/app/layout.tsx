import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Aegis - Asset Intelligence Platform',
  description: 'AI-powered decision intelligence for critical electrical infrastructure',
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
