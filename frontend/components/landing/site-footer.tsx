import type { Dictionary } from "@/i18n/dictionaries/en";
import { Logo } from "../logo";

export function SiteFooter({ t, nav }: { t: Dictionary["footer"]; nav: Dictionary["nav"] }) {
  const year = new Date().getFullYear();
  const columns = [
    { title: t.product, links: [{ href: "#features", label: nav.features }, { href: "#how-it-works", label: nav.howItWorks }, { href: "#for-doctors", label: nav.forDoctors }] },
    { title: t.company, links: [{ href: "#", label: t.about }, { href: "#", label: t.contact }, { href: "#", label: t.privacy }] },
  ];
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-14 sm:px-6 md:grid-cols-[2fr_1fr_1fr]">
        <div>
          <Logo id="footer" />
          <p className="mt-4 max-w-sm leading-7 text-slate-600">{t.tagline}</p>
        </div>
        {columns.map((col) => (
          <nav key={col.title} aria-label={col.title}>
            <h2 className="text-sm font-semibold text-slate-900">{col.title}</h2>
            <ul className="mt-4 space-y-3">
              {col.links.map((l) => (
                <li key={l.label}>
                  <a href={l.href} className="text-slate-600 transition hover:text-teal-700">{l.label}</a>
                </li>
              ))}
            </ul>
          </nav>
        ))}
      </div>
      <div className="border-t border-slate-100">
        <p className="mx-auto max-w-6xl px-4 py-6 text-sm text-slate-500 sm:px-6">
          © <span dir="ltr">{year}</span> CliniLink. {t.rights}
        </p>
      </div>
    </footer>
  );
}
