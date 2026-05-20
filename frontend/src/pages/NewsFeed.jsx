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
        <h2 className="font-display text-[28px] md:text-[36px] font-bold leading-tight text-ink line-clamp-3 mb-3">
          {title}
        </h2>
        <p className="text-[15px] text-ink-muted line-clamp-3 mb-3">
          {summary}
        </p>
        <div className="flex items-center gap-2 text-[12px] text-ink-muted">
          <span className="font-semibold">By Mint Street</span>
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
        <h3 className="font-display text-[15px] font-bold line-clamp-3 text-ink leading-snug">
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
      <div className="px-5 pt-5 pb-3 border-b border-white/20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-white/80 animate-pulse" />
          <span className="text-[11px] font-bold uppercase tracking-widest opacity-90">
            Funding Wire
          </span>
        </div>
        <button
          onClick={() => navigate("/?cat=funding")}
          className="text-[10px] font-semibold opacity-70 hover:opacity-100 transition underline underline-offset-2"
        >
          See all
        </button>
      </div>

      {/* Articles */}
      <div className="flex flex-col flex-1 divide-y divide-white/15">
        {items.map((article) => (
          <button
            key={article.id}
            onClick={() => openArticle(article)}
            className="text-left px-5 py-4 hover:bg-white/10 transition group flex-1 flex flex-col justify-between gap-1.5"
          >
            <span className="text-[13px] font-semibold leading-snug line-clamp-2 group-hover:underline underline-offset-2">
              {article.title}
            </span>
            <div className="flex items-center justify-between mt-1">
              <span className="text-[10px] opacity-60 font-medium">{article.source || "Mint Street"}</span>
              <span className="text-[18px] opacity-40 group-hover:opacity-90 group-hover:translate-x-0.5 transition-all">→</span>
            </div>
          </button>
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
    <div data-testid="news-feed-page" className="min-h-screen pb-20 bg-paper">
      {/* ── Section A: Combined Search + Filter pill bar ── */}
      <div className="flex items-center gap-2 py-3 px-4 bg-paper sticky top-[100px] z-30 border-b border-[#E5E0D6]">
        <div className="relative flex-1 flex items-center">
          <Search size={15} className="absolute left-4 text-ink-muted pointer-events-none" />
          <input
            data-testid="search-input"
            type="text"
            value={searchInput}
            onChange={(e) => handleSearchInput(e.target.value)}
            placeholder="Search articles..."
            className="w-full pl-10 pr-28 py-2 text-sm rounded-full border border-[#E5E0D6] bg-white text-ink placeholder:text-ink-muted outline-none transition-all focus:border-mint focus:ring-2 focus:ring-mint/20"
          />
          {isSearching && !loading && (
            <span className="absolute right-10 text-[11px] text-mint font-medium pointer-events-none">
              {`${searchTotal} result${searchTotal !== 1 ? "s" : ""}`}
            </span>
          )}
          {searchInput && (
            <button
              data-testid="search-clear-btn"
              onClick={clearSearch}
              className="absolute right-3 p-0.5 rounded-full text-ink-muted hover:text-ink hover:bg-[#E5E0D6]/60"
            >
              <X size={14} />
            </button>
          )}
        </div>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="text-[12px] font-semibold rounded-full border border-mint/40 bg-white text-ink px-3 py-2 outline-none cursor-pointer hover:border-mint transition"
        >
          {SORT_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        <select
          value={timeFilter}
          onChange={(e) => setTimeFilter(e.target.value)}
          className="text-[12px] font-semibold rounded-full border border-mint/40 bg-white text-ink px-3 py-2 outline-none cursor-pointer hover:border-mint transition"
        >
          {TIME_FILTERS.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
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
