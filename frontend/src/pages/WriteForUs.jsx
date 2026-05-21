import { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AppContext } from "../App";

function Para({ children }) {
  return (
    <p className="text-[15px] leading-relaxed text-[#7A90A8] dark:text-[#A0B4CC] mb-3">
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

function BulletList({ items }) {
  return (
    <ul className="space-y-1 mb-3 pl-1">
      {items.map((item, i) => (
        <li
          key={i}
          className="flex items-start gap-3 text-[15px] leading-relaxed text-[#7A90A8] dark:text-[#A0B4CC]"
        >
          <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 mt-[7px] bg-mint" />
          {item}
        </li>
      ))}
    </ul>
  );
}

export default function WriteForUs() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();

  return (
    <div className={`min-h-screen ${darkMode ? "bg-ink text-cream" : "bg-paper text-ink"}`}>
      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-[13px] mb-8" aria-label="Breadcrumb">
          <Link to="/" className="hover:underline text-mint">
            Home
          </Link>
          <span className={darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"}>/</span>
          <span className={darkMode ? "text-[#A0B4CC]" : "text-[#7A90A8]"}>Write for us</span>
        </nav>

        {/* Hero */}
        <header className="mb-10">
          <h1 className="font-display font-bold text-[36px] sm:text-[44px] leading-tight mb-4">
            Write for Venture OS
          </h1>
          <div className="w-16 h-[3px] rounded mb-5 bg-mint" />
          <Para>
            We commission sharp analysis on funding, M&amp;A and policy from operators, investors
            and freelance journalists who know their corner of the Indian economy better than
            anyone on the desk.
          </Para>
          <Para>
            <span className="font-semibold text-ink dark:text-cream">
              We pay &#8377;3,000&ndash;&#8377;8,000 per published piece
            </span>
            , depending on depth, originality and the amount of primary reporting involved. Rates
            for long-form investigations are negotiated separately.
          </Para>
          <Para>
            Pitch a 150-word outline to{" "}
            <a
              href="mailto:editor@ventureos.in"
              className="hover:underline font-semibold text-mint"
            >
              editor@ventureos.in
            </a>{" "}
            with the subject line &ldquo;Pitch &mdash; [your topic].&rdquo; We try to reply within
            a week.
          </Para>
        </header>

        {/* What we accept */}
        <Section title="What we accept">
          <BulletList items={[
            "Funding & deal analysis - what a round actually signals about the company, the sector and the fund writing the cheque. Bonus points for cap table or term sheet detail.",
            "M&A breakdowns - strategic reads of why a deal happened, what the multiples imply and which integration risks matter.",
            "Policy and regulation - DPDP, SEBI circulars, RBI fintech regs, state-level industrial policy. We want signal, not summary.",
            "Sector deep dives - climate hardware, deep tech, vertical SaaS, embedded finance, AI infra. Make us understand a sub-sector in 1,200 words.",
            "First-person operator essays - founders, CFOs, GPs writing on the record about something they actually built or backed.",
          ]} />
        </Section>

        {/* What we don't accept */}
        <Section title="What we don't accept">
          <BulletList items={[
            "Thinly-veiled marketing for a portfolio company or the author's own startup.",
            "Pieces previously published anywhere - including LinkedIn long-form, Substack or personal blogs.",
            "AI-generated drafts submitted without disclosure. If you used an LLM, tell us how.",
            "Investment recommendations, price targets or anything resembling stock tips.",
          ]} />
        </Section>

        {/* House rules */}
        <Section title="House rules">
          <BulletList items={[
            "Word count: 700–1,500 for analysis pieces; up to 3,000 for commissioned long-form.",
            "Sources must be attributed and linked. Anonymous sources are allowed but vetted by the editor.",
            "We edit for clarity, structure and house style. Significant edits are sent back to you before publication.",
            "Payment is on publication, paid within 10 working days, in INR.",
          ]} />
        </Section>

        {/* CTA */}
        <section
          className={`rounded-xl p-6 mb-10 border ${
            darkMode ? "bg-[#0D1321] border-[#1C2840]" : "bg-[#070B12] border-[#1C2840] shadow-sm"
          }`}
        >
          <h2 className="font-display text-[18px] font-bold mb-3 text-ink dark:text-cream">
            Ready to pitch?
          </h2>
          <p className="text-[14px] text-[#5A7090] dark:text-[#7A90A8] mb-3">
            A good pitch tells us, in 150 words: what you&rsquo;re arguing, who you&rsquo;ve spoken
            to, why now, and why you&rsquo;re the person to write it. Attach two links to previous
            work if you have them.
          </p>
          <p className="text-[14px] text-[#5A7090] dark:text-[#7A90A8]">
            <span className="font-semibold text-[#A0B4CC] dark:text-[#D0DDF0]">Email:</span>{" "}
            <a
              href="mailto:editor@ventureos.in"
              className="hover:underline font-medium text-mint"
            >
              editor@ventureos.in
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
