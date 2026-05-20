import { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AppContext } from "../App";

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

function Para({ children }) {
  return (
    <p className="text-[15px] leading-relaxed text-slate-600 dark:text-slate-300 mb-3">
      {children}
    </p>
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

export default function PrivacyPolicy() {
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
          <span className={darkMode ? "text-slate-500" : "text-slate-400"}>/</span>
          <span className={darkMode ? "text-slate-300" : "text-slate-600"}>Privacy</span>
        </nav>

        {/* Header */}
        <header className="mb-10">
          <h1 className="font-display font-bold text-[36px] sm:text-[44px] leading-tight mb-4">
            Privacy Policy
          </h1>
          <div className="w-16 h-[3px] rounded mb-5 bg-mint" />
          <p className="text-[13px] text-slate-400 dark:text-slate-500 font-medium uppercase tracking-widest">
            Last updated: May 2026
          </p>
        </header>

        <Para>
          This is the plain-English version of how (&ldquo;Mint
          Street,&rdquo; &ldquo;we&rdquo;) handles your data when you read us at ventureos.in,
          subscribe to our newsletters, or contact the newsroom. We try to collect as little as
          possible and explain the rest honestly. If anything below is unclear, write to
          legal@ventureos.in.
        </Para>

        {/* 1. Information We Collect */}
        <Section title="1. Information we collect">
          <Para>
            Most of Venture OS can be read without an account. When you do interact with us, here
            is what we end up with:
          </Para>
          <BulletList items={[
            "Things you give us directly - your name and email when you subscribe to a newsletter, the contents of any message you send us, and a profile if you create an account to save articles.",
            "Things your browser sends automatically - IP address (coarsened to a city), browser and device type, the pages you visited and the site that referred you. We use this to understand readership, not to identify individuals.",
            "Small files we store on your device - cookies and localStorage entries that remember whether you prefer dark mode, which articles you have saved, and whether you are signed in.",
          ]} />
        </Section>

        {/* 2. How We Use It */}
        <Section title="2. How we use it">
          <Para>We use what we collect for a short list of things:</Para>
          <BulletList items={[
            "Sending you the newsletters and alerts you have actively asked for.",
            "Keeping your account, saved articles and reading preferences working across visits.",
            "Understanding which stories resonate, so the newsroom can commission more of the right things.",
            "Protecting the site from abuse, scraping and fraud.",
            "Meeting our obligations under Indian law, including the Digital Personal Data Protection Act, 2023.",
          ]} />
          <Para>
            We do not sell your personal data, we do not rent our email list, and we do not run
            behavioural ad targeting on our own site.
          </Para>
        </Section>

        {/* 3. Cookies */}
        <Section title="3. Cookies">
          <Para>
            We use a small number of cookies. Some are essential &mdash; without them you cannot
            log in or save articles. The rest are analytics cookies that tell us aggregate things
            like &ldquo;this piece was read for an average of four minutes on mobile.&rdquo; You
            can block any of them in your browser; the site will still work, but personalisation
            will reset on every visit. For the long version, see our{" "}
            <Link to="/cookie-policy" className="underline text-mint">
              Cookie Policy
            </Link>
            .
          </Para>
        </Section>

        {/* 4. Sharing */}
        <Section title="4. Who we share data with">
          <Para>
            We keep the list of vendors short and only share what each actually needs:
          </Para>
          <BulletList items={[
            "Our cloud and email-delivery providers, who process data on our behalf under signed agreements.",
            "Analytics tools (currently a privacy-respecting analytics setup plus a basic install of Google Analytics) for aggregated traffic data.",
            "Law enforcement, regulators or courts when we are legally required to comply with a valid order.",
          ]} />
          <Para>
            We do not share your email or reading history with advertisers, sponsors or partners
            without your explicit consent.
          </Para>
        </Section>

        {/* 5. Your Rights */}
        <Section title="5. Your rights">
          <Para>
            Under Indian data-protection law (and most equivalents elsewhere), you have a few
            specific rights over your data:
          </Para>
          <BulletList items={[
            "Ask us what we hold about you and get a copy of it.",
            "Ask us to correct anything that is wrong.",
            "Ask us to delete your account and the personal data attached to it.",
            "Withdraw consent for marketing emails - every newsletter has a one-click unsubscribe.",
          ]} />
          <Para>
            Send any of these requests to{" "}
            <a href="mailto:legal@ventureos.in" className="underline text-mint">
              legal@ventureos.in
            </a>
            . We respond within 30 days, faster where we can.
          </Para>
        </Section>

        {/* 6. Children */}
        <Section title="6. Children">
          <Para>
            Venture OS is written for adults working in or near the startup economy. We do not
            knowingly collect data from anyone under 18. If you believe a child has signed up,
            email legal@ventureos.in and we will remove the account.
          </Para>
        </Section>

        {/* 7. Changes */}
        <Section title="7. Changes to this policy">
          <Para>
            When we change anything material here, we will update the &ldquo;Last updated&rdquo;
            date at the top and, if the change is significant, send a note to registered users.
            We will not retroactively use old data in ways that go against the version of the
            policy you originally agreed to.
          </Para>
        </Section>

        {/* 8. Contact */}
        <Section title="8. Contact">
          <Para>
            Privacy questions, data requests, complaints &mdash; send them all to{" "}
            <a href="mailto:legal@ventureos.in" className="underline text-mint">
              legal@ventureos.in
            </a>
            . Our registered office is below.
          </Para>
        </Section>

        {/* Contact card */}
        <section
          className={`rounded-xl p-6 mb-10 border ${
            darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200 shadow-sm"
          }`}
        >
          <h2 className="font-display text-[16px] font-bold mb-3 text-ink dark:text-cream">
            Contact us about privacy
          </h2>
          <p className="text-[14px] text-slate-500 dark:text-slate-400 mb-2">
           
            <br />
            Plot 14, HUDA Tech Park, Madhapur
            <br />
            Hyderabad &ndash; 500081, India
          </p>
          <a
            href="mailto:legal@ventureos.in"
            className="text-[14px] font-medium hover:underline text-mint"
          >
            legal@ventureos.in
          </a>
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
