import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/i18n/LanguageProvider";

export const metadata: Metadata = {
  title: "Vietnamese Food Recognition",
  description: "Upload a Vietnamese dish photo and see its nutrition.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-neutral-50 font-sans text-neutral-900">
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
