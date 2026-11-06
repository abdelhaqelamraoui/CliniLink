import Link from "next/link";
import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n/dictionaries/en";
import { Logo } from "../logo";
import { LanguageSwitcher } from "../language-switcher";

export function SiteHeader({ locale, t }: { locale: Locale; t: Dictionary["nav"] }) {
  const links = [
    { href: "#features", label: t.features },
    { href: "#how-it-works", label: t.howItWorks },
    { href: "#for-doctors", label: t.forDoctors },
  ];
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4 sm:px-6">
        <Link href={`/${locale}`} aria-label="CliniLink" className="rounded-lg focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-600">
          <Logo id="header" />
        </Link>
        <nav aria-label={t.menu} className="hidden md:block">
          <ul className="flex items-center gap-1">
            {links.map((l) => (
              <li key={l.href}>
                <a href={l.href} className="rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900">
                  {l.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <div className="ms-auto flex items-center gap-2 sm:gap-3">
          <LanguageSwitcher current={locale} label={t.language} />
          <a href="#get-started" className="hidden rounded-full px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:text-slate-950 sm:inline-block">
            {t.signIn}
          </a>
          <a href="#get-started" className="rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900">
            {t.getStarted}
          </a>
        </div>
      </div>
    </header>
  );
}
