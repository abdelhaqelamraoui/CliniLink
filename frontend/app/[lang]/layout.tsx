import type { Metadata, Viewport } from "next";
import { Geist, IBM_Plex_Sans_Arabic } from "next/font/google";
import { localeInfo, locales } from "@/i18n/config";
import { getDictionary, getLocale } from "@/i18n/get-dictionary";
import "../globals.css";

const geist = Geist({ variable: "--font-geist", subsets: ["latin"] });
const plexArabic = IBM_Plex_Sans_Arabic({
  variable: "--font-plex-arabic",
  subsets: ["arabic"],
  weight: ["400", "500", "600", "700"],
});

// Only /en and /ar exist; any other first segment is a 404.
export const dynamicParams = false;
export function generateStaticParams() {
  return locales.map((lang) => ({ lang }));
}

export async function generateMetadata(): Promise<Metadata> {
  const [locale, t] = await Promise.all([getLocale(), getDictionary()]);
  return {
    metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"),
    title: t.meta.title,
    description: t.meta.description,
    applicationName: "CliniLink",
    alternates: {
      canonical: `/${locale}`,
      languages: { en: "/en", ar: "/ar", "x-default": "/" },
    },
    openGraph: {
      title: t.meta.title,
      description: t.meta.description,
      siteName: "CliniLink",
      locale: locale === "ar" ? "ar_AR" : "en_US",
      type: "website",
    },
  };
}

export const viewport: Viewport = { themeColor: "#0d9488" };

export default async function RootLayout({ children }: LayoutProps<"/[lang]">) {
  const locale = await getLocale();
  return (
    <html lang={locale} dir={localeInfo[locale].dir} className={`${geist.variable} ${plexArabic.variable} antialiased`}>
      <body className="flex min-h-dvh flex-col">{children}</body>
    </html>
  );
}
