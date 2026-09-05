import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Forest Substrate',
  description: 'Experimental existence and navigation substrate for The Forest.'
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
