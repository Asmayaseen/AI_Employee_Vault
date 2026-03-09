import type { Metadata } from "next";
import "./globals.css";
import LayoutShell from "@/components/layout-shell";

export const metadata: Metadata = {
  title: "AI Employee Dashboard",
  description: "AI Employee System v3.0 - Platinum Tier Dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-[#F5F7FA] text-[#0A0A0A] antialiased dark:bg-[#0A0A0A] dark:text-[#F0F0F0]">
        <LayoutShell>{children}</LayoutShell>
      </body>
    </html>
  );
}
