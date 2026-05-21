import { useContext } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { AppContext } from "../App";
import { Moon, Sun, Settings, LogOut, Search, ChevronLeft, Terminal, Zap } from "lucide-react";

const NAV_LINKS = [
  { label: "Markets", slug: "ipo" },
  { label: "Funding", slug: "funding" },
  { label: "Startups", slug: "startups" },
  { label: "Policy", slug: "policy" },
  { label: "Deep Tech", slug: "deeptech" },
];

const TICKER_ITEMS = [
  "Razorpay raises $75M Series F at $7.5B valuation",
  "Zepto valued at $5B in latest funding round",
  "NSE files for IPO — India's biggest listing since 2022",
  "OpenAI partners with TCS for enterprise AI rollout",
  "Meesho crosses $1B GMV milestone in Q1 2026",
];

export const Header = () => {
  const { darkMode, toggleDarkMode, isAdmin, isLoggedIn, handleLogout } = useContext(AppContext);
  const navigate = useNavigate();
  const location = useLocation();
  const isHomePage = location.pathname === "/";

  const today = new Date();
  const formattedDate = today.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });

  // Theme tokens
  const bg        = darkMode ? "rgba(7,11,18,0.95)"   : "rgba(255,255,255,0.97)";
  const borderB   = darkMode ? "#1C2840"               : "#E2E8F4";
  const utilBg    = darkMode ? "#040609"               : "#F4F7FF";
  const utilBorder= darkMode ? "#131B2A"               : "#E8EEF8";
  const utilText  = darkMode ? "#3A4E66"               : "#6B7FA0";
  const logoText  = darkMode ? "#E2EAF6"               : "#0D1321";
  const logoSub   = darkMode ? "#3A4E66"               : "#94A3B8";
  const navText   = darkMode ? "#7A90A8"               : "#4A6280";
  const iconBtn   = darkMode ? "#3A4E66"               : "#94A3B8";
  const iconHover = darkMode ? "#131B2A"               : "#F0F4FF";
  const tickerBg  = darkMode ? "#0D1321"               : "#F4F7FF";
  const tickerText= darkMode ? "#A0B4CC"               : "#4A6280";
  const dateText  = darkMode ? "#3A4E66"               : "#94A3B8";

  const tickerStream = (
    <div className="flex whitespace-nowrap shrink-0 pr-12 items-center">
      <span className="text-[10px] font-mono mr-4" style={{ color: dateText }}>{formattedDate}</span>
      {TICKER_ITEMS.map((item, i) => (
        <span key={i} className="flex items-center">
          <span className="px-3 opacity-30">·</span>
          <span style={{ color: tickerText }}>{item}</span>
        </span>
      ))}
    </div>
  );

  return (
    <header
      className="sticky top-0 z-50 glass-header"
      style={{ background: bg, borderBottom: `1px solid ${borderB}`, boxShadow: darkMode ? "none" : "0 1px 0 #E2E8F4" }}
      data-testid="header"
    >
      <style>{`
        @keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
        .vos-nav-link { position: relative; transition: color 0.15s; }
        .vos-nav-link::after {
          content: '';
          position: absolute;
          bottom: -2px; left: 50%;
          width: 0; height: 2px;
          background: #2D7AFF;
          transform: translateX(-50%);
          transition: width 0.2s ease;
          border-radius: 1px;
        }
        .vos-nav-link:hover { color: #2D7AFF !important; }
        .vos-nav-link:hover::after { width: 70%; }
      `}</style>

      {/* Utility strip */}
      <div className="hidden md:flex items-center h-7 px-4" style={{ background: utilBg, borderBottom: `1px solid ${utilBorder}` }}>
        <div className="max-w-screen-xl mx-auto w-full flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal size={10} style={{ color: "#2D7AFF" }} />
            <span className="text-[10px] font-mono tracking-wider uppercase" style={{ color: utilText }}>
              venture-os v1.0 · mission control for india's startup ecosystem
            </span>
          </div>
          <div className="flex items-center gap-4">
            {[["Reporter Login", "/reporter-login"], ["Write For Us", "/write-for-us"], ["Advertise", "/advertise"]].map(([label, href]) => (
              <a key={label} href={href} className="text-[10px] uppercase tracking-wider transition-colors hover:text-mint" style={{ color: utilText }}>{label}</a>
            ))}
          </div>
        </div>
      </div>

      {/* Primary bar */}
      <div className="h-14 flex items-center" style={{ borderBottom: `1px solid ${utilBorder}` }}>
        <div className="max-w-screen-xl mx-auto px-4 w-full flex items-center justify-between gap-4">

          {/* Logo */}
          <div className="flex items-center gap-2 min-w-0">
            {!isHomePage && (
              <button onClick={() => window.history.length > 1 ? navigate(-1) : navigate("/")}
                className="p-1.5 rounded-md transition-colors"
                style={{ color: iconBtn }}
                onMouseEnter={e => e.currentTarget.style.background = iconHover}
                onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                aria-label="Go back">
                <ChevronLeft size={18} />
              </button>
            )}
            <button onClick={() => navigate("/")} className="flex items-center gap-2.5 select-none group" data-testid="logo" aria-label="Venture OS home">
              <div className="relative">
                <img src="/logo.svg" alt="Venture OS" className="w-8 h-8 rounded-lg" />
                <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  style={{ boxShadow: "0 0 12px rgba(45,122,255,0.5)" }} />
              </div>
              <div className="flex flex-col leading-none">
                <span className="font-display font-bold text-[16px] tracking-tight transition-colors" style={{ color: logoText }}>VentureOS</span>
                <span className="text-[9px] font-mono tracking-[0.2em] uppercase mt-0.5" style={{ color: logoSub }}>startup intelligence</span>
              </div>
            </button>
          </div>

          {/* Nav */}
          <nav className="hidden md:flex items-center" data-testid="nav-pill">
            {NAV_LINKS.map(link => (
              <button key={link.slug} type="button" onClick={() => navigate(`/?cat=${link.slug}`)}
                className="vos-nav-link px-4 py-2 text-[13px] font-medium"
                style={{ color: navText }}>
                {link.label}
              </button>
            ))}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-1">
            {[
              { icon: <Search size={15} />, label: "Search", onClick: () => {} },
              { icon: darkMode ? <Sun size={15} /> : <Moon size={15} />, label: "Toggle theme", onClick: toggleDarkMode },
              ...(isAdmin ? [{ icon: <Settings size={15} />, label: "Admin", onClick: () => navigate("/admin") }] : []),
              ...(isLoggedIn ? [{ icon: <LogOut size={15} />, label: "Log out", onClick: handleLogout, danger: true }] : []),
            ].map(({ icon, label, onClick, danger }) => (
              <button key={label} onClick={onClick} aria-label={label}
                className="p-2 rounded-lg transition-colors"
                style={{ color: danger ? undefined : iconBtn }}
                data-testid={label === "Toggle theme" ? "dark-mode-toggle" : label === "Search" ? "search-btn" : label === "Admin" ? "admin-btn" : "logout-btn"}
                onMouseEnter={e => { e.currentTarget.style.background = iconHover; if (danger) e.currentTarget.style.color = "#EF4444"; else e.currentTarget.style.color = darkMode ? "#E2EAF6" : "#0D1321"; }}
                onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = danger ? "" : iconBtn; }}>
                {icon}
              </button>
            ))}

            <button data-testid="subscribe-btn"
              className="flex items-center gap-1.5 text-white text-[12px] font-semibold px-4 py-1.5 rounded-lg ml-1 transition-all duration-200 hover:scale-105"
              style={{ background: "linear-gradient(135deg,#2D7AFF 0%,#1A5FCC 100%)", boxShadow: "0 2px 8px rgba(45,122,255,0.30)" }}>
              <Zap size={11} />Subscribe
            </button>
          </div>
        </div>
      </div>

      {/* Ticker */}
      <div className="h-7 flex items-center overflow-hidden" style={{ background: tickerBg, borderBottom: `1px solid ${utilBorder}` }} data-testid="ticker">
        <div className="shrink-0 flex items-center h-7 px-3 gap-1.5 z-10"
          style={{ background: "linear-gradient(135deg,#2D7AFF 0%,#1A5FCC 100%)" }}>
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
          <span className="text-white text-[10px] font-bold uppercase tracking-[0.15em]">LIVE</span>
        </div>
        <div className="flex text-[11px] font-medium uppercase tracking-wider pl-4"
          style={{ animation: "marquee 45s linear infinite" }}>
          {tickerStream}{tickerStream}
        </div>
      </div>
    </header>
  );
};
