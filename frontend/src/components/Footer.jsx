import { useContext, useState } from "react";
import { Twitter, Linkedin, Instagram, Youtube, ArrowRight, Zap } from "lucide-react";
import { AppContext } from "../App";

const COVERAGE = [
  { label: "Markets & IPOs", href: "/?cat=ipo" },
  { label: "Funding Rounds", href: "/?cat=funding" },
  { label: "Startups", href: "/?cat=startups" },
  { label: "Deep Tech", href: "/?cat=deeptech" },
  { label: "Fintech", href: "/?cat=fintech" },
  { label: "SaaS", href: "/?cat=saas" },
  { label: "Policy", href: "/?cat=policy" },
  { label: "Venture Capital", href: "/?cat=vc" },
  { label: "Climate Tech", href: "/?cat=climate" },
];

const COMPANY = [
  { label: "About", href: "/about" },
  { label: "Editorial Standards", href: "/editorial-standards" },
  { label: "Write For Us", href: "/write-for-us" },
  { label: "Advertise", href: "/advertise" },
  { label: "Contact", href: "/contact" },
  { label: "Careers", href: "/careers" },
];

const RESOURCES = [
  { label: "ePaper", href: "/epaper" },
  { label: "Video News", href: "/video" },
  { label: "Saved Articles", href: "/saved" },
  { label: "Reporter Portal", href: "/reporter-login" },
  { label: "Startup Apply", href: "/startup-apply" },
  { label: "RSS Feed", href: "/rss.xml" },
];

const LEGAL = [
  { label: "Privacy", href: "/privacy-policy" },
  { label: "Terms", href: "/terms" },
  { label: "Cookies", href: "/cookie-policy" },
  { label: "Disclaimer", href: "/disclaimer" },
];

const SOCIALS = [
  { Icon: Twitter, href: "https://twitter.com/ventureos_in", label: "Twitter / X" },
  { Icon: Linkedin, href: "https://linkedin.com/company/ventureos", label: "LinkedIn" },
  { Icon: Instagram, href: "https://instagram.com/ventureos", label: "Instagram" },
  { Icon: Youtube, href: "https://youtube.com/@ventureos", label: "YouTube" },
];

