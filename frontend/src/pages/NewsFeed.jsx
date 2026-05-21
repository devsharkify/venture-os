import { useState, useEffect, useContext, useCallback, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import { API, AppContext } from "../App";
import { CategoryChips } from "../components/CategoryChips";
import { NewsCard } from "../components/NewsCard";
import { Loader2, Newspaper, X, Search, Clock } from "lucide-react";
import { Button } from "../components/ui/button";

const SORT_OPTIONS = [
  { value: "newest", label: "New to Old" },
  { value: "oldest", label: "Old to New" },
];

const TIME_FILTERS = [
  { value: "all", label: "All Time" },
  { value: "1d", label: "Last 1 Day" },
  { value: "1w", label: "Last 1 Week" },
  { value: "1m", label: "Last 1 Month" },
  { value: "1y", label: "Last 1 Year" },
];

const DEFAULT_IMAGE = "https://images.pexels.com/photos/17706648/pexels-photo-17706648.jpeg?auto=compress&cs=tinysrgb&w=800";

const DEFAULT_IMAGES = {
  local: "https://images.pexels.com/photos/17706648/pexels-photo-17706648.jpeg?auto=compress&cs=tinysrgb&w=600",
  city: "https://images.pexels.com/photos/3573351/pexels-photo-3573351.jpeg?auto=compress&cs=tinysrgb&w=600",
  state: "https://images.pexels.com/photos/17706648/pexels-photo-17706648.jpeg?auto=compress&cs=tinysrgb&w=600",
  national: "https://images.pexels.com/photos/17706648/pexels-photo-17706648.jpeg?auto=compress&cs=tinysrgb&w=600",
  sports: "https://images.pexels.com/photos/31131696/pexels-photo-31131696.jpeg?auto=compress&cs=tinysrgb&w=600",
  entertainment: "https://images.pexels.com/photos/34818731/pexels-photo-34818731.jpeg?auto=compress&cs=tinysrgb&w=600",
  tech: "https://images.pexels.com/photos/2777898/pexels-photo-2777898.jpeg?auto=compress&cs=tinysrgb&w=600",
  health: "https://images.pexels.com/photos/3822688/pexels-photo-3822688.jpeg?auto=compress&cs=tinysrgb&w=600",
  business: "https://images.pexels.com/photos/6950229/pexels-photo-6950229.jpeg?auto=compress&cs=tinysrgb&w=600",
  international: "https://images.pexels.com/photos/1098460/pexels-photo-1098460.jpeg?auto=compress&cs=tinysrgb&w=600",
};

function getArticleImage(article) {
  return article.image || DEFAULT_IMAGES[article.category] || DEFAULT_IMAGE;
}

function formatDate(dateStr) {
  try {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "numeric", month: "short", year: "numeric"
    });
  } catch {
    return "";
  }
}

function readTimeMin(text) {
  return Math.max(1, Math.ceil((text || "").split(/\s+/).filter(Boolean).length / 200));
}

