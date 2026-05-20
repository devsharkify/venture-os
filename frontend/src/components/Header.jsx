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
} from "lucide-react";

const NAV_LINKS = [
  { label: "Markets", slug: "ipo" },
  { label: "Funding", slug: "funding" },
  { label: "Startups", slug: "startups" },
  { label: "Policy", slug: "policy" },
  { label: "Deep Tech", slug: "deeptech" },
];

const TICKER_ITEMS = [
  "Razorpay raises $75M Series F",
  "Zepto valued at $5B",
  "NSE files for IPO",
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
    <div className="flex whitespace-nowrap shrink-0 pr-12">
      <span className="opacity-70">{formattedDate}</span>
      <span className="px-2 opacity-50">·</span>
      <span className="text-saffron">LATEST</span>
      {TICKER_ITEMS.map((item) => (
        <span key={item} className="flex items-center">
          <span className="px-2 opacity-50">·</span>
          <span>{item}</span>
        </span>
      ))}
    </div>
  );

  return (
    <header
      className={`sticky top-0 z-50 ${
        darkMode ? "bg-[#1C1410]" : "bg-paper"
      }`}
      data-testid="header"
    >
      <style>{`@keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }`}</style>

      {/* ── Primary bar ── */}
      <div className="h-16 flex items-center">
        <div className="max-w-screen-xl mx-auto px-4 w-full flex items-center justify-between gap-4">
          {/* LEFT: optional back + brand */}
          <div className="flex items-center gap-2 min-w-0">
            {!isHomePage && (
              <button
                data-testid="back-btn"
                onClick={() =>
                  window.history.length > 1 ? navigate(-1) : navigate("/")
                }
                className={`p-1.5 rounded-md transition-colors ${
                  darkMode
                    ? "text-slate-300 hover:bg-[#241A14]"
                    : "text-slate-600 hover:bg-[#EFEADE]"
                }`}
                aria-label="Go back"
              >
                <ChevronLeft size={18} />
              </button>
            )}

            <button
              data-testid="logo"
              onClick={() => navigate("/")}
              className="flex items-center gap-2 select-none"
              aria-label="Mint Street home"
            >
              <span className="w-8 h-8 rounded-md bg-mint flex items-center justify-center shadow-sm">
                <span className="font-display font-black text-white text-[14px] leading-none">
                  M$
                </span>
              </span>
              <span
                className={`font-display font-black text-[22px] leading-none tracking-tight ${
                  darkMode ? "text-paper" : "text-ink"
                }`}
              >
                Mint Street
              </span>
            </button>
          </div>

          {/* CENTER: pill nav (desktop) */}
          <nav
            className="hidden md:flex items-center gap-1"
            data-testid="nav-pill"
          >
            {NAV_LINKS.map((link) => (
              <button
                key={link.slug}
                type="button"
                onClick={() => navigate(`/?cat=${link.slug}`)}
                className={`group relative px-3 py-1.5 text-[13px] font-medium transition-colors ${
                  darkMode
                    ? "text-slate-300 hover:text-mint"
                    : "text-ink/80 hover:text-mint"
                }`}
              >
                {link.label}
                <span className="pointer-events-none absolute left-1/2 -bottom-0.5 h-[2px] w-0 -translate-x-1/2 bg-mint transition-all duration-200 group-hover:w-[70%]" />
              </button>
            ))}
          </nav>

          {/* RIGHT: actions */}
          <div className="flex items-center gap-1">
            <button
              data-testid="search-btn"
              className={`p-2 rounded-full transition-colors ${
                darkMode
                  ? "text-slate-300 hover:bg-[#241A14]"
                  : "text-ink/70 hover:bg-[#EFEADE]"
              }`}
              aria-label="Search"
            >
              <Search size={16} />
            </button>

            <button
              data-testid="dark-mode-toggle"
              onClick={toggleDarkMode}
              className={`p-2 rounded-full transition-colors ${
                darkMode
                  ? "text-slate-300 hover:bg-[#241A14]"
                  : "text-ink/70 hover:bg-[#EFEADE]"
              }`}
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            {isAdmin && (
              <button
                data-testid="admin-btn"
                onClick={() => navigate("/admin")}
                className={`p-2 rounded-full transition-colors ${
                  darkMode
                    ? "text-slate-300 hover:bg-[#241A14]"
                    : "text-ink/70 hover:bg-[#EFEADE]"
                }`}
                aria-label="Admin settings"
              >
                <Settings size={16} />
              </button>
            )}

            {isLoggedIn && (
              <button
                data-testid="logout-btn"
                onClick={handleLogout}
                className={`p-2 rounded-full transition-colors ${
                  darkMode
                    ? "text-slate-300 hover:text-red-400 hover:bg-[#241A14]"
                    : "text-ink/70 hover:text-red-500 hover:bg-[#EFEADE]"
                }`}
                aria-label="Log out"
              >
                <LogOut size={16} />
              </button>
            )}

            <button
              data-testid="subscribe-btn"
              className="bg-mint text-white px-3 py-1.5 rounded-full text-[12px] font-semibold ml-1 hover:bg-mint-dark transition-colors"
            >
              Subscribe
            </button>
          </div>
        </div>
      </div>

      {/* ── Funding ticker strip ── */}
      <div
        className={`h-7 flex items-center overflow-hidden relative ${
          darkMode
            ? "bg-mint-dark text-paper"
            : "bg-ink text-paper"
        }`}
        data-testid="ticker"
      >
        <span className="shrink-0 bg-saffron text-ink px-2 h-7 flex items-center text-[11px] font-bold uppercase tracking-wider z-10">
          TICKER
        </span>
        <div
          className="flex text-[11px] font-semibold uppercase tracking-wider pl-4"
          style={{ animation: "marquee 30s linear infinite" }}
        >
          {tickerStream}
          {tickerStream}
        </div>
      </div>

      {/* ── Hairline divider ── */}
      <div
        className={`border-b ${
          darkMode ? "border-[#241A14]" : "border-[#E5E0D6]"
        }`}
      />
    </header>
  );
};
