// English is the source dictionary: its shape is the type every other language must match.
const en = {
  meta: {
    title: "CliniLink · Book doctors, follow live queues",
    description:
      "Find a doctor, book an appointment in seconds and follow your place in the waiting queue live. CliniLink connects patients, doctors and clinics.",
  },
  nav: {
    features: "Features",
    howItWorks: "How it works",
    forDoctors: "For doctors",
    signIn: "Sign in",
    getStarted: "Get started",
    language: "Language",
    menu: "Menu",
  },
  hero: {
    badge: "Healthcare appointments, made simple",
    titleStart: "Book the right doctor.",
    titleHighlight: "Skip the waiting room.",
    subtitle:
      "CliniLink connects patients, doctors and clinics. Find a doctor, book a free slot in seconds, and follow your place in the queue live from your phone.",
    primaryCta: "Find a doctor",
    secondaryCta: "I'm a doctor",
    points: ["No double bookings", "Live queue updates", "Email reminders"],
  },
  queueCard: {
    live: "Live",
    doctorName: "Dr. Sara Haddad",
    doctorSpecialty: "Cardiology · Today",
    nowServing: "Now serving",
    yourPosition: "Your position",
    estimatedTime: "Estimated time",
    ahead: "2 patients ahead of you",
    waiting: "Waiting",
    called: "Called",
    you: "You",
    booked: "Appointment confirmed",
    bookedDetail: "Tue, 10 Nov · 10:30",
  },
  features: {
    eyebrow: "Features",
    title: "Everything a visit needs, in one place",
    subtitle: "From the first search to the medical report, every step of the appointment is covered.",
    items: [
      {
        title: "Find the right doctor",
        description: "Search by name, specialty, location, price and patient rating, and see each doctor's location on the map.",
      },
      {
        title: "Book in seconds",
        description: "See real availability and reserve a slot instantly. A slot can never be booked twice.",
      },
      {
        title: "Live waiting queues",
        description: "Follow your place in the doctor's queue in real time, and arrive just when it's your turn.",
      },
      {
        title: "Reminders and alerts",
        description: "Get a confirmation, a reminder before your visit, and an alert if anything changes.",
      },
      {
        title: "Your medical reports",
        description: "Read your consultation reports, diagnoses and prescriptions whenever you need them.",
      },
      {
        title: "Ratings you can trust",
        description: "Only patients who completed a visit can rate a doctor, so reviews come from real consultations.",
      },
    ],
  },
  steps: {
    eyebrow: "How it works",
    title: "Three steps to your appointment",
    items: [
      { title: "Search", description: "Choose a specialty or a doctor near you and compare prices and ratings." },
      { title: "Book", description: "Pick a free slot. Your appointment is confirmed right away by email." },
      { title: "Arrive on time", description: "Check the live queue on the day and walk in when it's your turn." },
    ],
  },
  audiences: {
    eyebrow: "For everyone in the clinic",
    title: "Built for patients, doctors and staff",
    items: [
      {
        title: "Patients",
        points: ["Book, reschedule or cancel online", "See your place in the queue", "Keep your reports in one place"],
      },
      {
        title: "Doctors",
        points: ["Set working hours and prices", "See the day's appointments", "Write reports after each visit"],
      },
      {
        title: "Clinics and staff",
        points: ["Manage doctor and room queues", "Call the next patient in one tap", "Handle absences without the phone calls"],
      },
    ],
  },
  cta: {
    title: "Ready for your next appointment?",
    subtitle: "Create a free account and book your first visit in under a minute.",
    primary: "Create an account",
    secondary: "Sign in",
  },
  footer: {
    tagline: "Healthcare appointments and live queues for patients, doctors and clinics.",
    rights: "All rights reserved.",
    product: "Product",
    company: "CliniLink",
    about: "About",
    contact: "Contact",
    privacy: "Privacy",
  },
};

type Widen<T> = T extends string ? string : T extends readonly (infer U)[] ? Widen<U>[] : { [K in keyof T]: Widen<T[K]> };
export type Dictionary = Widen<typeof en>;

export default en satisfies Dictionary;
