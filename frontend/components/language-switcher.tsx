"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { localeInfo, locales, type Locale } from "@/i18n/config";
import { GlobeIcon } from "./icons";

/** Link to the same page in the other language. The proxy saves the choice in a cookie. */
export function LanguageSwitcher({ current, label }: { current: Locale; label: string }) {
  const pathname = usePathname();
  const rest = pathname.replace(/^\/[a-z]{2}(?=\/|$)/, "");
  const target = locales.find((l) => l !== current) ?? current;

  return (
    <Link
      href={`/${target}${rest}`}
      hrefLang={target}
      lang={target}
      aria-label={`${label}: ${localeInfo[target].name}`}
      className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:border-teal-300 hover:bg-teal-50 hover:text-teal-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
    >
      <GlobeIcon className="size-4" />
      {localeInfo[target].name}
    </Link>
  );
}
