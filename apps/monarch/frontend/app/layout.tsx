import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Monarch Report Transformer",
  description: "Transform IC research reports into LinkedIn, Newsletter, and WhatsApp formats",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
