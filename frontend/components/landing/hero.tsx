import type { Dictionary } from "@/i18n/dictionaries/en";
import { ArrowIcon, CheckIcon } from "../icons";
import { QueueCard } from "./queue-card";

export function Hero({ t, card }: { t: Dictionary["hero"]; card: Dictionary["queueCard"] }) {
  return (
    <section className="relative overflow-hidden">
      <div aria-hidden="true" className="absolute inset-0 -z-10 bg-[radial-gradient(60rem_30rem_at_50%_-10%,theme(colors.teal.50),transparent)]" />
      <div aria-hidden="true" className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,theme(colors.slate.100)_1px,transparent_1px),linear-gradient(to_bottom,theme(colors.slate.100)_1px,transparent_1px)] bg-[size:3.5rem_3.5rem] [mask-image:radial-gradient(ellipse_at_top,black_30%,transparent_75%)]" />

      <div className="mx-auto grid max-w-6xl items-center gap-16 px-4 pb-24 pt-14 sm:px-6 sm:pt-20 lg:grid-cols-[1.1fr_1fr] lg:gap-12 lg:pb-28">
        <div className="text-center lg:text-start">
          <p className="inline-flex items-center gap-2 rounded-full border border-teal-200 bg-white/80 px-3 py-1 text-sm font-medium text-teal-800 shadow-sm">
            <span className="size-1.5 rounded-full bg-teal-500" />
            {t.badge}
          </p>
          <h1 className="mt-6 text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl lg:text-6xl lg:leading-[1.08]">
            {t.titleStart}{" "}
            <span className="bg-gradient-to-r from-teal-600 to-blue-600 bg-clip-text text-transparent">{t.titleHighlight}</span>
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-slate-600 lg:mx-0">{t.subtitle}</p>

          <div className="mt-9 flex flex-col items-center gap-3 sm:flex-row sm:justify-center lg:justify-start">
            <a href="#features" className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-teal-600 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-teal-600/25 transition hover:bg-teal-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600 sm:w-auto">
              {t.primaryCta}
              <ArrowIcon className="size-5 transition group-hover:translate-x-0.5 rtl:-scale-x-100 rtl:group-hover:-translate-x-0.5" />
            </a>
            <a href="#for-doctors" className="inline-flex w-full items-center justify-center rounded-full border border-slate-300 bg-white px-6 py-3 text-base font-semibold text-slate-800 transition hover:border-slate-400 hover:bg-slate-50 sm:w-auto">
              {t.secondaryCta}
            </a>
          </div>

          <ul className="mt-9 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-slate-600 lg:justify-start">
            {t.points.map((p) => (
              <li key={p} className="flex items-center gap-1.5">
                <CheckIcon className="size-4 text-teal-600" />
                {p}
              </li>
            ))}
          </ul>
        </div>

        <QueueCard t={card} />
      </div>
    </section>
  );
}
