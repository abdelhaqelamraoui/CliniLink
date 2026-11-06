type LogoProps = {
  /** Unique per page: the SVG gradient needs its own id. */
  id: string;
  className?: string;
  withText?: boolean;
};

export function LogoMark({ id, className }: { id: string; className?: string }) {
  const gradient = `cl-logo-${id}`;
  return (
    <svg viewBox="0 0 48 48" fill="none" aria-hidden="true" className={className}>
      <defs>
        <linearGradient id={gradient} x1="6" y1="4" x2="42" y2="44" gradientUnits="userSpaceOnUse">
          <stop stopColor="#14B8A6" />
          <stop offset="1" stopColor="#2563EB" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="13" fill={`url(#${gradient})`} />
      <rect x="19" y="9" width="10" height="30" rx="3.5" fill="#fff" />
      <rect x="9" y="19" width="30" height="10" rx="3.5" fill="#fff" />
      <circle cx="24" cy="24" r="5.5" fill="#0E7490" />
      <circle cx="24" cy="24" r="2.4" fill="#fff" />
    </svg>
  );
}

export function Logo({ id, className = "", withText = true }: LogoProps) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <LogoMark id={id} className="size-9 shrink-0" />
      {withText && (
        <span className="text-xl font-semibold tracking-tight text-slate-900" dir="ltr">
          Clini<span className="text-teal-600">Link</span>
        </span>
      )}
    </span>
  );
}