// ─── LeadTile (Tile A) ────────────────────────────────────────────────────────
function LeadTile({ article }) {
  const { openArticle } = useContext(AppContext);
  if (!article) return null;

  const title = article.title;
  const summary = article.summary;
  const imageUrl = getArticleImage(article);
  const readTime = readTimeMin(article.summary);

  return (
    <article
      className="lg:col-span-2 lg:row-span-3 cursor-pointer group flex flex-col"
      onClick={() => openArticle(article)}
    >
      <div className="relative aspect-[16/10] overflow-hidden rounded-md">
        <img
          src={imageUrl}
          alt={title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          loading="eager"
          onError={(e) => { e.target.src = DEFAULT_IMAGE; }}
        />
        {article.is_pinned && (
          <span className="absolute top-3 left-3 bg-saffron text-white text-[10px] font-bold px-2.5 py-1 rounded uppercase tracking-wider">
            Breaking
          </span>
        )}
      </div>

      <div className="pt-4">
        <h2 className="font-display text-[28px] md:text-[36px] font-bold leading-tight line-clamp-3 mb-3" style={{ color: "var(--vos-text)" }}>
          {title}
        </h2>
        <p className="text-[15px] line-clamp-3 mb-3" style={{ color: "var(--vos-text-muted)" }}>
          {summary}
        </p>
        <div className="flex items-center gap-2 text-[12px] text-ink-muted">
          <span className="font-semibold">By Venture OS</span>
          <span className="opacity-50">·</span>
          <span>{formatDate(article.published_at || article.created_at)}</span>
          <span className="opacity-50">·</span>
          <span>{readTime} min read</span>
        </div>
      </div>
    </article>
  );
}

// ─── MediumTile (Tiles B/C) ───────────────────────────────────────────────────
function MediumTile({ article }) {
  const { openArticle } = useContext(AppContext);
  if (!article) return null;

  const title = article.title;
  const imageUrl = getArticleImage(article);

  return (
    <article
      className="lg:col-span-1 lg:row-span-1 cursor-pointer group flex gap-3"
      onClick={() => openArticle(article)}
    >
      <div className="flex-shrink-0 w-[40%] aspect-[4/3] overflow-hidden rounded-md">
        <img
          src={imageUrl}
          alt={title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
          onError={(e) => { e.target.src = DEFAULT_IMAGE; }}
        />
      </div>
      <div className="flex-1 min-w-0 flex flex-col justify-between">
        <h3 className="font-display text-[15px] font-bold line-clamp-3 leading-snug" style={{ color: "var(--vos-text)" }}>
          {title}
        </h3>
        <div className="flex items-center gap-1.5 text-[11px] text-ink-muted">
          <Clock size={10} />
          <span>{formatDate(article.published_at || article.created_at)}</span>
        </div>
      </div>
    </article>
  );
}

// ─── MarketsTile (Tile D) ─────────────────────────────────────────────────────
function MarketsTile({ articles }) {
  const { openArticle } = useContext(AppContext);
  const navigate = useNavigate();
  const items = (articles || []).slice(0, 3);
  if (items.length === 0) return null;

  return (
    <div className="lg:col-span-1 lg:row-span-1 bg-mint text-white rounded-md overflow-hidden flex flex-col">
      {/* Header */}
      <div className="px-4 pt-4 pb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2 shrink-0">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#070B12] opacity-60" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#070B12]" />
          </span>
          <span className="text-[10px] font-black uppercase tracking-[0.18em]">Funding Wire</span>
        </div>
        <button
          onClick={() => navigate("/?cat=funding")}
          className="text-[10px] font-bold bg-[#070B12]/15 hover:bg-[#070B12]/25 transition-colors px-2.5 py-1 rounded-full"
        >
          See all →
        </button>
      </div>

      <div className="mx-4 border-t border-white/20" />

      {/* Articles */}
      <div className="flex flex-col flex-1 px-4 py-1">
        {items.map((article, i) => (
          <div key={article.id}>
            <button
              onClick={() => openArticle(article)}
              className="w-full text-left py-3.5 hover:bg-[#070B12]/10 -mx-4 px-4 transition-colors group"
            >
              <div className="flex items-start gap-2.5">
                <span className="text-[11px] font-black opacity-25 mt-px tabular-nums w-3.5 shrink-0 text-right">{i + 1}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-[12.5px] font-semibold leading-snug line-clamp-2 group-hover:opacity-80 transition-opacity">
                    {article.title}
                  </p>
                  <div className="flex items-center gap-1.5 mt-1.5">
                    <span className="text-[10px] opacity-50 font-medium">{article.source || "Venture OS"}</span>
                    {article.category && (
                      <>
                        <span className="text-[9px] opacity-30">·</span>
                        <span className="text-[9px] font-bold uppercase tracking-wide opacity-40">{article.category}</span>
                      </>
                    )}
                  </div>
                </div>
                <span className="text-[13px] opacity-30 group-hover:opacity-80 group-hover:translate-x-0.5 transition-all mt-px shrink-0">→</span>
              </div>
            </button>
            {i < items.length - 1 && <div className="border-t border-white/10" />}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── NewsFeed ─────────────────────────────────────────────────────────────────
export default function NewsFeed() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();
  const location = useLocation();
  const urlCat = new URLSearchParams(location.search).get("cat") || "all";
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [activeCategory, setActiveCategory] = useState(urlCat);

  // Keep activeCategory in sync with the URL - header nav navigates to
  // /?cat=funding etc., which should refilter the feed without reload.
  useEffect(() => {
    setActiveCategory(urlCat);
  }, [urlCat]);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const [sortBy, setSortBy] = useState("newest");
  const [timeFilter, setTimeFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [searchTotal, setSearchTotal] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimerRef = useRef(null);
  const LIMIT = 10;

  const fetchNews = useCallback(async (category, skip = 0, append = false, sort = "newest", time = "all") => {
    try {
      if (skip === 0) setLoading(true);
      else setLoadingMore(true);

      let url = `${API}/news/feed?limit=${LIMIT}&skip=${skip}&sort=${sort}&time_filter=${time}`;
      if (category !== "all") {
        url = `${API}/news/category/${category}?limit=${LIMIT}&skip=${skip}&sort=${sort}&time_filter=${time}`;
      }

      const response = await axios.get(url);
      const newArticles = response.data;

      if (append) setArticles(prev => [...prev, ...newArticles]);
      else setArticles(newArticles);
      setHasMore(newArticles.length === LIMIT);
      setLoading(false);
      setLoadingMore(false);
    } catch (error) {
      console.error("Failed to fetch news:", error);
      setLoading(false);
      setLoadingMore(false);
    }
  }, []);

  const searchNews = useCallback(async (query, skip = 0, append = false) => {
    if (!query || query.length < 2) return;
    try {
      if (skip === 0) setLoading(true);
      else setLoadingMore(true);
      const response = await axios.get(`${API}/news/search?q=${encodeURIComponent(query)}&limit=${LIMIT}&skip=${skip}`);
      const data = response.data;
      if (append) setArticles(prev => [...prev, ...data.articles]);
      else setArticles(data.articles);
      setSearchTotal(data.total);
      setHasMore(data.articles.length === LIMIT);
    } catch (e) {
      console.error("Search failed:", e);
    }
    setLoading(false);
    setLoadingMore(false);
  }, []);

  useEffect(() => {
    if (isSearching && searchQuery.length >= 2) {
      searchNews(searchQuery, 0);
      setPage(0);
    } else if (!isSearching) {
      fetchNews(activeCategory, 0, false, sortBy, timeFilter);
      setPage(0);
    }
  }, [activeCategory, sortBy, timeFilter, fetchNews, isSearching, searchQuery, searchNews]);

  const handleCategoryChange = (category) => {
    setActiveCategory(category);
    setPage(0);
    // Sync the URL so deep links + back/forward work.
    if (category === "all") navigate("/");
    else navigate(`/?cat=${category}`);
  };

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    if (isSearching) {
      searchNews(searchQuery, nextPage * LIMIT, true);
    } else {
      fetchNews(activeCategory, nextPage * LIMIT, true, sortBy, timeFilter);
    }
  };

  const handleSearchInput = (value) => {
    setSearchInput(value);
    if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
    if (value.length >= 2) {
      searchTimerRef.current = setTimeout(() => {
        setSearchQuery(value);
        setIsSearching(true);
      }, 400);
    } else if (value.length === 0) {
      setSearchQuery("");
      setIsSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchInput("");
    setSearchQuery("");
    setIsSearching(false);
    if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
  };

  const sectionTitle = activeCategory === "all"
    ? "More from the floor"
    : activeCategory.charAt(0).toUpperCase() + activeCategory.slice(1);

  return (
    <div data-testid="news-feed-page" className="min-h-screen pb-20" style={{ background: "var(--vos-bg)" }}>
      {/* ── Section A: Combined Search + Filter pill bar ── */}
      <div
        className="flex items-center gap-2 py-3 px-4 sticky z-30"
        style={{ top: "100px", background: "var(--vos-bg)", borderBottom: "1px solid var(--vos-border)", backdropFilter: "blur(12px)" }}
      >
        <div className="relative flex-1 flex items-center">
          <Search size={15} className="absolute left-4 pointer-events-none" style={{ color: "#3A4E66" }} />
          <input
            data-testid="search-input"
            type="text"
            value={searchInput}
            onChange={(e) => handleSearchInput(e.target.value)}
            placeholder="Search articles..."
            className="w-full pl-10 pr-28 py-2 text-sm rounded-lg outline-none transition-all"
            style={{
              background: "var(--vos-surface)",
              border: "1px solid var(--vos-border)",
              color: "var(--vos-text)",
            }}
            onFocus={(e) => { e.target.style.borderColor = "#2D7AFF"; }}
            onBlur={(e) => { e.target.style.borderColor = "#1C2840"; }}
          />
          {isSearching && !loading && (
            <span className="absolute right-10 text-[11px] font-medium pointer-events-none" style={{ color: "#2D7AFF" }}>
              {`${searchTotal} result${searchTotal !== 1 ? "s" : ""}`}
            </span>
          )}
          {searchInput && (
            <button
              data-testid="search-clear-btn"
              onClick={clearSearch}
              className="absolute right-3 p-0.5 rounded-full transition-colors"
              style={{ color: "#3A4E66" }}
            >
              <X size={14} />
            </button>
          )}
        </div>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="text-[12px] font-semibold rounded-lg px-3 py-2 outline-none cursor-pointer transition"
          style={{ background: "var(--vos-surface)", border: "1px solid var(--vos-border)", color: "var(--vos-text-muted)" }}
        >
          {SORT_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>

        <select
          value={timeFilter}
          onChange={(e) => setTimeFilter(e.target.value)}
          className="text-[12px] font-semibold rounded-lg px-3 py-2 outline-none cursor-pointer transition"
          style={{ background: "var(--vos-surface)", border: "1px solid var(--vos-border)", color: "var(--vos-text-muted)" }}
        >
          {TIME_FILTERS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {/* Category nav */}
      <CategoryChips
        activeCategory={activeCategory}
        onCategoryChange={handleCategoryChange}
      />

      {/* Loading */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-24">
          <Loader2 size={36} className="animate-spin text-mint mb-4" />
          <p className="text-sm text-ink-muted">
            Loading news...
          </p>
        </div>
      )}

      {/* Empty */}
      {!loading && articles.length === 0 && (
        <div className="flex flex-col items-center justify-center py-24">
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 bg-mint/10">
            <Newspaper size={28} className="text-mint" />
          </div>
          <h3 className="text-base font-bold mb-1 tracking-tight text-ink">
            No articles found
          </h3>
          <p className="text-xs text-center max-w-[240px] text-ink-muted">
            Try adjusting your filters or category
          </p>
        </div>
      )}

      {/* Main content */}
      {!loading && articles.length > 0 && (
        <>
          {/* ── Section B: Bento hero ── */}
          {articles.length >= 1 && (
            <section className="max-w-screen-xl mx-auto px-4 py-8">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 lg:grid-rows-[auto_auto_auto]">
                <LeadTile article={articles[0]} />
                <MediumTile article={articles[1]} />
                <MediumTile article={articles[2]} />
                <MarketsTile articles={articles.slice(3, 6)} />
              </div>
            </section>
          )}

          <div className="max-w-screen-xl mx-auto px-4">
            {/* ── Section C: Divider + title ── */}
            <div className="border-t-2 border-mint mb-1" />
            <div className="flex justify-between items-baseline mb-5 pt-3">
              <h2 className="font-display text-[20px] font-bold text-ink">
                {sectionTitle}
              </h2>
            </div>

            {/* ── Section D: Masonry-ish CSS columns grid ── */}
            {articles.length > 6 && (
              <div className="columns-1 md:columns-2 lg:columns-3 gap-5 space-y-5">
                {articles.slice(6).map((article, index) => (
                  <div key={article.id} className="break-inside-avoid">
                    <NewsCard article={article} index={index + 6} articlesList={articles} />
                  </div>
                ))}
              </div>
            )}

            {/* ── Section E: Load More ── */}
            {hasMore && (
              <div className="flex justify-center mt-10 mb-6">
                <Button
                  data-testid="load-more-btn"
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                  className="bg-mint hover:bg-mint-dark text-white rounded-full px-8 py-3 text-[13px] font-bold uppercase tracking-wider transition-all active:scale-95"
                >
                  {loadingMore ? (
                    <>
                      <Loader2 size={14} className="animate-spin mr-2" />
                      Loading...
                    </>
                  ) : (
                    <span>
                      Load More
                    </span>
                  )}
                </Button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export { NewsFeed };
