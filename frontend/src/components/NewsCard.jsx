import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../App";
import { Bookmark, BookmarkCheck, Share2, Pencil } from "lucide-react";

// Source portal URLs for attribution
const SOURCE_URLS = {
  "Mint Street": "https://mintstreet.in",
  "ET Startups": "https://economictimes.indiatimes.com/small-biz/startups",
  "ET Tech": "https://economictimes.indiatimes.com/tech",
  "ET Markets": "https://economictimes.indiatimes.com/markets",
  "ET Funding": "https://economictimes.indiatimes.com/tech/funding-and-deals",
  "YourStory": "https://yourstory.com",
  "YourStory Funding": "https://yourstory.com/category/funding",
  "Mint": "https://www.livemint.com",
  "Mint Tech": "https://www.livemint.com/technology",
  "Mint Startups": "https://www.livemint.com/companies/start-ups",
  "VCCircle": "https://www.vccircle.com",
  "Entrackr": "https://entrackr.com",
  "Moneycontrol": "https://www.moneycontrol.com",
  "BusinessLine": "https://www.thehindubusinessline.com",
  "Business Standard": "https://www.business-standard.com",
  "Business Standard Tech": "https://www.business-standard.com/technology",
  "NDTV Profit": "https://www.ndtvprofit.com",
  "Financial Express": "https://www.financialexpress.com",
  "TechCrunch": "https://techcrunch.com",
};

const DEFAULT_IMAGES = {
  "funding": "https://images.pexels.com/photos/4386431/pexels-photo-4386431.jpeg?auto=compress&cs=tinysrgb&w=600",
  "startup": "https://images.pexels.com/photos/3184360/pexels-photo-3184360.jpeg?auto=compress&cs=tinysrgb&w=600",
  "vc": "https://images.pexels.com/photos/8867482/pexels-photo-8867482.jpeg?auto=compress&cs=tinysrgb&w=600",
  "ipo": "https://images.pexels.com/photos/7567444/pexels-photo-7567444.jpeg?auto=compress&cs=tinysrgb&w=600",
  "tech": "https://images.pexels.com/photos/1181271/pexels-photo-1181271.jpeg?auto=compress&cs=tinysrgb&w=600",
  "fintech": "https://images.pexels.com/photos/4968391/pexels-photo-4968391.jpeg?auto=compress&cs=tinysrgb&w=600",
  "policy": "https://images.pexels.com/photos/8112172/pexels-photo-8112172.jpeg?auto=compress&cs=tinysrgb&w=600",
  "business": "https://images.pexels.com/photos/3182812/pexels-photo-3182812.jpeg?auto=compress&cs=tinysrgb&w=600",
};

