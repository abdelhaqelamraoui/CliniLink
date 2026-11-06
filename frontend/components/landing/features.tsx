import type { Dictionary } from "@/i18n/dictionaries/en";
import { BellIcon, CalendarIcon, QueueIcon, ReportIcon, SearchIcon, StarIcon } from "../icons";
import { SectionHeading } from "./section-heading";

const icons = [SearchIcon, CalendarIcon, QueueIcon, BellIcon, ReportIcon, StarIcon];

export function Features({ t }: { t: Dictionary["features"] }) {
  return (
    <section id="features" className="border-t border-slate-100 bg-slate-50/60 py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionHeading eyebrow={t.eyebrow} title={t.title} subtitle={t.subtitle} />
        <ul className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {t.items.map((item, i) => {
            const Icon = icons[i % icons.length];
            return (
              <li key={item.title} className="group rounded-2xl border border-slate-200 bg-white p-6 transition hover:-translate-y-0.5 hover:border-teal-200 hover:shadow-lg hover:shadow-teal-900/5">
                <span className="grid size-11 place-items-center rounded-xl bg-gradient-to-br from-teal-50 to-blue-50 text-teal-700 ring-1 ring-teal-100">
                  <Icon className="size-6" />
                </span>
                <h3 className="mt-5 text-lg font-semibold text-slate-900">{item.title}</h3>
                <p className="mt-2 leading-7 text-slate-600">{item.description}</p>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
