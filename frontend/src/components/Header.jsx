import { useContext } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { AppContext } from "../App";
import {
  Moon,
  Sun,
  Settings,
  LogOut,
  Search,
  ChevronLeft,
  Terminal,
  Zap,
} from "lucide-react";

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
  const { darkMode, toggleDarkMode, isAdmin, isLoggedIn, handleLogout } =
    useContext(AppContext);
  const navigate = useNavigate();
  const location = useLocation();

  const isHomePage = location.pathname === "/";

  const today = new Date();
  const formattedDate = today.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  const tickerStream = (
    <div className="flex whitespace-nowrap shrink-0 pr-12 items-center">
      <span className="text-[#7A90A8] text-[10px] font-mono">{formattedDate}</span>
      {TICKER_ITEMS.map((item, i) => (
        <span key={i} className="flex items-center">
          <span className="px-3 text-[#1C2840]">·</span>
          <span className="text-[#A0B4CC]">{item}</span>
        </span>
      ))}
    </div>
  );

  return (
    <header
      className="sticky top-0 z-50 glass-header"
      style={{
        background: "rgba(7, 11, 18, 0.92)",
        borderBottom: "1px solid #1C2840",
      }}
      data-testid="header"
    >
      <style>{`
        @keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
        .vos-nav-link::after {
          content: '';
          position: absolute;
          bottom: -2px;
          left: 50%;
          width: 0;
          height: 2px;
          background: #2D7AFF;
          transform: translateX(-50%);
          transition: width 0.2s ease;
          border-radius: 1px;
        }
        .vos-nav-link:hover::after { width: 70%; }
        .vos-nav-link:hover { color: #2D7AFF; }
      `}</style>

      {/* ── Utility strip (top) ── */}
      <div
        style={{ background: "#040609", borderBottom: "1px solid #131B2A" }}
        className="hidden md:flex items-center h-7 px-4"
      >
        <div className="max-w-screen-xl mx-auto w-full flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal size={10} className="text-[#2D7AFF]" />
            <span className="text-[10px] font-mono text-[#3A4E66] tracking-wider uppercase">
              venture-os v1.0 · mission control for india's startup ecosystem
            </span>
          </div>
          <div className="flex items-center gap-4">
            <a href="/reporter-login" className="text-[10px] text-[#3A4E66] hover:text-[#2D7AFF] transition-colors uppercase tracking-wider">
              Reporter Login
            </a>
            <a href="/write-for-us" className="text-[10px] text-[#3A4E66] hover:text-[#2D7AFF] transition-colors uppercase tracking-wider">
              Write For Us
            </a>
            <a href="/advertise" className="text-[10px] text-[#3A4E66] hover:text-[#2D7AFF] transition-colors uppercase tracking-wider">
              Advertise
            </a>
          </div>
        </div>
      </div>

      {/* ── Primary bar ── */}
      <div className="h-14 flex items-center" style={{ borderBottom: "1px solid #131B2A" }}>
        <div className="max-w-screen-xl mx-auto px-4 w-full flex items-center justify-between gap-4">

          {/* LEFT: logo */}
          <div className="flex items-center gap-2 min-w-0">
            {!isHomePage && (
              <button
                data-testid="back-btn"
                onClick={() =>
                  window.history.length > 1 ? navigate(-1) : navigate("/")
                }
                className="p-1.5 rounded-md transition-colors text-[#7A90A8] hover:text-[#E2EAF6] hover:bg-[#131B2A]"
                aria-label="Go back"
              >
                <ChevronLeft size={18} />
              </button>
            )}

            <button
              data-testid="logo"
              onClick={() => navigate("/")}
              className="flex items-center gap-2.5 select-none group"
              aria-label="Venture OS home"
            >
              <div className="relative">
                <img
                  src="/logo.svg"
                  alt="Venture OS"
                  className="w-8 h-8 rounded-lg"
                />
                <div
                  className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  style={{ boxShadow: "0 0 12px rgba(45, 122, 255, 0.6)" }}
                />
              </div>
              <div className="flex flex-col leading-none">
                <span className="font-display font-bold text-[16px] tracking-tight text-[#E2EAF6] group-hover:text-white transition-colors">
                  VentureOS
                </span>
                <span className="text-[9px] font-mono text-[#3A4E66] tracking-[0.2em] uppercase mt-0.5">
                  startup intelligence
                </span>
              </div>
            </button>
          </div>

          {/* CENTER: nav links */}
          <nav
            className="hidden md:flex items-center gap-0"
            data-testid="nav-pill"
          >
            {NAV_LINKS.map((link) => (
              <button
                key={link.slug}
                type="button"
                onClick={() => navigate(`/?cat=${link.slug}`)}
                className="vos-nav-link relative px-4 py-2 text-[13px] font-medium text-[#7A90A8] transition-colors duration-200"
              >
                {link.label}
              </button>
            ))}
          </nav>

          {/* RIGHT: actions */}
          <div className="flex items-center gap-1">
            <button
              data-testid="search-btn"
              className="p-2 rounded-lg text-[#7A90A8] hover:text-[#E2EAF6] hover:bg-[#131B2A] transition-colors"
              aria-label="Search"
            >
              <Search size={15} />
            </button>

            <button
              data-testid="dark-mode-toggle"
              onClick={toggleDarkMode}
              className="p-2 rounded-lg text-[#7A90A8] hover:text-[#E2EAF6] hover:bg-[#131B2A] transition-colors"
              aria-label="Toggle theme"
            >
              {darkMode ? <Sun size={15} /> : <Moon size={15} />}
            </button>

            {isAdmin && (
              <button
                data-testid="admin-btn"
                onClick={() => navigate("/admin")}
                className="p-2 rounded-lg text-[#7A90A8] hover:text-[#E2EAF6] hover:bg-[#131B2A] transition-colors"
                aria-label="Admin settings"
              >
                <Settings size={15} />
              </button>
            )}

            {isLoggedIn && (
              <button
                data-testid="logout-btn"
                onClick={handleLogout}
                className="p-2 rounded-lg text-[#7A90A8] hover:text-red-400 hover:bg-[#131B2A] transition-colors"
                aria-label="Log out"
              >
                <LogOut size={15} />
              </button>
            )}

            <button
              data-testid="subscribe-btn"
              className="flex items-center gap-1.5 text-white text-[12px] font-semibold px-4 py-1.5 rounded-lg ml-1 transition-all duration-200 hover:scale-105"
              style={{
                background: "linear-gradient(135deg, #2D7AFF 0%, #1A5FCC 100%)",
                boxShadow: "0 2px 8px rgba(45, 122, 255, 0.35)",
              }}
            >
              <Zap size={11} />
              Subscribe
            </button>
          </div>
        </div>
      </div>

      {/* ── Live ticker strip ── */}
      <div
        className="h-7 flex items-center overflow-hidden relative"
        style={{ background: "#0D1321" }}
        data-testid="ticker"
      >
        <div
          className="shrink-0 flex items-center h-7 px-3 gap-1.5 z-10"
          style={{
            background: "linear-gradient(135deg, #2D7AFF 0%, #1A5FCC 100%)",
          }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
          <span className="text-white text-[10px] font-bold uppercase tracking-[0.15em]">LIVE</span>
        </div>
        <div
          className="flex text-[11px] font-medium uppercase tracking-wider pl-4"
          style={{ animation: "marquee 45s linear infinite" }}
        >
          {tickerStream}
          {tickerStream}
        </div>
      </div>
    </header>
  );
};
