import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
import { Logo } from "@/components/logo";
import "./globals.css";

const geist = Geist({ variable: "--font-geist", subsets: ["latin"] });

export const metadata: Metadata = { title: "404 · CliniLink" };

// Shown for URLs outside /en and /ar, where there is no layout (and so no language) yet.
export default function GlobalNotFound() {
  return (
    <html lang="en" className={`${geist.variable} antialiased`}>
      <body className="grid min-h-dvh place-items-center px-4">
        <main className="text-center">
          <Logo id="404" className="justify-center" />
          <p className="mt-10 text-6xl font-bold text-teal-600">404</p>
          <h1 className="mt-3 text-xl font-semibold text-slate-900">Page not found</h1>
          <p className="mt-1 text-slate-600" lang="ar" dir="rtl">الصفحة غير موجودة</p>
          <div className="mt-8 flex justify-center gap-3">
            <Link href="/en" className="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-800">Home</Link>
            <Link href="/ar" lang="ar" className="rounded-full border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-800 hover:bg-slate-50">الرئيسية</Link>
          </div>
        </main>
      </body>
    </html>
  );
}
