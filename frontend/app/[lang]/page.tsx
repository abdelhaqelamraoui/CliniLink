import { Audiences } from "@/components/landing/audiences";
import { CallToAction } from "@/components/landing/call-to-action";
import { Features } from "@/components/landing/features";
import { Hero } from "@/components/landing/hero";
import { SiteFooter } from "@/components/landing/site-footer";
import { SiteHeader } from "@/components/landing/site-header";
import { Steps } from "@/components/landing/steps";
import { getDictionary, getLocale } from "@/i18n/get-dictionary";

export default async function LandingPage() {
  const [locale, t] = await Promise.all([getLocale(), getDictionary()]);
  return (
    <>
      <SiteHeader locale={locale} t={t.nav} />
      <main className="flex-1">
        <Hero t={t.hero} card={t.queueCard} />
        <Features t={t.features} />
        <Steps t={t.steps} locale={locale} />
        <Audiences t={t.audiences} />
        <CallToAction t={t.cta} />
      </main>
      <SiteFooter t={t.footer} nav={t.nav} />
    </>
  );
}
