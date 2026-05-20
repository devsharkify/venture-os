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

export default function TermsOfService() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();

  return (
    <div className={`min-h-screen ${darkMode ? "bg-[#1C1410] text-slate-100" : "bg-white text-slate-800"}`}>
      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-[13px] mb-8" aria-label="Breadcrumb">
          <Link to="/" className={`hover:underline ${darkMode ? "text-blue-400" : "text-[#F26B1F]"}`}>
            Home
          </Link>
          <span className={darkMode ? "text-slate-500" : "text-slate-400"}>/</span>
          <span className={darkMode ? "text-slate-300" : "text-slate-600"}>Terms of Service</span>
        </nav>

        {/* Header */}
        <header className="mb-10">
          <h1
            className="font-bold text-[36px] sm:text-[44px] leading-tight mb-4"
            style={{ fontFamily: "'Fraunces', 'Georgia', serif" }}
          >
            Terms of Service
          </h1>
          <div className="w-16 h-[3px] rounded mb-5" style={{ backgroundColor: BRAND }} />
          <p className="text-[13px] text-slate-400 dark:text-slate-500 font-medium uppercase tracking-widest">
            Last Updated: May 2026
          </p>
        </header>

        <Para>
          Welcome to Mint Street. These Terms of Service (&ldquo;Terms&rdquo;) govern your
          access to and use of themintstreet.in and any related services, mobile applications, or
          publications operated by Mint Street (&ldquo;we,&rdquo; &ldquo;us,&rdquo; or
          &ldquo;our&rdquo;). Please read these Terms carefully before using our platform. By accessing
          or using our services in any way, you agree to be bound by these Terms.
        </Para>

        {/* 1. Acceptance of Terms */}
        <Section title="1. Acceptance of Terms" darkMode={darkMode}>
          <Para>
            By visiting, reading, or otherwise using Mint Street&rsquo;s website, applications,
            newsletters, or any other content we publish, you acknowledge that you have read, understood,
            and agree to be bound by these Terms and our Privacy Policy, which is incorporated herein by
            reference.
          </Para>
          <Para>
            If you do not agree to these Terms, you must immediately cease use of our services. Your
            continued use of our platform following any modification to these Terms constitutes your
            acceptance of the updated Terms.
          </Para>
          <Para>
            We reserve the right to modify these Terms at any time. Material changes will be communicated
            via a notice on our website or via email to registered users. It is your responsibility to
            review these Terms periodically.
          </Para>
        </Section>

        {/* 2. Use of Content */}
        <Section title="2. Use of Content" darkMode={darkMode}>
          <Para>
            All content published on Mint Street &mdash; including but not limited to articles,
            analysis, data visualisations, infographics, photographs, video, audio, and design elements
            &mdash; is the exclusive intellectual property of Mint Street or its licensors, and
            is protected under applicable Indian and international copyright law.
          </Para>
          <Para>
            You are permitted to:
          </Para>
          <BulletList items={[
            "Read and access content for personal, non-commercial use",
            "Share article links on social media with proper attribution to Mint Street",
            "Quote brief excerpts (not to exceed 150 words) in commentary or reporting, provided you credit the source and include a link to the original article",
          ]} />
          <Para>
            You are expressly prohibited from:
          </Para>
          <BulletList items={[
            "Reproducing, republishing, or redistributing our content in full without prior written permission",
            "Using our content for commercial purposes without a valid licensing agreement",
            "Scraping, crawling, or harvesting content from our website through automated means",
            "Removing or altering copyright notices, watermarks, or attribution from our content",
            "Creating derivative works based on our content without authorisation",
          ]} />
          <Para>
            For licensing, syndication, or reproduction enquiries, contact us at
            legal@themintstreet.in.
          </Para>
        </Section>

        {/* 3. User Conduct */}
        <Section title="3. User Conduct" darkMode={darkMode}>
          <Para>
            When using any interactive features of our platform (including comments, submissions, reporter
            registration, or account features), you agree to conduct yourself in a manner that is lawful,
            respectful, and consistent with the standards of a professional publication.
          </Para>
          <Para>You agree not to:</Para>
          <BulletList items={[
            "Submit false, misleading, or defamatory content",
            "Impersonate any person, organisation, or entity",
            "Harass, threaten, or abuse other users, journalists, or staff",
            "Upload or transmit malware, viruses, or any code designed to cause harm",
            "Attempt to gain unauthorised access to any part of our platform or infrastructure",
            "Use our platform for spam, unsolicited solicitation, or any form of commercial messaging without consent",
            "Engage in any activity that disrupts or degrades the performance of our services",
          ]} />
          <Para>
            We reserve the right to suspend or permanently terminate accounts that violate these
            conduct standards, without prior notice and without liability to you.
          </Para>
        </Section>

        {/* 4. Intellectual Property */}
        <Section title="4. Intellectual Property" darkMode={darkMode}>
          <Para>
            All intellectual property rights in and to Mint Street &mdash; including our brand
            name, logo, taglines, design system, editorial content, databases, and software &mdash; are
            owned by or licensed to Mint Street. Nothing in these Terms grants you any right,
            title, or interest in our intellectual property beyond the limited licence to access and use
            our content as expressly set out herein.
          </Para>
          <Para>
            Mint Street name and logo are registered trademarks. You may not use our trademarks
            in any manner that is likely to cause confusion, disparage us, or suggest endorsement without
            our prior written consent.
          </Para>
          <Para>
            If you submit content to us (such as a pitch, tip, or comment), you grant us a non-exclusive,
            royalty-free, worldwide licence to use, publish, and modify that content in connection with
            our editorial operations, subject to our Privacy Policy.
          </Para>
        </Section>

        {/* 5. Disclaimer of Warranties */}
        <Section title="5. Disclaimer of Warranties" darkMode={darkMode}>
          <Para>
            Mint Street provides its services on an &ldquo;as is&rdquo; and &ldquo;as
            available&rdquo; basis. We make no warranties, express or implied, including but not limited
            to warranties of merchantability, fitness for a particular purpose, accuracy, completeness,
            or non-infringement.
          </Para>
          <Para>
            While we strive for accuracy in all our reporting, we do not guarantee that our content is
            free from errors, omissions, or inaccuracies. Our content is for informational purposes only
            and should not be construed as investment advice, legal advice, financial guidance, or any
            other form of professional advice.
          </Para>
          <Para>
            We do not warrant that our website will be uninterrupted, error-free, or free from viruses
            or other harmful components. We are not liable for any loss or damage arising from your use
            of or inability to access our services.
          </Para>
        </Section>

        {/* 6. Limitation of Liability */}
        <Section title="6. Limitation of Liability" darkMode={darkMode}>
          <Para>
            To the maximum extent permitted by applicable law, Mint Street, its directors,
            employees, journalists, contributors, and affiliates shall not be liable for any indirect,
            incidental, special, consequential, or punitive damages, including but not limited to:
          </Para>
          <BulletList items={[
            "Loss of profits, revenue, or business opportunities",
            "Loss of data or content",
            "Reputational harm",
            "Decisions made in reliance on our editorial content",
            "Any claims arising from third-party services linked to or mentioned on our platform",
          ]} />
          <Para>
            In no event shall our aggregate liability to you for any claim arising out of or related to
            these Terms or your use of our services exceed INR 1,000 (One Thousand Indian Rupees) or
            the amount you paid us in the preceding 12 months, whichever is greater.
          </Para>
          <Para>
            Some jurisdictions do not allow the exclusion of certain warranties or limitation of liability.
            In such jurisdictions, our liability shall be limited to the fullest extent permitted by law.
          </Para>
        </Section>

        {/* 7. Third-Party Links */}
        <Section title="7. Third-Party Links &amp; References" darkMode={darkMode}>
          <Para>
            Our content may contain links to third-party websites, sources, or services. These links are
            provided for reference and convenience only. Mint Street does not endorse, control,
            or take responsibility for the content, privacy practices, or conduct of any third-party
            websites. Accessing third-party sites is entirely at your own risk.
          </Para>
        </Section>

        {/* 8. Governing Law */}
        <Section title="8. Governing Law &amp; Dispute Resolution" darkMode={darkMode}>
          <Para>
            These Terms shall be governed by and construed in accordance with the laws of India, without
            regard to its conflict of law provisions. The courts of Hyderabad, Telangana, India, shall
            have exclusive jurisdiction over any disputes arising out of or in connection with these Terms
            or your use of Mint Street&rsquo;s services.
          </Para>
          <Para>
            Before initiating any legal proceeding, both parties agree to attempt to resolve the dispute
            informally by contacting us at legal@themintstreet.in. We will make good-faith efforts
            to resolve the issue within 30 days of receiving notice.
          </Para>
        </Section>

        {/* 9. Indemnification */}
        <Section title="9. Indemnification" darkMode={darkMode}>
          <Para>
            You agree to indemnify, defend, and hold harmless Mint Street and its officers,
            directors, employees, and agents from and against any claims, liabilities, damages, losses,
            and expenses (including reasonable legal fees) arising out of or in connection with your use
            of our services, your breach of these Terms, or your violation of any third-party rights.
          </Para>
        </Section>

        {/* 10. Termination */}
        <Section title="10. Termination" darkMode={darkMode}>
          <Para>
            We reserve the right to suspend or terminate your access to our services at any time, for
            any reason, with or without notice &mdash; including if we believe you have violated these
            Terms. Upon termination, your right to access and use our services will immediately cease.
            All provisions of these Terms that by their nature should survive termination shall do so,
            including intellectual property rights, disclaimers, and limitations of liability.
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
            Contact Our Legal Team
          </h2>
          <p className="text-[14px] text-slate-500 dark:text-slate-400 mb-2">
            For questions about these Terms, licensing, or legal matters:
          </p>
          <p className="text-[14px] text-slate-500 dark:text-slate-400 mb-1">
            Mint Street, Hyderabad, Telangana, India
          </p>
          <a
            href="mailto:legal@themintstreet.in"
            className="text-[14px] font-medium hover:underline"
            style={{ color: BRAND }}
          >
            legal@themintstreet.in
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
