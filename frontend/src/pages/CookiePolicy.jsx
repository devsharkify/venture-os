import { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AppContext } from "../App";

const BRAND = "#F26B1F";

function Section({ title, children, darkMode }) {
  return (
    <section className="mb-8">
      <h2
        className="text-[18px] font-bold mt-8 mb-3"
        style={{ fontFamily: "'Fraunces', 'Georgia', serif", color: darkMode ? "#e2e8f0" : "#1e293b" }}
      >
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

function SubHeading({ children, darkMode }) {
  return (
    <h3
      className="text-[15px] font-bold mt-5 mb-2"
      style={{ color: darkMode ? "#cbd5e1" : "#334155" }}
    >
      {children}
    </h3>
  );
}

function BulletList({ items }) {
  return (
    <ul className="space-y-1 mb-3 pl-1">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-3 text-[15px] leading-relaxed text-slate-600 dark:text-slate-300">
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

export default function CookiePolicy() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();

  const cookieTableRows = [
    { name: "tvr_dark_mode", purpose: "Stores your UI dark/light mode preference", duration: "1 year" },
    { name: "tvr_saved", purpose: "Keeps track of articles you have saved for later reading", duration: "1 year" },
    { name: "_ga", purpose: "Google Analytics - distinguishes unique users and sessions", duration: "2 years" },
    { name: "_gid", purpose: "Google Analytics - identifies a session within a 24-hour window", duration: "24 hours" },
  ];

  return (
    <div className={`min-h-screen ${darkMode ? "bg-[#1C1410] text-slate-100" : "bg-[#FAF7F1] text-slate-800"}`}>
      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-[13px] mb-8" aria-label="Breadcrumb">
          <Link to="/" className={`hover:underline ${darkMode ? "text-blue-400" : "text-[#F26B1F]"}`}>
            Home
          </Link>
          <span className={darkMode ? "text-slate-500" : "text-slate-400"}>/</span>
          <span className={darkMode ? "text-slate-300" : "text-slate-600"}>Cookie Policy</span>
        </nav>

        {/* Header */}
        <header className="mb-10">
          <h1
            className="font-bold text-[36px] sm:text-[44px] leading-tight mb-4"
            style={{ fontFamily: "'Fraunces', 'Georgia', serif" }}
          >
            Cookie Policy
          </h1>
          <div className="w-16 h-[3px] rounded mb-5" style={{ backgroundColor: BRAND }} />
          <p className="text-[13px] text-slate-400 dark:text-slate-500 font-medium uppercase tracking-widest">
            Last Updated: May 2026
          </p>
        </header>

        <Para>
          This Cookie Policy explains how Mint Street (&ldquo;we,&rdquo; &ldquo;us,&rdquo; or
          &ldquo;our&rdquo;) uses cookies and similar tracking technologies when you visit
          themintstreet.in. We want to be transparent about the data we collect, why we collect
          it, and the choices available to you. By continuing to use our website, you consent to the
          use of cookies as described in this policy.
        </Para>

        {/* 1. What Are Cookies */}
        <Section title="1. What Are Cookies?" darkMode={darkMode}>
          <Para>
            Cookies are small text files that are placed on your device (computer, smartphone, or
            tablet) by websites you visit. They are widely used to make websites work efficiently,
            to remember your preferences, and to provide information to the site owners.
          </Para>

          <SubHeading darkMode={darkMode}>Session Cookies</SubHeading>
          <Para>
            Session cookies are temporary files that exist only for the duration of your browser
            session. They are automatically deleted when you close your browser. We use session
            cookies to keep you logged in as you navigate between pages and to maintain the state
            of your reading experience during a single visit.
          </Para>

          <SubHeading darkMode={darkMode}>Persistent Cookies</SubHeading>
          <Para>
            Persistent cookies remain on your device for a set period of time after the browser
            session ends &mdash; or until you manually delete them. We use persistent cookies to
            remember your preferences (such as dark mode) across multiple visits, so you do not
            have to reconfigure your settings each time.
          </Para>

          <SubHeading darkMode={darkMode}>First-Party vs. Third-Party Cookies</SubHeading>
          <Para>
            First-party cookies are set directly by Mint Street and are used solely to
            improve your experience on our site. Third-party cookies are placed by external services
            that we use, such as Google Analytics, to help us understand how our content is consumed.
            Third-party cookies are governed by the privacy policies of those respective providers.
          </Para>
        </Section>

        {/* 2. How We Use Cookies */}
        <Section title="2. How We Use Cookies" darkMode={darkMode}>
          <SubHeading darkMode={darkMode}>Essential Cookies</SubHeading>
          <Para>
            These cookies are strictly necessary for the website to function correctly. Without them,
            services such as login sessions, navigation, and saved article preferences would not work.
            Because they are essential to the basic operation of the site, these cookies cannot be
            disabled through our platform.
          </Para>

          <SubHeading darkMode={darkMode}>Analytics Cookies</SubHeading>
          <Para>
            We use Google Analytics to collect aggregated, anonymised data about how visitors
            interact with our site &mdash; including which articles are read most, how long visitors
            stay, and where they arrive from. This data helps us improve our editorial output and
            product experience. Analytics cookies do not identify you personally.
          </Para>

          <SubHeading darkMode={darkMode}>Performance Cookies</SubHeading>
          <Para>
            Performance cookies help us understand how our website loads and performs across
            different devices and connection speeds. The data collected is used to optimise page
            delivery, reduce load times, and ensure a consistent reading experience for all users.
          </Para>

          <SubHeading darkMode={darkMode}>Functional Cookies</SubHeading>
          <Para>
            Functional cookies enable enhanced features and personalisation. We use them to
            remember your dark mode or light mode preference and articles you have bookmarked.
            Disabling functional cookies will result in these settings being reset on each visit.
          </Para>
        </Section>

        {/* 3. Third-Party Cookies */}
        <Section title="3. Third-Party Cookies" darkMode={darkMode}>
          <Para>
            Some cookies on our site are placed by third-party services that appear on our pages.
            We do not control these cookies, and they are subject to the respective third parties&rsquo;
            privacy and cookie policies.
          </Para>

          <SubHeading darkMode={darkMode}>Google Analytics</SubHeading>
          <Para>
            We use Google Analytics (provided by Google LLC) to measure website traffic and user
            behaviour. Google Analytics sets cookies (_ga, _gid, and related variants) to collect
            anonymised usage data, which is transmitted to Google servers. Google&rsquo;s use of this
            data is governed by the{" "}
            <a
              href="https://policies.google.com/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="underline"
              style={{ color: BRAND }}
            >
              Google Privacy Policy
            </a>
            . You can opt out of Google Analytics across all websites using the{" "}
            <a
              href="https://tools.google.com/dlpage/gaoptout"
              target="_blank"
              rel="noopener noreferrer"
              className="underline"
              style={{ color: BRAND }}
            >
              Google Analytics Opt-Out Browser Add-on
            </a>
            .
          </Para>

          <SubHeading darkMode={darkMode}>Embedded Content</SubHeading>
          <Para>
            Articles on Mint Street may include embedded content from third-party platforms
            such as YouTube, Twitter/X, or LinkedIn. These embedded resources may set their own
            cookies when you interact with them. We recommend reviewing the cookie policies of these
            platforms separately if you have concerns about the data they collect.
          </Para>
        </Section>

        {/* 4. Managing Cookies */}
        <Section title="4. Managing Your Cookie Preferences" darkMode={darkMode}>
          <Para>
            You have the right to accept, decline, or delete cookies. Below is guidance on how to
            control cookies in the most commonly used browsers. Note that restricting certain cookies
            may impact the functionality of features such as dark mode and saved articles.
          </Para>

          <SubHeading darkMode={darkMode}>Google Chrome</SubHeading>
          <BulletList items={[
            "Open Chrome and go to Settings (three-dot menu > Settings).",
            "Click on Privacy and security > Cookies and other site data.",
            "Select your preferred option: Allow all cookies, Block third-party cookies, or Block all cookies.",
            "To delete existing cookies, go to Privacy and security > Clear browsing data and check Cookies and other site data.",
          ]} />

          <SubHeading darkMode={darkMode}>Mozilla Firefox</SubHeading>
          <BulletList items={[
            "Open Firefox and go to Settings > Privacy & Security.",
            "Under Enhanced Tracking Protection, select Standard, Strict, or Custom.",
            "To clear cookies, scroll to Cookies and Site Data and click Clear Data.",
          ]} />

          <SubHeading darkMode={darkMode}>Apple Safari</SubHeading>
          <BulletList items={[
            "Open Safari and go to Preferences > Privacy.",
            "Check Prevent cross-site tracking to block third-party cookies.",
            "To remove cookies, click Manage Website Data and then Remove All.",
          ]} />

          <Para>
            You can also opt out of interest-based advertising and cross-site tracking using tools
            provided by the{" "}
            <a
              href="http://www.youronlinechoices.eu"
              target="_blank"
              rel="noopener noreferrer"
              className="underline"
              style={{ color: BRAND }}
            >
              Your Online Choices
            </a>{" "}
            initiative.
          </Para>
        </Section>

        {/* 5. Cookie Table */}
        <Section title="5. Cookie Reference Table" darkMode={darkMode}>
          <Para>
            The following table lists the primary cookies used on themintstreet.in, their
            purpose, and how long they are retained on your device.
          </Para>
          <div className="overflow-x-auto mt-4 mb-4 rounded-lg border border-slate-200 dark:border-slate-700">
            <table className="w-full text-[14px] border-collapse">
              <thead>
                <tr className={darkMode ? "bg-slate-800" : "bg-slate-100"}>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-200 border-b border-slate-200 dark:border-slate-700 whitespace-nowrap">
                    Cookie Name
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-200 border-b border-slate-200 dark:border-slate-700">
                    Purpose
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-200 border-b border-slate-200 dark:border-slate-700 whitespace-nowrap">
                    Duration
                  </th>
                </tr>
              </thead>
              <tbody>
                {cookieTableRows.map((row, i) => (
                  <tr
                    key={i}
                    className={`border-b last:border-0 border-slate-200 dark:border-slate-700 ${
                      i % 2 === 0
                        ? darkMode ? "bg-[#1C1410]" : "bg-white"
                        : darkMode ? "bg-slate-800/50" : "bg-slate-50"
                    }`}
                  >
                    <td className="px-4 py-3 font-mono text-[13px] text-slate-700 dark:text-slate-300 whitespace-nowrap">
                      {row.name}
                    </td>
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-300">{row.purpose}</td>
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-300 whitespace-nowrap">{row.duration}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>

        {/* 6. Changes */}
        <Section title="6. Changes to This Cookie Policy" darkMode={darkMode}>
          <Para>
            We may update this Cookie Policy from time to time as our technology, legal obligations,
            or services evolve. When we make significant changes, we will update the &ldquo;Last
            Updated&rdquo; date at the top of this page. We encourage you to revisit this page
            periodically to stay informed about how we use cookies.
          </Para>
        </Section>

        {/* Contact */}
        <section
          className={`rounded-xl p-6 mb-10 border ${
            darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200 shadow-sm"
          }`}
        >
          <h2
            className="text-[16px] font-bold mb-3"
            style={{ fontFamily: "'Fraunces', 'Georgia', serif", color: darkMode ? "#e2e8f0" : "#1e293b" }}
          >
            Questions About Cookies?
          </h2>
          <p className="text-[14px] text-slate-500 dark:text-slate-400 mb-2">
            If you have any questions about our use of cookies or this Cookie Policy, please
            contact our privacy team:
          </p>
          <p className="text-[14px] text-slate-500 dark:text-slate-400 mb-1">
            Mint Street, Hyderabad, Telangana, India
          </p>
          <a
            href="mailto:privacy@themintstreet.in"
            className="text-[14px] font-medium hover:underline"
            style={{ color: BRAND }}
          >
            privacy@themintstreet.in
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
