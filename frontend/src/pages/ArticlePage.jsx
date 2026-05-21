import { useState, useEffect, useContext } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { API, AppContext } from "../App";
import { Clock, ArrowLeft, Share2, Link2, Check } from "lucide-react";

const DEFAULT_IMAGES = {
  funding: "https://images.pexels.com/photos/6950229/pexels-photo-6950229.jpeg?auto=compress&cs=tinysrgb&w=400",
  startup: "https://images.pexels.com/photos/3184338/pexels-photo-3184338.jpeg?auto=compress&cs=tinysrgb&w=400",
  vc: "https://images.pexels.com/photos/7567443/pexels-photo-7567443.jpeg?auto=compress&cs=tinysrgb&w=400",
  ipo: "https://images.pexels.com/photos/6801874/pexels-photo-6801874.jpeg?auto=compress&cs=tinysrgb&w=400",
  tech: "https://images.pexels.com/photos/2777898/pexels-photo-2777898.jpeg?auto=compress&cs=tinysrgb&w=400",
  fintech: "https://images.pexels.com/photos/50987/money-card-business-credit-card-50987.jpeg?auto=compress&cs=tinysrgb&w=400",
  policy: "https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg?auto=compress&cs=tinysrgb&w=400",
  business: "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=400",
};

function getImage(article) {
  return article.image || DEFAULT_IMAGES[article.category] || DEFAULT_IMAGES.startup;
}

function formatShortDate(dateStr) {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
  } catch { return ""; }
}

