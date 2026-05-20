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

  return (
    <footer
      data-testid="footer"
      className="mt-8"
      style={{ background: "#040609", borderTop: "1px solid #131B2A" }}
    >
      {/* Blue gradient top accent */}
      <div style={{ height: "2px", background: "linear-gradient(90deg, #2D7AFF 0%, #00D9C8 50%, transparent 100%)" }} />

      <div className="max-w-screen-xl mx-auto px-6 py-10">

        {/* Top: brand + newsletter */}
        <div className="pb-8 mb-8 grid grid-cols-1 lg:grid-cols-2 gap-10 items-start" style={{ borderBottom: "1px solid #131B2A" }}>

          {/* Brand */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <img src="/logo.svg" alt="Venture OS" className="w-9 h-9 rounded-lg" />
              <div>
                <div className="font-display font-bold text-[18px] tracking-tight" style={{ color: "#E2EAF6" }}>VentureOS</div>
                <div className="text-[10px] font-mono tracking-[0.2em] uppercase mt-0.5" style={{ color: "#3A4E66" }}>startup intelligence</div>
              </div>
            </div>
            <p className="text-[13px] leading-relaxed max-w-[38ch]" style={{ color: "#4A6280" }}>
              Mission control for India's startup ecosystem. Daily intelligence on funding, M&A, policy, and deep tech — built by founders, for founders.
            </p>
            <div className="flex items-center gap-3 mt-5">
              {SOCIALS.map(({ Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-150 hover:opacity-80"
                  style={{ background: "#0D1321", border: "1px solid #1C2840" }}
                >
                  <Icon size={14} strokeWidth={1.75} style={{ color: "#7A90A8" }} />
                </a>
              ))}
            </div>
          </div>

          {/* Newsletter */}
          <div className="rounded-xl p-6" style={{ background: "#0D1321", border: "1px solid #1C2840" }}>
            <div className="flex items-center gap-2 mb-3">
              <Zap size={14} style={{ color: "#2D7AFF" }} />
              <h3 className="font-display font-bold text-[15px]" style={{ color: "#E2EAF6" }}>The Daily Signal</h3>
            </div>
            <p className="text-[12px] mb-4 leading-relaxed" style={{ color: "#5A7090" }}>
              5-minute brief on India's top startup deals and tech moves. Delivered every weekday at 7am IST.
            </p>
            {subscribed ? (
              <div className="flex items-center gap-2 px-4 py-3 rounded-lg text-[13px] font-semibold" style={{ background: "rgba(0,217,200,0.1)", border: "1px solid rgba(0,217,200,0.3)", color: "#00D9C8" }}>
                <span>✓</span><span>You're subscribed — check your inbox!</span>
              </div>
            ) : (
              <form onSubmit={handleSubscribe} className="flex gap-2">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="flex-1 min-w-0 rounded-lg px-3 py-2.5 text-[13px] outline-none transition-all"
                  style={{ background: "#070B12", border: "1px solid #1C2840", color: "#E2EAF6" }}
                />
                <button
                  type="submit"
                  className="flex items-center gap-1.5 text-white text-[13px] font-semibold px-4 py-2.5 rounded-lg whitespace-nowrap hover:opacity-90 transition-opacity"
                  style={{ background: "linear-gradient(135deg, #2D7AFF 0%, #1A5FCC 100%)", boxShadow: "0 2px 8px rgba(45,122,255,0.35)" }}
                >
                  Subscribe <ArrowRight size={12} />
                </button>
              </form>
            )}
            <p className="text-[11px] mt-2.5" style={{ color: "#3A4E66" }}>
              Free · Unsubscribe anytime · We never share your email.
            </p>
          </div>
        </div>

        {/* 3-column link grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-4 rounded-full" style={{ background: "#2D7AFF" }} />
              <h4 className="text-[10px] font-bold uppercase tracking-[0.2em]" style={{ color: "#3A4E66" }}>Coverage</h4>
            </div>
            <nav className="flex flex-col gap-2.5">
              {COVERAGE.map(({ label, href }) => (
                <a key={label} href={href} className="text-[13px] transition-colors hover:text-mint" style={{ color: "#5A7090" }}>{label}</a>
              ))}
            </nav>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-4 rounded-full" style={{ background: "#00D9C8" }} />
              <h4 className="text-[10px] font-bold uppercase tracking-[0.2em]" style={{ color: "#3A4E66" }}>Company</h4>
            </div>
            <nav className="flex flex-col gap-2.5">
              {COMPANY.map(({ label, href }) => (
                <a key={label} href={href} className="text-[13px] transition-colors hover:text-mint" style={{ color: "#5A7090" }}>{label}</a>
              ))}
            </nav>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-4 rounded-full" style={{ background: "#F59E0B" }} />
              <h4 className="text-[10px] font-bold uppercase tracking-[0.2em]" style={{ color: "#3A4E66" }}>Resources</h4>
            </div>
            <nav className="flex flex-col gap-2.5">
              {RESOURCES.map(({ label, href }) => (
                <a key={label} href={href} className="text-[13px] transition-colors hover:text-mint" style={{ color: "#5A7090" }}>{label}</a>
              ))}
            </nav>
          </div>
        </div>

        {/* Bottom strip */}
        <div className="pt-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3" style={{ borderTop: "1px solid #131B2A" }}>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[11px] font-mono" style={{ color: "#2A3D55" }}>© {year} VentureOS. Built in Hyderabad.</span>
            <span style={{ color: "#1C2840" }}>·</span>
            {LEGAL.map(({ label, href }, i) => (
              <span key={label} className="flex items-center gap-2">
                <a href={href} className="text-[11px] transition-colors hover:text-mint" style={{ color: "#2A3D55" }}>{label}</a>
                {i < LEGAL.length - 1 && <span style={{ color: "#1C2840" }}>·</span>}
              </span>
            ))}
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg" style={{ background: "#0D1321", border: "1px solid #1C2840" }}>
            <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "#00D9C8" }} />
            <span className="text-[10px] font-mono uppercase tracking-wider" style={{ color: "#3A4E66" }}>All systems operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
