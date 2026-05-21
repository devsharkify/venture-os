import { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AppContext } from "../App";

const BRAND = "#2D7AFF";

function Section({ title, children, darkMode }) {
  return (
    <section className="mb-8">
      <h2
        className="text-[18px] font-bold mt-8 mb-3"
        style={{ fontFamily: "'Syne', 'Georgia', serif", color: darkMode ? "#e2e8f0" : "#1e293b" }}
      >
        {title}
      </h2>
      {children}
    </section>
  );
}

function Para({ children }) {
  return (
    <p className="text-[15px] leading-relaxed text-[#7A90A8] dark:text-[#A0B4CC] mb-3">
      {children}
    </p>
  );
}

function BulletList({ items }) {
  return (
    <ul className="space-y-1 mb-3 pl-1">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-3 text-[15px] leading-relaxed text-[#7A90A8] dark:text-[#A0B4CC]">
          <span
            className="w-1.5 h-1.5 rounded-full flex-shrink-0 mt-[7px]"
            style={{ backgroundColor: BRAND }}
          />
          {item}
        </li>
      ))}
    </ul>
  );
}

export default function Disclaimer() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();

  return (
    <div className={`min-h-screen ${darkMode ? "bg-[#070B12] text-[#E2EAF6]" : "bg-[#070B12] text-[#E2EAF6]"}`}>
      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-[13px] mb-8" aria-label="Breadcrumb">
          <Link to="/" className={`hover:underline ${darkMode ? "text-blue-400" : "text-[#2D7AFF]"}`}>
            Home
          </Link>
          <span className={darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"}>/</span>
          <span className={darkMode ? "text-[#A0B4CC]" : "text-[#7A90A8]"}>Disclaimer</span>
        </nav>

        {/* Header */}
        <header className="mb-10">
          <h1
            className="font-bold text-[36px] sm:text-[44px] leading-tight mb-4"
            style={{ fontFamily: "'Syne', 'Georgia', serif" }}
          >
            Disclaimer
          </h1>
          <div className="w-16 h-[3px] rounded mb-5" style={{ backgroundColor: BRAND }} />
          <p className="text-[13px] text-[#7A90A8] dark:text-[#5A7090] font-medium uppercase tracking-widest">
            Last Updated: May 2026
          </p>
        </header>

        <Para>
          Please read this Disclaimer carefully before accessing or relying on any content
          published by Venture OS (&ldquo;we,&rdquo; &ldquo;us,&rdquo; or
          &ldquo;our&rdquo;) on theventureos.in or across any of our associated
          channels, newsletters, or social media properties.
        </Para>

        {/* 1. Editorial Disclaimer */}
        <Section title="1. Editorial Disclaimer" darkMode={darkMode}>
          <Para>
            All articles, features, analyses, opinion pieces, and reports published on The
            Venture OS are intended solely for general informational and educational
            purposes. Our editorial content reflects the views, observations, and independent
            research of our journalists and contributors at the time of publication.
          </Para>
          <Para>
            Nothing published on Venture OS should be construed as financial advice,
            investment advice, legal advice, tax advice, or any other form of professional
            guidance. If you require advice specific to your circumstances, we strongly encourage
            you to consult a qualified professional in the relevant field.
          </Para>
          <Para>
            The views expressed in opinion pieces, guest contributions, and columns are those of
            the individual authors and do not necessarily represent the editorial position of The
            Venture OS as a publication.
          </Para>
        </Section>

        {/* 2. Accuracy & Completeness */}
        <Section title="2. Accuracy &amp; Completeness" darkMode={darkMode}>
          <Para>
            We are committed to the highest standards of accuracy in our reporting and make every
            reasonable effort to verify information before publication. However, The Venture
            Republic makes no warranties, express or implied, regarding the completeness,
            accuracy, reliability, or timeliness of any content on this website.
          </Para>
          <Para>
            The startup ecosystem moves fast. Funding rounds, valuations, company statuses,
            leadership changes, and regulatory developments can change rapidly after our stories
            are published. We aim to update material inaccuracies as quickly as practicable, but
            we cannot guarantee that every piece of content reflects the most current state of
            affairs at any given moment.
          </Para>
          <Para>
            If you believe any information on our site is factually incorrect, please contact us
            at hello@theventureos.in so we can investigate and issue a correction where
            warranted.
          </Para>
        </Section>

        {/* 3. Investment Disclaimer */}
        <Section title="3. Investment Disclaimer" darkMode={darkMode}>
          <Para>
            Venture OS is a media company, not a registered investment advisor, broker,
            or financial planner. Nothing on this website &mdash; including articles covering
            startup funding rounds, valuations, market trends, sector analyses, or investor
            commentary &mdash; constitutes investment advice or a solicitation to buy, sell, or
            hold any security, asset, or financial instrument.
          </Para>
          <Para>
            Any coverage of funding rounds, venture capital activity, or public market developments
            is journalistic in nature and is provided for informational purposes only. Readers
            should not make investment decisions based solely or primarily on information published
            by Venture OS.
          </Para>
          <Para>
            Investing in startups and early-stage ventures involves significant risk, including the
            potential loss of capital. Before making any investment decision, we strongly recommend
            that you:
          </Para>
          <BulletList items={[
            "Consult a SEBI-registered investment advisor or financial planner",
            "Conduct your own independent due diligence",
            "Read all relevant offer documents, disclosures, and regulatory filings",
            "Assess your personal risk tolerance and financial situation",
          ]} />
          <Para>
            Venture OS does not hold any SEBI registration and is not regulated as a
            financial services entity. Readers in other jurisdictions should consult the relevant
            regulatory authority in their region.
          </Para>
        </Section>

        {/* 4. Third-Party Links */}
        <Section title="4. Third-Party Links &amp; References" darkMode={darkMode}>
          <Para>
            Our articles frequently reference and link to external websites, third-party sources,
            company websites, regulatory filings, and publicly available databases. These links are
            provided as a convenience and for reference purposes only.
          </Para>
          <Para>
            Venture OS does not endorse, control, or take responsibility for the accuracy,
            legality, or content of any third-party website. We are not liable for any loss or damage
            that may result from your use of, or reliance on, content found at external links. Accessing
            third-party websites is entirely at your own risk, and we recommend reviewing the privacy
            and disclaimer policies of those sites independently.
          </Para>
        </Section>

        {/* 5. Forward-Looking Statements */}
        <Section title="5. Forward-Looking Statements" darkMode={darkMode}>
          <Para>
            Certain content on Venture OS, including coverage of startup projections,
            anticipated funding rounds, expansion plans, market forecasts, and industry outlooks,
            may contain forward-looking statements. These statements are based on information
            available to our journalists at the time of writing and reflect expectations or
            assessments about future events.
          </Para>
          <Para>
            Forward-looking statements are inherently uncertain and subject to risks, assumptions,
            and factors that are difficult to predict. Actual outcomes may differ materially from
            what is discussed or implied. Readers should treat such statements with appropriate
            caution and not rely on them as guarantees of future performance.
          </Para>
          <Para>
            Startup valuations, funding amounts, and revenue figures cited in our articles are
            sourced from public disclosures, regulatory filings, company announcements, or
            industry databases. We do not independently verify all such figures and note that
            private market valuations in particular are estimates subject to change.
          </Para>
        </Section>

        {/* 6. Affiliate Disclosure */}
        <Section title="6. Affiliate Disclosure" darkMode={darkMode}>
          <Para>
            Venture OS may from time to time feature content that includes affiliate
            links &mdash; these are links to products, services, or platforms through which we may
            earn a referral commission if a reader clicks through and makes a purchase or signs up.
          </Para>
          <Para>
            Where affiliate links appear, they will be clearly identified with a disclosure notice
            such as &ldquo;Affiliate Link&rdquo; or &ldquo;Sponsored Link.&rdquo; The presence of
            an affiliate relationship does not influence our editorial judgment or the
            independence of our reporting. We only recommend or feature products and services that
            we believe are genuinely relevant and useful to our readership.
          </Para>
          <Para>
            If you have questions about a specific affiliate partnership or sponsored placement,
            please contact us at hello@theventureos.in.
          </Para>
        </Section>

        {/* 7. No Professional Relationship */}
        <Section title="7. No Professional Relationship" darkMode={darkMode}>
          <Para>
            Your use of Venture OS does not create any professional, advisory, or
            fiduciary relationship between you and Venture OS, its journalists, or its
            contributors. The information we publish should be treated as a starting point for your
            own research &mdash; not as definitive guidance on which you should act without
            independent verification.
          </Para>
        </Section>

        {/* 8. Limitation of Liability */}
        <Section title="8. Limitation of Liability" darkMode={darkMode}>
          <Para>
            To the fullest extent permitted by applicable law, Venture OS and its
            officers, directors, employees, journalists, and contributors shall not be liable for
            any direct, indirect, incidental, consequential, or special damages arising out of
            or in connection with your use of, or reliance upon, any content published on this
            website. This includes, without limitation, any losses arising from investment
            decisions made in reliance on our content.
          </Para>
        </Section>

        {/* Contact */}
        <section
          className={`rounded-xl p-6 mb-10 border ${
            darkMode ? "bg-[#0D1321] border-[#1C2840]" : "bg-[#070B12] border-[#1C2840] shadow-sm"
          }`}
        >
          <h2
            className="text-[16px] font-bold mb-3"
            style={{ fontFamily: "'Syne', 'Georgia', serif", color: darkMode ? "#e2e8f0" : "#1e293b" }}
          >
            Contact Us
          </h2>
          <p className="text-[14px] text-[#5A7090] dark:text-[#7A90A8] mb-2">
            For editorial corrections, factual disputes, or general inquiries:
          </p>
          <p className="text-[14px] text-[#5A7090] dark:text-[#7A90A8] mb-1">
            Venture OS, Hyderabad, Telangana, India
          </p>
          <a
            href="mailto:hello@theventureos.in"
            className="text-[14px] font-medium hover:underline"
            style={{ color: BRAND }}
          >
            hello@theventureos.in
          </a>
        </section>

        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-[14px] font-medium hover:underline"
          style={{ color: BRAND }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Go Back
        </button>
      </div>
    </div>
  );
}