// Sidebar card - compact horizontal layout
function SidebarArticleCard({ article, darkMode, onClick }) {
  const title = article.title || "";
  const img = getImage(article);
  const catLabel = article.category_label || "";
  return (
    <div
      onClick={() => onClick(article)}
      className={`flex gap-2.5 cursor-pointer group rounded-lg p-2 -mx-2 transition-colors ${
        darkMode ? "hover:bg-[#0D1321]/60" : "hover:bg-[#0D1321]"
      }`}
    >
      <div className="flex-shrink-0 w-[76px] h-[58px] rounded-md overflow-hidden">
        <img
          src={img}
          alt={title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
          onError={(e) => { e.target.src = DEFAULT_IMAGES.startup; }}
        />
      </div>
      <div className="flex-1 min-w-0">
        {catLabel && (
          <span className="text-[9px] font-bold uppercase tracking-wider text-[#2D7AFF] block mb-0.5">{catLabel}</span>
        )}
        <p className={`text-[12px] font-semibold leading-snug line-clamp-2 ${
          darkMode ? "text-[#D0DDF0]" : "text-[#E2EAF6]"
        }`}>{title}</p>
        <span className={`text-[10px] mt-0.5 block ${darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"}`}>
          {formatShortDate(article.published_at || article.created_at)}
        </span>
      </div>
    </div>
  );
}

export default function ArticlePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { darkMode, openArticle } = useContext(AppContext);
  const [article, setArticle] = useState(null);
  const [relatedArticles, setRelatedArticles] = useState([]);
  const [latestArticles, setLatestArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setLoading(true);
    axios.get(`${API}/news/article/${id}`).then(res => {
      setArticle(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [id]);

  // Load related (same category) + latest articles for sidebars
  useEffect(() => {
    if (!article) return;
    // Related: same category, exclude current
    axios.get(`${API}/news/category/${article.category}?limit=6`).then(res => {
      const items = (res.data.articles || res.data || []).filter(a => (a.id || a._id) !== id).slice(0, 5);
      setRelatedArticles(items);
    }).catch(() => {});
    // Latest: newest articles
    axios.get(`${API}/news?limit=6`).then(res => {
      const items = (res.data.articles || res.data || []).filter(a => (a.id || a._id) !== id).slice(0, 5);
      setLatestArticles(items);
    }).catch(() => {});
  }, [article, id]);

  const title = article ? article.title : "";
  const summary = article ? article.summary : "";
  const category = article ? article.category_label : "";
  const shareUrl = `https://www.ventureos.in/news/${id}`;

  useEffect(() => {
    if (title) document.title = `${title} - Venture OS`;
    return () => { document.title = "Venture OS"; };
  }, [title]);

  const getPublishedTime = (article) => {
    try {
      const dateStr = article.published_at || article.article_published_time || article.created_at;
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return "";
      const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
      let h = d.getHours();
      const ampm = h >= 12 ? "PM" : "AM";
      h = h % 12 || 12;
      return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}, ${h}:${d.getMinutes().toString().padStart(2,"0")} ${ampm}`;
    } catch { return ""; }
  };

  const shareText = `${title}\n\n${(summary || "").slice(0, 180)}...\n\n${shareUrl}`;

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({ title, text: (summary || "").slice(0, 200), url: shareUrl }).catch(() => {});
    } else {
      window.open(`https://wa.me/?text=${encodeURIComponent(shareText)}`, "_blank");
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(shareUrl).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const SHARE_BUTTONS = [
    {
      label: "WhatsApp",
      color: "#25D366",
      href: `https://wa.me/?text=${encodeURIComponent(shareText)}`,
      icon: (
        <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
      ),
    },
    {
      label: "Telegram",
      color: "#0088cc",
      href: `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(title)}`,
      icon: (
        <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
          <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
        </svg>
      ),
    },
    {
      label: "LinkedIn",
      color: "#0A66C2",
      href: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`,
      icon: (
        <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
      ),
    },
    {
      label: "Twitter / X",
      color: "#000000",
      href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(shareUrl)}`,
      icon: (
        <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
      ),
    },
    {
      label: "Instagram",
      color: "#E1306C",
      href: null, // no web URL - use native share or copy
      onClick: () => {
        if (navigator.share) {
          navigator.share({ title, text: shareText, url: shareUrl }).catch(() => {});
        } else {
          navigator.clipboard.writeText(shareText);
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        }
      },
      icon: (
        <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
        </svg>
      ),
    },
  ];

  if (loading) return (
    <div className={`min-h-screen flex items-center justify-center ${darkMode ? "bg-[#070B12]" : "bg-[#070B12]"}`}>
      <div className="animate-spin w-8 h-8 border-2 border-[#2D7AFF] border-t-transparent rounded-full" />
    </div>
  );

  if (!article) return (
    <div className={`min-h-screen flex flex-col items-center justify-center gap-4 ${darkMode ? "bg-[#070B12] text-white" : "bg-[#070B12]"}`}>
      <p>Article not found</p>
      <button onClick={() => navigate("/")} className="text-[#2D7AFF]">Go Home</button>
    </div>
  );

  const publishedTime = getPublishedTime(article);

  return (
    <div data-testid="article-page" className={`min-h-screen pb-10 ${darkMode ? "bg-[#070B12]" : "bg-[#070B12]"}`}>
      {/* Sticky top bar */}
      <div className={`sticky top-0 z-10 px-4 py-3 flex items-center gap-3 border-b ${darkMode ? "bg-[#070B12]/95 border-[#1C2840]" : "bg-[#070B12]/95 border-[#131B2A]"} backdrop-blur`}>
        <button data-testid="article-back-btn" onClick={() => navigate(-1)} className={`p-1.5 rounded-lg ${darkMode ? "hover:bg-[#0D1321]" : "hover:bg-[#131B2A]"}`}>
          <ArrowLeft size={20} />
        </button>
        <span className={`text-sm font-semibold flex-1 truncate ${darkMode ? "text-white" : "text-[#E2EAF6]"}`}>Venture OS</span>
        <button data-testid="article-share-btn" onClick={handleShare} className={`p-1.5 rounded-lg ${darkMode ? "hover:bg-[#0D1321]" : "hover:bg-[#131B2A]"}`}>
          <Share2 size={18} />
        </button>
      </div>

      {/* 3-column layout on lg screens */}
      <div className="max-w-screen-xl mx-auto px-4 py-6 lg:grid lg:grid-cols-[260px_1fr_260px] lg:gap-8">

        {/* ── LEFT SIDEBAR: Related Articles ── */}
        <aside className="hidden lg:block">
          <div className={`sticky top-20 rounded-xl p-4 ${darkMode ? "bg-[#111827] border border-[#1C2840]" : "bg-[#070B12] border border-[#1C2840]"}`}>
            <h3 className={`text-[10px] font-black uppercase tracking-[0.18em] pb-2 mb-3 border-b-2 border-[#2D7AFF] ${darkMode ? "text-[#A0B4CC]" : "text-[#A0B4CC]"}`}>
              Related Stories
            </h3>
            <div className="flex flex-col gap-3">
              {relatedArticles.length > 0 ? relatedArticles.map(a => (
                <SidebarArticleCard
                  key={a.id || a._id}
                  article={a}
                  darkMode={darkMode}
                  onClick={(art) => openArticle(art)}
                />
              )) : (
                <p className={`text-[11px] ${darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"}`}>Loading…</p>
              )}
            </div>
          </div>
        </aside>

        {/* ── MAIN ARTICLE ── */}
        <article className="min-w-0">
          {/* Category + date */}
          <div className="flex items-center gap-2 mb-3">
            <span className="px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-[#2D7AFF] text-white rounded">
              {category}
            </span>
            {publishedTime && (
              <span className={`flex items-center gap-1 text-[11px] ${darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"}`}>
                <Clock size={11} />
                {publishedTime}
              </span>
            )}
          </div>

          {/* Headline */}
          <h1 className={`text-2xl sm:text-3xl font-serif-display font-bold leading-tight mb-5 ${darkMode ? "text-white" : "text-[#E2EAF6]"}`}>
            {title}
          </h1>

          {/* Hero image */}
          {article.image && (
            <div className="mb-0 rounded-xl overflow-hidden">
              <img
                src={article.image}
                alt={title}
                className="w-full max-h-[420px] object-cover"
                onError={(e) => { e.target.style.display = "none"; }}
              />
            </div>
          )}

          {/* ── Social Share Bar ── */}
          <div className={`flex items-center gap-2 flex-wrap py-3 mb-5 border-b ${darkMode ? "border-[#1C2840]" : "border-[#1C2840]"}`}>
            <span className={`text-[10px] font-black uppercase tracking-[0.16em] mr-1 ${darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"}`}>
              Share
            </span>

            {SHARE_BUTTONS.map(({ label, color, href, onClick, icon }) => (
              href ? (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`Share on ${label}`}
                  title={label}
                  className="flex items-center justify-center w-8 h-8 rounded-full transition-opacity hover:opacity-80"
                  style={{ backgroundColor: color, color: "#fff" }}
                >
                  {icon}
                </a>
              ) : (
                <button
                  key={label}
                  onClick={onClick}
                  aria-label={`Share on ${label}`}
                  title={label}
                  className="flex items-center justify-center w-8 h-8 rounded-full transition-opacity hover:opacity-80"
                  style={{ backgroundColor: color, color: "#fff" }}
                >
                  {icon}
                </button>
              )
            ))}

            {/* Copy Link */}
            <button
              onClick={handleCopy}
              aria-label="Copy link"
              title="Copy link"
              className={`flex items-center gap-1.5 px-3 h-8 rounded-full text-[11px] font-semibold transition-all ${
                copied
                  ? "bg-[#00D9C8] text-white"
                  : darkMode
                  ? "bg-[#131B2A] text-[#A0B4CC] hover:bg-[#1C2840]"
                  : "bg-[#131B2A] text-[#7A90A8] hover:bg-[#1C2840]"
              }`}
            >
              {copied ? <Check size={13} /> : <Link2 size={13} />}
              {copied ? "Copied!" : "Copy link"}
            </button>
          </div>

          {/* Body */}
          <div className={`text-base leading-relaxed whitespace-pre-line ${darkMode ? "text-[#A0B4CC]" : "text-[#A0B4CC]"}`}>
            {summary}
          </div>

          {/* Mobile: show related articles below body */}
          {relatedArticles.length > 0 && (
            <div className="lg:hidden mt-8">
              <h3 className={`text-[10px] font-black uppercase tracking-[0.18em] pb-2 mb-3 border-b-2 border-[#2D7AFF] ${darkMode ? "text-[#A0B4CC]" : "text-[#A0B4CC]"}`}>
                Related Stories
              </h3>
              <div className="flex flex-col gap-3">
                {relatedArticles.map(a => (
                  <SidebarArticleCard key={a.id || a._id} article={a} darkMode={darkMode} onClick={(art) => openArticle(art)} />
                ))}
              </div>
            </div>
          )}
        </article>

        {/* ── RIGHT SIDEBAR: Latest News ── */}
        <aside className="hidden lg:block">
          <div className={`sticky top-20 rounded-xl p-4 ${darkMode ? "bg-[#111827] border border-[#1C2840]" : "bg-[#070B12] border border-[#1C2840]"}`}>
            <h3 className={`text-[10px] font-black uppercase tracking-[0.18em] pb-2 mb-3 border-b-2 border-[#2D7AFF] ${darkMode ? "text-[#A0B4CC]" : "text-[#A0B4CC]"}`}>
              Latest News
            </h3>
            <div className="flex flex-col gap-3">
              {latestArticles.length > 0 ? latestArticles.map(a => (
                <SidebarArticleCard
                  key={a.id || a._id}
                  article={a}
                  darkMode={darkMode}
                  onClick={(art) => openArticle(art)}
                />
              )) : (
                <p className={`text-[11px] ${darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"}`}>Loading…</p>
              )}
            </div>
          </div>
        </aside>

      </div>
    </div>
  );
}
