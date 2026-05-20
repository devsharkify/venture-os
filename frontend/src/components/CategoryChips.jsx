import { useContext, useRef, useEffect } from "react";
import { AppContext } from "../App";

export const CategoryChips = ({ activeCategory, onCategoryChange }) => {
  const { language, categories, darkMode } = useContext(AppContext);
  const scrollRef = useRef(null);

  const categoryList = [
    { key: "all", en: "All News", te: "అన్ని వార్తలు" },
    ...Object.entries(categories).map(([key, value]) => ({
      key,
      en: value.en,
      te: value.te
    }))
  ];

  useEffect(() => {
    if (scrollRef.current && activeCategory) {
      const activeChip = scrollRef.current.querySelector(
        `[data-category="${activeCategory}"]`
      );
      if (activeChip) {
        activeChip.scrollIntoView({
          behavior: "smooth",
          inline: "center",
          block: "nearest"
        });
      }
    }
  }, [activeCategory]);

  return (
    <div
      className={`sticky top-[88px] z-40 ${
        darkMode ? "bg-[#0E1714]" : "bg-[#FAF7F1]"
      }`}
      data-testid="category-chips"
    >
      {/* Mint hairline across the top of the nav strip */}
      <div className="h-[2px] bg-[#0FAE7F]" />

      {/* Scrollable chip row */}
      <div
        ref={scrollRef}
        className={`
          flex gap-2 overflow-x-auto hide-scrollbar
          px-4 md:px-6 py-2.5
          max-w-screen-xl md:mx-auto
          chip-scroll-container
        `}
      >
        {categoryList.map((cat) => {
          const isActive = activeCategory === cat.key;
          const isTelugu = language === "te";
          const label = isTelugu ? cat.te : cat.en;

          return (
            <button
              key={cat.key}
              data-category={cat.key}
              data-testid={`category-${cat.key}`}
              onClick={() => onCategoryChange(cat.key)}
              className={`
                flex-shrink-0
                rounded-full px-4 py-1.5
                transition-colors duration-150
                whitespace-nowrap
                focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0FAE7F] focus-visible:ring-offset-1
                ${isTelugu
                  ? "font-telugu normal-case text-[13px] font-semibold tracking-normal"
                  : "text-[12px] font-semibold uppercase tracking-wider"
                }
                ${isActive
                  ? "bg-[#0FAE7F] text-white border border-[#0FAE7F]"
                  : darkMode
                    ? "bg-[#152420] border border-[#1F2D29] text-[#FAF7F1] hover:border-[#0FAE7F] hover:text-[#0FAE7F]"
                    : "bg-white border border-[#E5E0D6] text-[#0E1714] hover:border-[#0FAE7F] hover:text-[#0FAE7F]"
                }
              `}
            >
              {label}
            </button>
          );
        })}
      </div>

      {/* Bottom divider */}
      <div
        className={`h-px ${darkMode ? "bg-[#1F2D29]" : "bg-[#E5E0D6]"}`}
      />
    </div>
  );
};
