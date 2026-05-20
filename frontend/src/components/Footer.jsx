import { useContext, useState } from "react";
import { Twitter, Linkedin, Instagram, Youtube } from "lucide-react";
import { AppContext } from "../App";

const COVERAGE = [
  { label: "Markets", href: "/?cat=markets" },
  { label: "Funding Rounds", href: "/?cat=funding" },
  { label: "Startups", href: "/?cat=startups" },
  { label: "Deep Tech", href: "/?cat=deeptech" },
  { label: "Fintech", href: "/?cat=fintech" },
  { label: "SaaS", href: "/?cat=saas" },
  { label: "Policy", href: "/?cat=policy" },
  { label: "IPOs", href: "/?cat=ipo" },
  { label: "Venture Capital", href: "/?cat=vc" },
  { label: "Climate", href: "/?cat=climate" },
];

const INSIDE = [
  { label: "About", href: "/about" },
  { label: "Our Team", href: "/team" },
  { label: "Editorial Standards", href: "/editorial-standards" },
  { label: "Pitch a Story", href: "/pitch" },
  { label: "Advertise", href: "/advertise" },
  { label: "Careers", href: "/careers" },
  { label: "Contact", href: "/contact" },
];

const LEGAL = [
  { label: "Privacy", href: "/privacy-policy" },
  { label: "Terms", href: "/terms" },
  { label: "Cookies", href: "/cookie-policy" },
  { label: "Disclaimer", href: "/disclaimer" },
  { label: "RSS", href: "/rss" },
];

const SOCIALS = [
  { Icon: Twitter, href: "https://twitter.com/mintstreet", label: "Twitter / X" },
  { Icon: Linkedin, href: "https://linkedin.com/company/mintstreet", label: "LinkedIn" },
  { Icon: Instagram, href: "https://instagram.com/mintstreet", label: "Instagram" },
  { Icon: Youtube, href: "https://youtube.com/@mintstreet", label: "YouTube" },
];

