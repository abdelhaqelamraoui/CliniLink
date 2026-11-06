import type { Dictionary } from "@/i18n/dictionaries/en";
import { ArrowIcon } from "../icons";
import { LogoMark } from "../logo";

export function CallToAction({ t }: { t: Dictionary["cta"] }) {
  return (
    <section id="get-started" className="py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-teal-600 via-cyan-700 to-blue-700 px-6 py-16 text-center shadow-xl shadow-teal-900/20 sm:px-12">
          <LogoMark id="cta" className="absolute -end-10 -top-10 size-56 rotate-12 opacity-10" />
          <h2 className="relative text-3xl font-bold tracking-tight text-white sm:text-4xl">{t.title}</h2>
          <p className="relative mx-auto mt-4 max-w-xl text-lg text-teal-50">{t.subtitle}</p>
          <div className="relative mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <a href="#get-started" className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-white px-6 py-3 font-semibold text-teal-800 shadow-md transition hover:bg-teal-50 sm:w-auto">
              {t.primary}
              <ArrowIcon className="size-5 rtl:-scale-x-100" />
            </a>
            <a href="#get-started" className="inline-flex w-full items-center justify-center rounded-full border border-white/40 px-6 py-3 font-semibold text-white transition hover:bg-white/10 sm:w-auto">
              {t.secondary}
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
