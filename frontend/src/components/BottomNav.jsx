import { useContext } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { AppContext } from "../App";
import { Home, Bookmark, Layers, Newspaper } from "lucide-react";

export const BottomNav = () => {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();
  const location = useLocation();

  const navBg     = darkMode ? "rgba(7,11,18,0.96)"   : "rgba(255,255,255,0.97)";
  const navBorder = darkMode ? "#1C2840"               : "#E2E8F4";
  const inactiveC = darkMode ? "#3A4E66"               : "#94A3B8";

  const navItems = [
    { path: "/", icon: Home, label: "Home" },
    { path: "/swipe", icon: Layers, label: "Shorts" },
    { path: "/epaper", icon: Newspaper, label: "ePaper" },
    { path: "/saved", icon: Bookmark, label: "Saved" },
  ];

  return (
    <nav className="bottom-nav" style={{ background: navBg, borderColor: navBorder }} data-testid="bottom-nav">
      <div className="flex justify-around items-center h-16 max-w-lg mx-auto">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <button key={label} onClick={() => navigate(path)}
              data-testid={`nav-${path === "/" ? "home" : label.toLowerCase()}`}
              className="flex flex-col items-center justify-center w-16 h-full transition-all duration-200"
              style={{ color: isActive ? "#2D7AFF" : inactiveC }}>
              <Icon size={20} strokeWidth={isActive ? 2.5 : 1.8} className="mb-0.5" />
              <span className={`text-[10px] tracking-wide uppercase ${isActive ? "font-bold" : "font-medium"}`}>{label}</span>
              {isActive && (
                <div className="w-4 h-0.5 rounded-full mt-0.5"
                  style={{ background: "linear-gradient(90deg,#2D7AFF,#00D9C8)" }} />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