export const Footer = () => {
  const { darkMode } = useContext(AppContext);
  const [email, setEmail] = useState("");

  const handleSubscribe = (e) => {
    e.preventDefault();
    console.log("Mint Street newsletter subscribe:", email);
    setEmail("");
  };

  const year = new Date().getFullYear();

  return (
    <footer
      data-testid="footer"
      className={`mt-12 border-t-2 border-mint ${
        darkMode ? "bg-[#1C1410]" : "bg-[#FAF7F1]"
      }`}
    >
      <div className="max-w-screen-xl mx-auto px-6 py-10">
        {/* Newsletter band */}
        <div
          className={`pb-8 mb-8 grid grid-cols-1 md:grid-cols-3 gap-8 items-center border-b ${
            darkMode ? "border-[#1F2A26]" : "border-[#E5E0D6]"
          }`}
        >
          <div className="md:col-span-2">
            <h2
              className={`font-display text-[28px] md:text-[32px] font-bold leading-tight ${
                darkMode ? "text-[#F4EEDF]" : "text-ink"
              }`}
            >
              The newsletter that funds your morning.
            </h2>
            <p
              className={`text-[14px] mt-2 ${
                darkMode ? "text-[#A8B3AE]" : "text-ink-muted"
              }`}
            >
              A 5-minute brief on Indian + global startup deals, every weekday at 7am IST.
            </p>
          </div>

          <div className="md:col-span-1">
            <form
              onSubmit={handleSubscribe}
              className="flex flex-col sm:flex-row gap-2"
            >
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className={`flex-1 min-w-0 rounded-full px-4 py-2.5 text-[13px] outline-none border border-mint focus:ring-2 focus:ring-mint ${
                  darkMode
                    ? "bg-[#16201D] text-[#F4EEDF] placeholder:text-[#6B7975]"
                    : "bg-white text-ink placeholder:text-ink-muted"
                }`}
              />
              <button
                type="submit"
                className="bg-mint text-white rounded-full px-5 py-2.5 text-[13px] font-semibold hover:opacity-90 transition-opacity whitespace-nowrap"
              >
                Subscribe →
              </button>
            </form>
            <p
              className={`text-[11px] mt-2 ${
                darkMode ? "text-[#7A8581]" : "text-ink-muted"
              }`}
            >
              Free. Unsubscribe anytime. We never share your email.
            </p>
          </div>
        </div>

        {/* Main 3-column grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {/* Column 1 - Mint Street brand */}
          <div>
            <span
              className={`font-display text-[20px] font-black tracking-tight leading-none ${
                darkMode ? "text-[#F4EEDF]" : "text-ink"
              }`}
            >
              Mint Street
            </span>
            <p
              className={`text-[12px] leading-relaxed mt-3 max-w-[26ch] ${
                darkMode ? "text-[#A8B3AE]" : "text-ink-muted"
              }`}
            >
              Where new money meets new ideas. Daily startup, VC, and policy intelligence - written by people who've shipped, raised, and exited.
            </p>
            <p
              className={`text-[12px] mt-3 ${
                darkMode ? "text-[#A8B3AE]" : "text-ink-muted"
              }`}
            >
              Hyderabad · Bengaluru · 2026
            </p>
            <div className="flex items-center gap-4 mt-4">
              {SOCIALS.map(({ Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className={`transition-colors duration-150 hover:text-mint ${
                    darkMode ? "text-[#A8B3AE]" : "text-ink-muted"
                  }`}
                >
                  <Icon size={16} strokeWidth={1.75} />
                </a>
              ))}
            </div>
          </div>

          {/* Column 2 - Coverage */}
          <div>
            <h3
              className={`text-[10px] font-bold uppercase tracking-[0.18em] mb-3 ${
                darkMode ? "text-[#7A8581]" : "text-ink-muted"
              }`}
            >
              Coverage
            </h3>
            <nav className="flex flex-col gap-2">
              {COVERAGE.map(({ label, href }) => (
                <a
                  key={label}
                  href={href}
                  className={`text-[13px] transition-colors duration-150 hover:text-mint ${
                    darkMode ? "text-[#D4CFC0]" : "text-ink"
                  }`}
                >
                  {label}
                </a>
              ))}
            </nav>
          </div>

          {/* Column 3 - Inside Mint Street */}
          <div>
            <h3
              className={`text-[10px] font-bold uppercase tracking-[0.18em] mb-3 ${
                darkMode ? "text-[#7A8581]" : "text-ink-muted"
              }`}
            >
              Inside Mint Street
            </h3>
            <nav className="flex flex-col gap-2">
              {INSIDE.map(({ label, href }) => (
                <a
                  key={label}
                  href={href}
                  className={`text-[13px] transition-colors duration-150 hover:text-mint ${
                    darkMode ? "text-[#D4CFC0]" : "text-ink"
                  }`}
                >
                  {label}
                </a>
              ))}
            </nav>
          </div>
        </div>

        {/* Bottom strip */}
        <div
          className={`mt-10 pt-6 border-t flex flex-col gap-2 ${
            darkMode ? "border-[#1F2A26]" : "border-[#E5E0D6]"
          }`}
        >
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
            {LEGAL.map(({ label, href }, i) => (
              <span key={label} className="flex items-center gap-2">
                <a
                  href={href}
                  className={`text-[11px] transition-colors duration-150 hover:text-mint ${
                    darkMode ? "text-[#A8B3AE]" : "text-ink-muted"
                  }`}
                >
                  {label}
                </a>
                {i < LEGAL.length - 1 && (
                  <span
                    className={`text-[11px] ${
                      darkMode ? "text-[#3F4A46]" : "text-[#C9C2B3]"
                    }`}
                  >
                    ·
                  </span>
                )}
              </span>
            ))}
          </div>
          <p
            className={`text-[11px] ${
              darkMode ? "text-[#7A8581]" : "text-ink-muted"
            }`}
          >
            © {year}. Made with masala chai in Hyderabad.
          </p>
        </div>
      </div>
    </footer>
  );
};
