import type { Metadata } from "next";
import "./globals.css";
import "./littlefinger.css";
import "./account.css";
import catalogue from "../public/specs/workbook-catalogue-report.json";

export const metadata: Metadata = {
  metadataBase: new URL("https://little-world-playroom.atikadewi.chatgpt.site"),
  title: "Littlefinger Activities · Bermain & belajar",
  description: `${catalogue.worksheets.toLocaleString("id-ID")} worksheet interaktif dalam ${catalogue.categories} kategori. Buku aktivitas untuk bermain dan menemukan hal kecil bersama.`,
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <body className="antialiased">{children}</body>
    </html>
  );
}
