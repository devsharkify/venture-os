import { useContext, useRef, useEffect } from "react";
import { AppContext } from "../App";

export const CategoryChips = ({ activeCategory, onCategoryChange }) => {
  const { categories, darkMode } = useContext(AppContext);
  const scrollRef = useRef(null);

  const categoryList = [
    { key: "all", en: "All" },
    ...Object.entries(categories).map(([key, value]) => ({ key, en: value.en }))
  ];

  useEffect(() => {
    if (scrollRef.current && activeCategory) {
      const activeChip = scrollRef.current.querySelector(`[data-category="${activeCategory}"]`);
      if (activeChip) activeChip.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }
  }, [activeCategory]);

  const stripBg     = darkMode ? "rgba(7,11,18,0.95)"  : "rgba(255,255,255,0.97)";
  const stripBorder = darkMode ? "#1C2840"              : "#E2E8F4";
  const chipBg      = darkMode ? "#0D1321"              : "#F4F7FF";
  const chipBorder  = darkMode ? "#1C2840"              : "#E2E8F4";
  const chipColor   = darkMode ? "#7A90A8"              : "#4A6280";

  return (
    <div
      className="sticky z-40"
      style={{ top: "88px", background: stripBg, borderBottom: `1px solid ${stripBorder}`, backdropFilter: "blur(12px)" }}
      data-testid="category-chips"
    >
      <div ref={scrollRef} className="flex gap-2 overflow-x-auto hide-scrollbar px-4 md:px-6 py-2.5 max-w-screen-xl md:mx-auto chip-scroll-container">
        {categoryList.map((cat) => {
          const isActive = activeCategory === cat.key;
          return (
            <button
              key={cat.key}
              data-category={cat.key}
              data-testid={`category-${cat.key}`}
              onClick={() => onCategoryChange(cat.key)}
              className="flex-shrink-0 rounded-lg px-4 py-1.5 transition-all duration-150 whitespace-nowrap focus:outline-none text-[12px] font-semibold uppercase tracking-wider"
              style={isActive ? {
                background: "linear-gradient(135deg,#2D7AFF 0%,#1A5FCC 100%)",
                color: "white", border: "1px solid #2D7AFF",
                boxShadow: "0 2px 8px rgba(45,122,255,0.25)",
              } : {
                background: chipBg, border: `1px solid ${chipBorder}`, color: chipColor,
              }}
            >
              {cat.en}
            </button>
          );
        })}
      </div>
    </div>
  );
};
