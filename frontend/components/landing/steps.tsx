import type { Dictionary } from "@/i18n/dictionaries/en";
import { SectionHeading } from "./section-heading";

export function Steps({ t, locale }: { t: Dictionary["steps"]; locale: string }) {
  const number = new Intl.NumberFormat(locale);
  return (
    <section id="how-it-works" className="py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionHeading eyebrow={t.eyebrow} title={t.title} />
        <ol className="relative mt-14 grid gap-10 md:grid-cols-3 md:gap-8">
          <div aria-hidden="true" className="absolute inset-x-[16%] top-6 hidden h-px bg-gradient-to-r from-teal-200 via-sky-200 to-blue-200 md:block" />
          {t.items.map((step, i) => (
            <li key={step.title} className="relative text-center">
              <span className="relative mx-auto grid size-12 place-items-center rounded-full bg-white text-lg font-bold text-teal-700 shadow-md shadow-teal-900/10 ring-1 ring-teal-100">
                {number.format(i + 1)}
              </span>
              <h3 className="mt-5 text-lg font-semibold text-slate-900">{step.title}</h3>
              <p className="mx-auto mt-2 max-w-xs leading-7 text-slate-600">{step.description}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
