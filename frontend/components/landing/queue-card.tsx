import type { Dictionary } from "@/i18n/dictionaries/en";
import { CalendarIcon, CheckIcon, StethoscopeIcon } from "../icons";

/** Illustration of the live queue a patient sees (mirrors the queue-resource-service data). */
export function QueueCard({ t }: { t: Dictionary["queueCard"] }) {
  const rows = [
    { n: 12, status: t.called, time: "09:45", tone: "called" },
    { n: 13, status: t.waiting, time: "10:00", tone: "waiting" },
    { n: 14, status: t.waiting, time: "10:15", tone: "waiting" },
    { n: 15, status: t.you, time: "10:30", tone: "you" },
  ] as const;

  return (
    <div className="relative mx-auto w-full max-w-md">
      <div aria-hidden="true" className="absolute -inset-6 -z-10 rounded-[2.5rem] bg-gradient-to-br from-teal-200/60 via-sky-200/40 to-blue-300/50 blur-2xl" />

      <div className="rounded-3xl border border-slate-200 bg-white p-5 pb-12 shadow-xl shadow-slate-900/10 sm:p-6 sm:pb-12">
        <div className="flex items-center gap-3">
          <span className="grid size-11 place-items-center rounded-2xl bg-teal-50 text-teal-700">
            <StethoscopeIcon className="size-6" />
          </span>
          <div className="min-w-0">
            <p className="truncate font-semibold text-slate-900">{t.doctorName}</p>
            <p className="text-sm text-slate-500">{t.doctorSpecialty}</p>
          </div>
          <span className="ms-auto inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
            </span>
            {t.live}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-3 gap-2 rounded-2xl bg-slate-50 p-3 text-center">
          <div>
            <p className="text-xs text-slate-500">{t.nowServing}</p>
            <p className="mt-1 text-2xl font-bold tabular-nums text-slate-900">#12</p>
          </div>
          <div className="rounded-xl bg-white py-1 shadow-sm ring-1 ring-teal-100">
            <p className="text-xs font-medium text-teal-700">{t.yourPosition}</p>
            <p className="mt-1 text-2xl font-bold tabular-nums text-teal-700">3</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">{t.estimatedTime}</p>
            <p className="mt-1 text-2xl font-bold tabular-nums text-slate-900" dir="ltr">10:30</p>
          </div>
        </div>
        <p className="mt-2 text-center text-xs font-medium text-teal-700">{t.ahead}</p>

        <ul className="mt-4 space-y-2">
          {rows.map((r) => (
            <li
              key={r.n}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm ${
                r.tone === "you" ? "bg-teal-600 text-white" : r.tone === "called" ? "bg-sky-50 text-sky-900" : "text-slate-700"
              }`}
            >
              <span className={`w-9 font-semibold tabular-nums ${r.tone === "you" ? "text-white" : "text-slate-900"}`}>#{r.n}</span>
              <span className="font-medium">{r.status}</span>
              <span className={`ms-auto tabular-nums ${r.tone === "you" ? "text-teal-50" : "text-slate-500"}`} dir="ltr">{r.time}</span>
            </li>
          ))}
        </ul>
              </div>

      <div className="absolute -bottom-6 start-[-0.75rem] flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-lg shadow-slate-900/10 sm:start-[-2rem]">
        <span className="grid size-9 place-items-center rounded-full bg-emerald-100 text-emerald-700">
          <CheckIcon className="size-5" />
        </span>
        <div>
          <p className="text-sm font-semibold text-slate-900">{t.booked}</p>
          <p className="flex items-center gap-1 text-xs text-slate-500">
            <CalendarIcon className="size-3.5" />
            {t.bookedDetail}
          </p>
        </div>
      </div>
    </div>
  );
}
