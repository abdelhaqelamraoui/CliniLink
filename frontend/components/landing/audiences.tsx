import type { Dictionary } from "@/i18n/dictionaries/en";
import { BuildingIcon, CheckIcon, StethoscopeIcon, UserIcon } from "../icons";
import { SectionHeading } from "./section-heading";

const styles = [
  { Icon: UserIcon, tone: "bg-teal-50 text-teal-700 ring-teal-100" },
  { Icon: StethoscopeIcon, tone: "bg-sky-50 text-sky-700 ring-sky-100" },
  { Icon: BuildingIcon, tone: "bg-blue-50 text-blue-700 ring-blue-100" },
];

export function Audiences({ t }: { t: Dictionary["audiences"] }) {
  return (
    <section id="for-doctors" className="border-t border-slate-100 bg-slate-50/60 py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionHeading eyebrow={t.eyebrow} title={t.title} />
        <div className="mt-14 grid gap-5 md:grid-cols-3">
          {t.items.map((group, i) => {
            const { Icon, tone } = styles[i % styles.length];
            return (
              <article key={group.title} className="rounded-2xl border border-slate-200 bg-white p-7">
                <div className="flex items-center gap-3">
                  <span className={`grid size-11 place-items-center rounded-xl ring-1 ${tone}`}>
                    <Icon className="size-6" />
                  </span>
                  <h3 className="text-xl font-semibold text-slate-900">{group.title}</h3>
                </div>
                <ul className="mt-6 space-y-3">
                  {group.points.map((p) => (
                    <li key={p} className="flex gap-2.5 text-slate-700">
                      <CheckIcon className="mt-0.5 size-5 shrink-0 text-teal-600" />
                      {p}
                    </li>
                  ))}
                </ul>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