export const Footer = () => {
  const { darkMode } = useContext(AppContext);
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e) => {
    e.preventDefault();
    setSubscribed(true);
    setEmail("");
    setTimeout(() => setSubscribed(false), 3000);
  };

  const year = new Date().getFullYear();

  // Theme tokens
  const bg         = darkMode ? "#040609"  : "#F4F7FF";
  const topBorder  = darkMode ? "#131B2A"  : "#E2E8F4";
  const surface    = darkMode ? "#0D1321"  : "#FFFFFF";
  const border     = darkMode ? "#1C2840"  : "#E2E8F4";
  const bodyText   = darkMode ? "#4A6280"  : "#4A6280";
  const linkText   = darkMode ? "#5A7090"  : "#64748B";
  const labelText  = darkMode ? "#3A4E66"  : "#94A3B8";
  const headText   = darkMode ? "#E2EAF6"  : "#0D1321";
  const iconBg     = darkMode ? "#0D1321"  : "#FFFFFF";
  const iconBorder = darkMode ? "#1C2840"  : "#E2E8F4";
  const inputBg    = darkMode ? "#070B12"  : "#F8FAFF";
  const inputBorder= darkMode ? "#1C2840"  : "#CBD5E8";
  const inputText  = darkMode ? "#E2EAF6"  : "#0D1321";
  const statusBg   = darkMode ? "#0D1321"  : "#FFFFFF";
  const dotColor   = "#00D9C8";
  const bottomBorder= darkMode ? "#131B2A" : "#E2E8F4";
  const copyText   = darkMode ? "#2A3D55"  : "#94A3B8";

  return (
    <footer data-testid="footer" className="mt-8" style={{ background: bg, borderTop: `1px solid ${topBorder}` }}>
      {/* Blue gradient top accent */}
      <div style={{ height: "2px", background: "linear-gradient(90deg,#2D7AFF 0%,#00D9C8 50%,transparent 100%)" }} />

      <div className="max-w-screen-xl mx-auto px-6 py-10">

        {/* Brand + newsletter */}
        <div className="pb-8 mb-8 grid grid-cols-1 lg:grid-cols-2 gap-10 items-start" style={{ borderBottom: `1px solid ${topBorder}` }}>

          <div>
            <div className="flex items-center gap-3 mb-4">
              <img src="/logo.svg" alt="Venture OS" className="w-9 h-9 rounded-lg" />
              <div>
                <div className="font-display font-bold text-[18px] tracking-tight" style={{ color: headText }}>VentureOS</div>
                <div className="text-[10px] font-mono tracking-[0.2em] uppercase mt-0.5" style={{ color: labelText }}>startup intelligence</div>
              </div>
            </div>
            <p className="text-[13px] leading-relaxed max-w-[38ch]" style={{ color: bodyText }}>
              Mission control for India's startup ecosystem. Daily intelligence on funding, M&A, policy, and deep tech — built by founders, for founders.
            </p>
            <div className="flex items-center gap-3 mt-5">
              {SOCIALS.map(({ Icon, href, label }) => (
                <a key={label} href={href} target="_blank" rel="noopener noreferrer" aria-label={label}
                  className="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:opacity-70"
                  style={{ background: iconBg, border: `1px solid ${iconBorder}` }}>
                  <Icon size={14} strokeWidth={1.75} style={{ color: darkMode ? "#7A90A8" : "#64748B" }} />
                </a>
              ))}
            </div>
          </div>

          {/* Newsletter */}
          <div className="rounded-xl p-6" style={{ background: surface, border: `1px solid ${border}` }}>
            <div className="flex items-center gap-2 mb-3">
              <Zap size={14} style={{ color: "#2D7AFF" }} />
              <h3 className="font-display font-bold text-[15px]" style={{ color: headText }}>The Daily Signal</h3>
            </div>
            <p className="text-[12px] mb-4 leading-relaxed" style={{ color: bodyText }}>
              5-minute brief on India's top startup deals and tech moves. Delivered every weekday at 7am IST.
            </p>
            {subscribed ? (
              <div className="flex items-center gap-2 px-4 py-3 rounded-lg text-[13px] font-semibold"
                style={{ background: "rgba(0,217,200,0.08)", border: "1px solid rgba(0,217,200,0.3)", color: "#00A89A" }}>
                <span>✓</span><span>You're subscribed — check your inbox!</span>
              </div>
            ) : (
              <form onSubmit={handleSubscribe} className="flex gap-2">
                <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="flex-1 min-w-0 rounded-lg px-3 py-2.5 text-[13px] outline-none transition-all"
                  style={{ background: inputBg, border: `1px solid ${inputBorder}`, color: inputText }} />
                <button type="submit"
                  className="flex items-center gap-1.5 text-white text-[13px] font-semibold px-4 py-2.5 rounded-lg whitespace-nowrap hover:opacity-90 transition-opacity"
                  style={{ background: "linear-gradient(135deg,#2D7AFF 0%,#1A5FCC 100%)", boxShadow: "0 2px 8px rgba(45,122,255,0.30)" }}>
                  Subscribe <ArrowRight size={12} />
                </button>
              </form>
            )}
            <p className="text-[11px] mt-2.5" style={{ color: labelText }}>
              Free · Unsubscribe anytime · We never share your email.
            </p>
          </div>
        </div>

        {/* 3-column links */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-8 mb-8">
          {[
            { title: "Coverage", color: "#2D7AFF", items: COVERAGE },
            { title: "Company",  color: "#00D9C8", items: COMPANY  },
            { title: "Resources",color: "#F59E0B", items: RESOURCES },
          ].map(({ title, color, items }) => (
            <div key={title}>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-1 h-4 rounded-full" style={{ background: color }} />
                <h4 className="text-[10px] font-bold uppercase tracking-[0.2em]" style={{ color: labelText }}>{title}</h4>
              </div>
              <nav className="flex flex-col gap-2.5">
                {items.map(({ label, href }) => (
                  <a key={label} href={href} className="text-[13px] transition-colors hover:text-mint" style={{ color: linkText }}>{label}</a>
                ))}
              </nav>
            </div>
          ))}
        </div>

        {/* Bottom strip */}
        <div className="pt-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3" style={{ borderTop: `1px solid ${bottomBorder}` }}>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[11px] font-mono" style={{ color: copyText }}>© {year} VentureOS. Built in Hyderabad.</span>
            <span style={{ color: border }}>·</span>
            {LEGAL.map(({ label, href }, i) => (
              <span key={label} className="flex items-center gap-2">
                <a href={href} className="text-[11px] transition-colors hover:text-mint" style={{ color: copyText }}>{label}</a>
                {i < LEGAL.length - 1 && <span style={{ color: border }}>·</span>}
              </span>
            ))}
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg" style={{ background: statusBg, border: `1px solid ${border}` }}>
            <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: dotColor }} />
            <span className="text-[10px] font-mono uppercase tracking-wider" style={{ color: labelText }}>All systems operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
