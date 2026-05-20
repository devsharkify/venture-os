import { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AppContext } from "../App";

const coverage = [
  "Funding rounds",
  "M&A",
  "IPOs",
  "Policy",
  "Deep Tech",
  "SaaS",
  "Fintech",
  "Climate",
];

const principles = [
  {
    title: "Independence",
    body: "We have no investors in the companies we cover. No sweetheart embargoes, no quiet edits after publication, no founders allowed to vet copy.",
  },
  {
    title: "Original reporting",
    body: "We do not retype press releases. Every story leans on primary sources - operators, term sheets, filings, and the people closest to the deal.",
  },
  {
    title: "Source attribution",
    body: "When a number or claim comes from somewhere else, we say so and link to it. Readers deserve to trace the reporting back to its origin.",
  },
];

const team = [
  { name: "Riya Menon", role: "Editor-in-Chief" },
  { name: "Arjun Bose", role: "Markets Lead" },
  { name: "Sneha Kulkarni", role: "Funding Desk" },
  { name: "Karan Iyer", role: "Deep Tech" },
];

export default function AboutPage() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();

  return (
    <div className={`min-h-screen ${darkMode ? "bg-ink text-cream" : "bg-paper text-ink"}`}>
      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-[13px] mb-8" aria-label="Breadcrumb">
          <Link to="/" className={`hover:underline ${darkMode ? "text-mint" : "text-mint"}`}>
            Home
          </Link>
          <span className={darkMode ? "text-slate-500" : "text-slate-400"}>/</span>
          <span className={darkMode ? "text-slate-300" : "text-slate-600"}>About</span>
        </nav>

        {/* Hero */}
        <header className="mb-12">
          <h1 className="font-display text-[36px] sm:text-[44px] font-bold leading-tight mb-4">
            About Mint Street
          </h1>
          <div className="w-16 h-[3px] rounded mb-6 bg-mint" />
          <p className="text-[17px] leading-relaxed font-medium text-slate-600 dark:text-slate-300 max-w-2xl italic">
            Where new money meets new ideas.
          </p>
          <p className="text-[15px] leading-relaxed text-slate-600 dark:text-slate-300 mt-5">
            We started Mint Street because Indian startup journalism deserves better than recycled
            press releases and breathless valuation theatre. A generation of founders, operators and
            allocators are quietly remaking the country&rsquo;s balance sheet &mdash; from climate
            hardware in Bengaluru to fintech rails out of Hyderabad &mdash; and they need a publication
            that takes the work seriously without losing its sense of humour about it.
          </p>
          <p className="text-[15px] leading-relaxed text-slate-600 dark:text-slate-300 mt-3">
            Mint Street is independent, India-first and obsessively interested in primary sources.
            We cover the deals, the policy and the people, but we try hardest on the stories you
            cannot find anywhere else.
          </p>
        </header>

        {/* What we cover */}
        <section className="mb-10">
          <h2 className="font-display text-[18px] font-bold mt-8 mb-3 text-ink dark:text-cream">
            What we cover
          </h2>
          <ul className="space-y-2">
            {coverage.map((cat) => (
              <li key={cat} className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full flex-shrink-0 bg-mint" />
                <span className="text-[15px] leading-relaxed text-slate-600 dark:text-slate-300">
                  {cat}
                </span>
              </li>
            ))}
          </ul>
        </section>

        {/* Editorial principles */}
        <section className="mb-10">
          <h2 className="font-display text-[18px] font-bold mt-8 mb-3 text-ink dark:text-cream">
            Editorial principles
          </h2>
          <ul className="space-y-4">
            {principles.map((p) => (
              <li key={p.title}>
                <p className="text-[15px] font-semibold text-ink dark:text-cream mb-1">
                  {p.title}
                </p>
                <p className="text-[15px] leading-relaxed text-slate-600 dark:text-slate-300">
                  {p.body}
                </p>
              </li>
            ))}
          </ul>
        </section>

        {/* Team */}
        <section className="mb-10">
          <h2 className="font-display text-[18px] font-bold mt-8 mb-3 text-ink dark:text-cream">
            Team
          </h2>
          <ul className="space-y-2">
            {team.map((member) => (
              <li
                key={member.name}
                className="flex flex-col sm:flex-row sm:items-baseline gap-1 sm:gap-3"
              >
                <span className="text-[15px] font-semibold text-ink dark:text-cream">
                  {member.name}
                </span>
                <span className="text-[14px] text-slate-500 dark:text-slate-400">
                  {member.role}
                </span>
              </li>
            ))}
          </ul>
        </section>

        {/* Contact block */}
        <section
          className={`rounded-xl p-6 mb-10 border ${
            darkMode
              ? "bg-slate-800 border-slate-700"
              : "bg-white border-slate-200 shadow-sm"
          }`}
        >
          <h2 className="font-display text-[16px] font-bold mb-3 text-ink dark:text-cream">
            Get in touch
          </h2>
          <p className="text-[14px] text-slate-500 dark:text-slate-400 mb-1">
            <span className="font-medium text-slate-700 dark:text-slate-200">Mint Street</span>
            <br />
            Hyderabad &middot; Bengaluru &middot; India
          </p>
          <p className="text-[14px] text-slate-500 dark:text-slate-400 mt-2">
            <span className="font-medium text-slate-700 dark:text-slate-200">Email:</span>{" "}
            <a
              href="mailto:editor@mintstreet.in"
              className="hover:underline text-mint"
            >
              editor@mintstreet.in
            </a>
          </p>
        </section>

        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-[14px] font-medium hover:underline text-mint"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Go back
        </button>
      </div>
    </div>
  );
}