export const NewsCard = ({ article, articlesList = [] }) => {
  const { darkMode, saveArticle, isArticleSaved, openArticle, isAdmin } = useContext(AppContext);
  const navigate = useNavigate();
  const isSaved = isArticleSaved(article.id);

  const title = article.title;
  const summary = article.summary;
  const categoryLabel = article.category_label;

  const readTime = Math.max(1, Math.ceil((article.summary || "").split(/\s+/).filter(Boolean).length / 200));

  // Short date: "20 May"
  const getShortDate = (article) => {
    try {
      const dateStr = article.published_at || article.created_at;
      const d = new Date(dateStr);
      return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
    } catch {
      return "";
    }
  };

  const imageUrl = article.image || DEFAULT_IMAGES[article.category] || DEFAULT_IMAGES["startup"];
  const sourceName = article.source || "Mint Street";
  const sourcePortalUrl = SOURCE_URLS[sourceName] || null;

  const handleShare = (e) => {
    e.stopPropagation();
    const shareUrl = `https://mintstreet.in/news/${article.id}`;
    const shareText = `${title}\n\n${(summary || "").slice(0, 180)}...\n\n${shareUrl}`;
    if (navigator.share) {
      navigator.share({ title, text: (summary || "").slice(0, 200), url: shareUrl }).catch(() => {});
      return;
    }
    window.open(`https://wa.me/?text=${encodeURIComponent(shareText)}`, "_blank");
  };

  const handleSourceClick = (e) => {
    e.stopPropagation();
    if (sourcePortalUrl) {
      window.open(sourcePortalUrl, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <article
      data-testid={`news-card-${article.id}`}
      className={`
        group news-card rounded-sm overflow-hidden border transition-all duration-200
        hover:border-mint hover:shadow-[0_6px_24px_rgba(15,174,127,0.10)]
        ${darkMode
          ? "bg-[#241A14] border-[#3A2A1F]"
          : "bg-white border-[#E5E0D6]"}
      `}
    >
      {/* Top stripe — category (left) + source (right) */}
      <div
        className={`flex items-center justify-between px-3 py-2 border-b ${
          darkMode ? "border-[#3A2A1F]" : "border-[#EFEAE0]"
        }`}
      >
        <div className="min-w-0 flex-1">
          {article.is_pinned ? (
            <span className="bg-saffron text-ink text-[10px] font-bold px-2 py-0.5 rounded-sm uppercase tracking-wider">
              Breaking
            </span>
          ) : categoryLabel ? (
            <span
              className="text-[10px] font-bold uppercase tracking-[0.14em] text-mint truncate"
            >
              {categoryLabel}
            </span>
          ) : null}
        </div>

        {sourcePortalUrl ? (
          <button
            onClick={handleSourceClick}
            className={`text-[10px] font-medium uppercase tracking-wider truncate ml-2 hover:text-mint transition-colors ${
              darkMode ? "text-[#9AA8A2]" : "text-ink-muted"
            }`}
            title={`Visit ${sourceName}`}
          >
            {sourceName}
          </button>
        ) : (
          <span
            className={`text-[10px] font-medium uppercase tracking-wider truncate ml-2 ${
              darkMode ? "text-[#9AA8A2]" : "text-ink-muted"
            }`}
          >
            {sourceName}
          </span>
        )}
      </div>

      {/* Image — 4:3 */}
      <div
        className="relative aspect-[4/3] cursor-pointer overflow-hidden"
        onClick={() => openArticle(article, articlesList)}
      >
        <img
          src={imageUrl}
          alt={title}
          loading="lazy"
          className="w-full h-full object-cover filter brightness-95 group-hover:brightness-100 transition duration-300"
          onError={(e) => { e.target.src = DEFAULT_IMAGES["startup"]; }}
        />
      </div>

      {/* Body */}
      <div className="p-4">
        <h3
          onClick={() => openArticle(article, articlesList)}
          className={`
            font-display text-[16px] md:text-[17px] font-bold leading-snug line-clamp-3 mb-2 cursor-pointer
            ${darkMode ? "text-[#F2EDE2]" : "text-ink"}
          `}
        >
          {title}
        </h3>

        {summary && (
          <p
            className={`text-[13px] line-clamp-2 mb-3 leading-relaxed ${
              darkMode ? "text-[#9AA8A2]" : "text-ink-muted"
            }`}
          >
            {summary}
          </p>
        )}

        {/* Footer meta */}
        <div
          className={`flex items-center justify-between text-[11px] ${
            darkMode ? "text-[#9AA8A2]" : "text-ink-muted"
          }`}
        >
          <div className="flex items-center gap-1 min-w-0">
            <span className="truncate">{getShortDate(article)}</span>
            <span className="opacity-50"> · </span>
            <span className="truncate">{readTime} min read</span>
          </div>

          <div className="flex items-center gap-2 ml-2">
            <button
              onClick={handleShare}
              aria-label="Share"
              className={`hover:text-mint transition-colors ${
                darkMode ? "text-[#9AA8A2]" : "text-ink-muted"
              }`}
            >
              <Share2 size={14} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); saveArticle(article); }}
              aria-label={isSaved ? "Saved" : "Save"}
              className={`transition-colors ${
                isSaved
                  ? "text-mint fill-mint"
                  : darkMode
                    ? "text-[#9AA8A2] hover:text-mint"
                    : "text-ink-muted hover:text-mint"
              }`}
            >
              {isSaved ? (
                <BookmarkCheck size={14} className="text-mint" fill="currentColor" />
              ) : (
                <Bookmark size={14} />
              )}
            </button>
            {isAdmin && (
              <button
                onClick={(e) => { e.stopPropagation(); navigate(`/admin?edit=${article.id}`); }}
                aria-label="Edit"
                className={`hover:text-mint transition-colors ${
                  darkMode ? "text-[#9AA8A2]" : "text-ink-muted"
                }`}
              >
                <Pencil size={14} />
              </button>
            )}
          </div>
        </div>
      </div>
    </article>
  );
};
