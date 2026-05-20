import { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AppContext } from "../App";

function Para({ children }) {
  return (
    <p className="text-[15px] leading-relaxed text-slate-600 dark:text-slate-300 mb-3">
      {children}
    </p>
  );
}

function Section({ title, children }) {
  return (
    <section className="mb-8">
      <h2 className="font-display text-[18px] font-bold mt-8 mb-3 text-ink dark:text-cream">
        {title}
      </h2>
      {children}
    </section>
  );
}

function AdCard({ title, description, icon, darkMode }) {
  return (
    <div
      className={`rounded-xl p-5 border ${
        darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200 shadow-sm"
      }`}
    >
      <div className="text-[24px] mb-3">{icon}</div>
      <h3 className="font-display text-[16px] font-bold mb-2 text-ink dark:text-cream">
        {title}
      </h3>
      <p className="text-[14px] leading-relaxed text-slate-500 dark:text-slate-400">
        {description}
      </p>
    </div>
  );
}

function BulletList({ items }) {
  return (
    <ul className="space-y-1 mb-3 pl-1">
      {items.map((item, i) => (
        <li
          key={i}
          className="flex items-start gap-3 text-[15px] leading-relaxed text-slate-600 dark:text-slate-300"
        >
          <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 mt-[7px] bg-mint" />
          {item}
        </li>
      ))}
    </ul>
  );
}

export default function AdvertisePage() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();

  const adOptions = [
    {
      icon: "@",
      title: "Newsletter Sponsorship",
      description:
        "A clearly-marked slot at the top or middle of the Venture OS daily, delivered each morning to founders, investors and operators who actually open their inbox before scrolling X.",
    },
    {
      icon: "#",
      title: "Site Display",
      description:
        "Tasteful, fast-loading display units on the homepage, section pages and individual articles. No pop-ups, no chumboxes, no scripts that slow the page down.",
    },
    {
      icon: "*",
      title: "Branded Series",
      description:
        "A multi-part editorial series produced by our partnerships studio, clearly labelled as branded. We bring the reporting craft; you bring the point of view worth making.",
    },
  ];

  return (
    <div className={`min-h-screen ${darkMode ? "bg-ink text-cream" : "bg-paper text-ink"}`}>
      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-[13px] mb-8" aria-label="Breadcrumb">
          <Link to="/" className="hover:underline text-mint">
            Home
          </Link>
          <span className={darkMode ? "text-slate-500" : "text-slate-400"}>/</span>
          <span className={darkMode ? "text-slate-300" : "text-slate-600"}>Advertise</span>
        </nav>

        {/* Hero */}
        <header className="mb-10">
          <h1 className="font-display font-bold text-[36px] sm:text-[44px] leading-tight mb-4">
            Advertise on Venture OS
          </h1>
          <div className="w-16 h-[3px] rounded mb-5 bg-mint" />
          <Para>
            Venture OS is where new money meets new ideas &mdash; a daily read for the people
            actually making capital allocation, hiring and product decisions inside India&rsquo;s
            startup economy, plus the global investors and operators paying close attention to it.
          </Para>
        </header>

        {/* Why Venture OS */}
        <Section title="Why Venture OS">
          <Para>
            Our readership is small on purpose. We are read by founders, partners at venture funds,
            CXOs at growth-stage companies, policy staffers and the journalists who cover them
            elsewhere. They open the Venture OS daily newsletter for sharp, original analysis on
            funding, M&amp;A and policy &mdash; not for SEO chum.
          </Para>
          <BulletList items={[
            "Daily newsletter with strong open and click-through rates among India + global startup decision-makers.",
            "An audience that reads to the end &mdash; average session times north of four minutes on long-form pieces.",
            "Heavy concentration in Bengaluru, Hyderabad, Mumbai, Delhi NCR, plus growing readership in Singapore, the Gulf and the Bay Area.",
            "No clickbait, no chumbox, no autoplay video. Your placement sits in a clean environment readers actually trust.",
          ]} />
        </Section>

        {/* Ad formats */}
        <Section title="Ways to partner">
          <Para>
            Three formats cover most of what brands want to do with us. All placements are clearly
            labelled and never blur the line between editorial and sponsored work.
          </Para>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
            {adOptions.map((opt, i) => (
              <AdCard key={i} {...opt} darkMode={darkMode} />
            ))}
          </div>
        </Section>

        {/* CTA */}
        <section
          className={`rounded-xl p-6 mb-10 border ${
            darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200 shadow-sm"
          }`}
        >
          <h2 className="font-display text-[18px] font-bold mb-3 text-ink dark:text-cream">
            Get in touch
          </h2>
          <p className="text-[14px] text-slate-500 dark:text-slate-400 mb-4">
            Send us a short note with the campaign, the timing and what you&rsquo;d like the
            audience to walk away with. Our partnerships desk replies inside two working days with
            a rate card and recommended formats.
          </p>
          <p className="text-[14px] text-slate-500 dark:text-slate-400">
            <span className="font-semibold text-slate-700 dark:text-slate-200">Email:</span>{" "}
            <a
              href="mailto:advertise@ventureos.in"
              className="hover:underline font-medium text-mint"
            >
              advertise@ventureos.in
            </a>
          </p>
        </section>

        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-[14px] font-medium hover:underline text-mint"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Go back
        </button>
      </div>
    </div>
  );
}
