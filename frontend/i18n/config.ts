export const locales = ["en", "ar"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "en";

/** Cookie that remembers the language a visitor picked. */
export const LOCALE_COOKIE = "NEXT_LOCALE";

export const localeInfo: Record<Locale, { name: string; dir: "ltr" | "rtl" }> = {
  en: { name: "English", dir: "ltr" },
  ar: { name: "العربية", dir: "rtl" },
};

export const hasLocale = (value: string): value is Locale => (locales as readonly string[]).includes(value);
