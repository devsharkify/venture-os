import { useContext } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { AppContext } from "../App";
import { Home, Bookmark, Layers, Newspaper } from "lucide-react";

export const BottomNav = () => {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: "/", icon: Home, label: "Home" },
    { path: "/swipe", icon: Layers, label: "Shorts" },
    { path: "/epaper", icon: Newspaper, label: "ePaper" },
    { path: "/saved", icon: Bookmark, label: "Saved" },
  ];

  return (
    <nav
      className="bottom-nav"
      style={{
        background: "rgba(7, 11, 18, 0.95)",
        borderColor: "#1C2840",
      }}
      data-testid="bottom-nav"
    >
      <div className="flex justify-around items-center h-16 max-w-lg mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <button
              key={item.label}
              data-testid={`nav-${item.path === "/" ? "home" : item.label.toLowerCase()}`}
              onClick={() => navigate(item.path)}
              className="flex flex-col items-center justify-center w-16 h-full transition-all duration-200"
              style={{ color: isActive ? "#2D7AFF" : "#3A4E66" }}
            >
              <Icon size={20} strokeWidth={isActive ? 2.5 : 1.8} className="mb-0.5" />
              <span className={`text-[10px] tracking-wide uppercase ${isActive ? "font-bold" : "font-medium"}`}>
                {item.label}
              </span>
              {isActive && (
                <div
                  className="w-4 h-0.5 rounded-full mt-0.5"
                  style={{ background: "linear-gradient(90deg, #2D7AFF, #00D9C8)" }}
                />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
