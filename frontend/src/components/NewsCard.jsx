import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../App";
import { Bookmark, BookmarkCheck, Share2, Pencil } from "lucide-react";

// Source portal URLs for attribution
const SOURCE_URLS = {
  "Venture OS": "https://ventureos.in",
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
  const { darkMode = false, saveArticle, isArticleSaved, openArticle, isAdmin } = useContext(AppContext);

  const cardBg      = darkMode ? "#0D1321"  : "#FFFFFF";
  const cardBorder  = darkMode ? "#1C2840"  : "#E2E8F4";
  const cardBorderH = "#2D7AFF";
  const stripBorder = darkMode ? "#131B2A"  : "#F0F4FF";
  const titleColor  = darkMode ? "#D0DDF0"  : "#0D1321";
  const summaryColor= darkMode ? "#5A7090"  : "#4A6280";
  const metaColor   = darkMode ? "#4A6280"  : "#94A3B8";
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
  const sourceName = article.source || "Venture OS";
  const sourcePortalUrl = SOURCE_URLS[sourceName] || null;

  const handleShare = (e) => {
    e.stopPropagation();
    const shareUrl = `https://ventureos.in/news/${article.id}`;
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
      className="group news-card rounded-xl overflow-hidden border transition-all duration-200"
      style={{ background: cardBg, borderColor: cardBorder }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = cardBorderH; e.currentTarget.style.boxShadow = darkMode ? "0 4px 20px rgba(45,122,255,0.10)" : "0 4px 20px rgba(45,122,255,0.08)"; }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = cardBorder; e.currentTarget.style.boxShadow = "none"; }}
    >
      {/* Top stripe - category (left) + source (right) */}
      <div
        className="flex items-center justify-between px-3 py-2 border-b"
        style={{ borderColor: stripBorder }}
      >
        <div className="min-w-0 flex-1">
          {article.is_pinned ? (
            <span
              className="text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider"
              style={{ background: "rgba(245,158,11,0.15)", color: "#F59E0B", border: "1px solid rgba(245,158,11,0.3)" }}
            >
              Breaking
            </span>
          ) : categoryLabel ? (
            <span className="text-[10px] font-bold uppercase tracking-[0.14em] truncate" style={{ color: "#2D7AFF" }}>
              {categoryLabel}
            </span>
          ) : null}
        </div>

        {sourcePortalUrl ? (
          <button
            onClick={handleSourceClick}
            className="text-[10px] font-medium uppercase tracking-wider truncate ml-2 transition-colors"
            style={{ color: "#4A6280" }}
            onMouseEnter={(e) => { e.currentTarget.style.color = "#2D7AFF"; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = "#4A6280"; }}
            title={`Visit ${sourceName}`}
          >
            {sourceName}
          </button>
        ) : (
          <span className="text-[10px] font-medium uppercase tracking-wider truncate ml-2" style={{ color: "#4A6280" }}>
            {sourceName}
          </span>
        )}
      </div>

      {/* Image - 4:3 */}
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
          className="font-display text-[16px] md:text-[17px] font-bold leading-snug line-clamp-3 mb-2 cursor-pointer transition-colors group-hover:text-mint"
          style={{ color: titleColor }}
        >
          {title}
        </h3>

        {summary && (
          <p
            className="text-[13px] line-clamp-2 mb-3 leading-relaxed"
            style={{ color: summaryColor }}
          >
            {summary}
          </p>
        )}

        {/* Footer meta */}
        <div className="flex items-center justify-between text-[11px]" style={{ color: metaColor }}>
          <div className="flex items-center gap-1 min-w-0">
            <span className="truncate">{getShortDate(article)}</span>
            <span className="opacity-50"> · </span>
            <span className="truncate">{readTime} min read</span>
          </div>

          <div className="flex items-center gap-2 ml-2">
            <button
              onClick={handleShare}
              aria-label="Share"
              className="transition-colors"
              style={{ color: "#4A6280" }}
              onMouseEnter={(e) => { e.currentTarget.style.color = "#2D7AFF"; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = "#4A6280"; }}
            >
              <Share2 size={14} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); saveArticle(article); }}
              aria-label={isSaved ? "Saved" : "Save"}
              className="transition-colors"
              style={{ color: isSaved ? "#2D7AFF" : "#4A6280" }}
              onMouseEnter={(e) => { if (!isSaved) e.currentTarget.style.color = "#2D7AFF"; }}
              onMouseLeave={(e) => { if (!isSaved) e.currentTarget.style.color = "#4A6280"; }}
            >
              {isSaved ? (
                <BookmarkCheck size={14} fill="currentColor" />
              ) : (
                <Bookmark size={14} />
              )}
            </button>
            {isAdmin && (
              <button
                onClick={(e) => { e.stopPropagation(); navigate(`/admin?edit=${article.id}`); }}
                aria-label="Edit"
                className="transition-colors"
                style={{ color: "#4A6280" }}
                onMouseEnter={(e) => { e.currentTarget.style.color = "#2D7AFF"; }}
                onMouseLeave={(e) => { e.currentTarget.style.color = "#4A6280"; }}
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
