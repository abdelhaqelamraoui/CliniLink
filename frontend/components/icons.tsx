import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

function Icon({ children, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round"
      strokeLinejoin="round" aria-hidden="true" {...props}>
      {children}
    </svg>
  );
}

export const SearchIcon = (p: IconProps) => <Icon {...p}><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></Icon>;
export const CalendarIcon = (p: IconProps) => <Icon {...p}><rect x="3" y="4.5" width="18" height="16" rx="2.5" /><path d="M3 9.5h18M8 3v3M16 3v3" /><path d="m9 15 2 2 4-4" /></Icon>;
export const QueueIcon = (p: IconProps) => <Icon {...p}><circle cx="6" cy="7" r="2.2" /><circle cx="6" cy="17" r="2.2" /><path d="M11 7h9M11 17h9M11 12h6" /><circle cx="6" cy="12" r="0.6" fill="currentColor" /></Icon>;
export const BellIcon = (p: IconProps) => <Icon {...p}><path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15z" /><path d="M10 20.5a2 2 0 0 0 4 0" /></Icon>;
export const ReportIcon = (p: IconProps) => <Icon {...p}><path d="M7 3h7l5 5v12a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" /><path d="M14 3v5h5M9.5 13h5M12 10.5v5" /></Icon>;
export const StarIcon = (p: IconProps) => <Icon {...p}><path d="m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z" /></Icon>;
export const CheckIcon = (p: IconProps) => <Icon {...p}><path d="m5 12.5 4.5 4.5L19 7.5" /></Icon>;
export const ArrowIcon = (p: IconProps) => <Icon {...p}><path d="M5 12h14M13 6l6 6-6 6" /></Icon>;
export const GlobeIcon = (p: IconProps) => <Icon {...p}><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c2.5 2.6 3.7 5.6 3.7 9s-1.2 6.4-3.7 9c-2.5-2.6-3.7-5.6-3.7-9S9.5 5.6 12 3z" /></Icon>;
export const UserIcon = (p: IconProps) => <Icon {...p}><circle cx="12" cy="8" r="4" /><path d="M4.5 20.5c1.2-3.8 4-5.5 7.5-5.5s6.3 1.7 7.5 5.5" /></Icon>;
export const StethoscopeIcon = (p: IconProps) => <Icon {...p}><path d="M6 3H5v6a5 5 0 0 0 10 0V3h-1" /><path d="M10 14v1.5a5 5 0 0 0 10 0V13" /><circle cx="20" cy="11" r="2" /></Icon>;
export const BuildingIcon = (p: IconProps) => <Icon {...p}><path d="M4 21V5a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v16M15 9h4a1 1 0 0 1 1 1v11M2.5 21h19" /><path d="M8 8h3M8 12h3M8 16h3M9.5 6.5v3" /></Icon>;
