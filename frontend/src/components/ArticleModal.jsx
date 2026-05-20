import { useContext, useEffect, useState, useCallback, useRef } from "react";
import { AppContext, API } from "../App";
import axios from "axios";
import { Bookmark, BookmarkCheck, Clock, Share2, X, ChevronLeft, ChevronRight, Heart } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";

const SWIPE_THRESHOLD = 80;

export const ArticleModal = () => {
  const {
    selectedArticle, closeArticle, darkMode,
    saveArticle, isArticleSaved, user,
    articlesList, articleIndex, goNextArticle, goPrevArticle
  } = useContext(AppContext);

  const [direction, setDirection] = useState(0);
  const [dragX, setDragX] = useState(0);
  const [showHeart, setShowHeart] = useState(false);
  const lastTapRef = useRef(0);

  const handleDoubleTap = useCallback((e) => {
    const now = Date.now();
    if (now - lastTapRef.current < 350) {
      e.preventDefault();
      if (selectedArticle && !isArticleSaved(selectedArticle.id)) {
        saveArticle(selectedArticle);
      }
      setShowHeart(true);
      setTimeout(() => setShowHeart(false), 900);
    }
    lastTapRef.current = now;
  }, [selectedArticle, saveArticle, isArticleSaved]);

  useEffect(() => {
    if (selectedArticle?.id) {
      axios.post(`${API}/news/${selectedArticle.id}/view`, null, {
        params: { user_phone: user?.phone || "", source: "app" }
      }).catch(() => {});
    }
  }, [selectedArticle?.id, user?.phone]);

  // Keyboard navigation
  useEffect(() => {
    if (!selectedArticle) return;
    const handler = (e) => {
      if (e.key === "ArrowRight" || e.key === "ArrowDown") { setDirection(1); goNextArticle(); }
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp") { setDirection(-1); goPrevArticle(); }
      else if (e.key === "Escape") closeArticle();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [selectedArticle, goNextArticle, goPrevArticle, closeArticle]);

  const handleDragEnd = useCallback((_, info) => {
    const { offset } = info;
    if (offset.x < -SWIPE_THRESHOLD) { setDirection(1); goNextArticle(); }
    else if (offset.x > SWIPE_THRESHOLD) { setDirection(-1); goPrevArticle(); }
    setDragX(0);
  }, [goNextArticle, goPrevArticle]);

  if (!selectedArticle) return null;

  const article = selectedArticle;
  const isSaved = isArticleSaved(article.id);
  const hasNext = articlesList.length > 0 && articleIndex < articlesList.length - 1;
  const hasPrev = articlesList.length > 0 && articleIndex > 0;
  const title = article.title;
  const summary = article.summary;
  const categoryLabel = article.category_label;

  const seoTitle = article.seo_title || title;
  const seoDesc = (article.seo_description || summary || "").slice(0, 155);

  const getTimeAgo = (dateStr) => {
    try { return formatDistanceToNow(new Date(dateStr), { addSuffix: true }); } catch { return ""; }
  };
  const getExactTime = (dateStr) => {
    try {
      const d = new Date(dateStr);
      const day = d.getDate();
      const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
      let h = d.getHours(); const ampm = h >= 12 ? "PM" : "AM"; h = h % 12 || 12;
      return `${day} ${months[d.getMonth()]} ${d.getFullYear()}, ${h}:${d.getMinutes().toString().padStart(2,"0")} ${ampm}`;
    } catch { return ""; }
  };
  const handleShare = () => {
    // Share the branded mintstreet.in URL so the unfurl card shows the Mint Street domain.
    const shareUrl = `https://www.mintstreet.in/news/${article.id}`;
    const shareText = `${title}\n\n${summary?.slice(0, 180)}...\n\n${shareUrl}`;
    if (navigator.share) {
      navigator.share({ title, text: summary?.slice(0, 200), url: shareUrl }).catch(() => {});
    } else {
      window.open(`https://wa.me/?text=${encodeURIComponent(shareText)}`, "_blank");
    }
  };

  const defaultImages = {
    "local": "https://images.pexels.com/photos/17706648/pexels-photo-17706648.jpeg?auto=compress&cs=tinysrgb&w=600",
    "city": "https://images.pexels.com/photos/3573351/pexels-photo-3573351.jpeg?auto=compress&cs=tinysrgb&w=600",
    "sports": "https://images.pexels.com/photos/31131696/pexels-photo-31131696.jpeg?auto=compress&cs=tinysrgb&w=600",
    "entertainment": "https://images.pexels.com/photos/34818731/pexels-photo-34818731.jpeg?auto=compress&cs=tinysrgb&w=600",
    "tech": "https://images.pexels.com/photos/2777898/pexels-photo-2777898.jpeg?auto=compress&cs=tinysrgb&w=600",
    "health": "https://images.pexels.com/photos/3822688/pexels-photo-3822688.jpeg?auto=compress&cs=tinysrgb&w=600",
    "business": "https://images.pexels.com/photos/6950229/pexels-photo-6950229.jpeg?auto=compress&cs=tinysrgb&w=600",
    "national": "https://images.pexels.com/photos/17706648/pexels-photo-17706648.jpeg?auto=compress&cs=tinysrgb&w=600"
  };
  const imageUrl = article.image || defaultImages[article.category] || defaultImages["national"];

  const cardVariants = {
    enter: (dir) => ({ x: dir > 0 ? 400 : -400, opacity: 0, scale: 0.92 }),
    center: { x: 0, opacity: 1, scale: 1 },
    exit: (dir) => ({ x: dir > 0 ? -400 : 400, opacity: 0, scale: 0.92 }),
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      data-testid="article-modal-overlay"
      onClick={(e) => { if (e.target === e.currentTarget) closeArticle(); }}
    >
      {/* SEO meta handled by document.title */}
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      {/* Nav arrows */}
      {hasPrev && (
        <button data-testid="swipe-prev-btn" onClick={() => { setDirection(-1); goPrevArticle(); }}
          className="absolute left-1 md:left-4 top-1/2 -translate-y-1/2 z-[60] text-black hover:text-orange-600 transition-colors p-1">
          <ChevronLeft size={32} strokeWidth={2.5} />
        </button>
      )}
      {hasNext && (
        <button data-testid="swipe-next-btn" onClick={() => { setDirection(1); goNextArticle(); }}
          className="absolute right-1 md:right-4 top-1/2 -translate-y-1/2 z-[60] text-black hover:text-orange-600 transition-colors p-1">
          <ChevronRight size={32} strokeWidth={2.5} />
        </button>
      )}

      {/* Swipe indicator */}
      {articlesList.length > 1 && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-[60] flex items-center gap-2">
          <span className="text-white/60 text-xs font-mono">{articleIndex + 1} / {articlesList.length}</span>
          <div className="flex gap-1">
            {articlesList.slice(Math.max(0, articleIndex - 3), Math.min(articlesList.length, articleIndex + 4)).map((a, i) => {
              const realIdx = Math.max(0, articleIndex - 3) + i;
              return <div key={a.id} className="rounded-full transition-all" style={{
                width: realIdx === articleIndex ? "16px" : "5px",
                height: "5px",
                background: realIdx === articleIndex ? "#f97316" : "rgba(255,255,255,0.3)",
              }} />;
            })}
          </div>
        </div>
      )}

      {/* Swipeable Card */}
      <AnimatePresence mode="popLayout" custom={direction}>
        <motion.div
          key={article.id}
          custom={direction}
          variants={cardVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{ type: "spring", stiffness: 350, damping: 35 }}
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={0.4}
          onDrag={(_, info) => setDragX(info.offset.x)}
          onDragEnd={handleDragEnd}
          className="relative z-[55] w-[95vw] max-w-2xl max-h-[85vh] overflow-y-auto rounded-2xl touch-pan-y"
          style={{
            background: darkMode ? "#1e293b" : "#fff",
            boxShadow: "0 25px 50px rgba(0,0,0,0.3)",
            rotate: dragX * 0.02,
          }}
          data-testid="article-modal"
        >
          {/* Swipe hint overlays */}
          {dragX < -30 && (
            <div className="absolute inset-0 z-10 flex items-center justify-center pointer-events-none rounded-2xl" style={{ background: "rgba(34,197,94,0.15)" }}>
              <span className="text-green-400 text-lg font-bold tracking-wider">NEXT</span>
            </div>
          )}
          {dragX > 30 && (
            <div className="absolute inset-0 z-10 flex items-center justify-center pointer-events-none rounded-2xl" style={{ background: "rgba(168,85,247,0.15)" }}>
              <span className="text-purple-400 text-lg font-bold tracking-wider">PREV</span>
            </div>
          )}

          {/* Header */}
          <div className={`sticky top-0 z-20 border-b px-4 py-3 flex items-center justify-between ${
            darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-100"
          }`}>
            <div className="flex items-center gap-1.5">
              {articlesList.length > 1 && (
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${darkMode ? "bg-slate-700 text-slate-400" : "bg-slate-100 text-slate-500"}`}>
                  {articleIndex + 1}/{articlesList.length}
                </span>
              )}
            </div>
            <div className="flex items-center gap-1.5">
              <button data-testid="modal-share-btn" onClick={handleShare}
                className={`h-9 w-9 rounded-full flex items-center justify-center transition-colors ${darkMode ? "text-green-400 hover:bg-green-900/30" : "text-slate-500 hover:bg-slate-100"}`}>
                <Share2 size={17} />
              </button>
              <button data-testid="modal-save-btn" onClick={() => saveArticle(article)}
                className={`h-9 w-9 rounded-full flex items-center justify-center transition-colors ${isSaved ? "bg-orange-500 text-white" : darkMode ? "text-slate-300 hover:bg-slate-700" : "text-slate-500 hover:bg-slate-100"}`}>
                {isSaved ? <BookmarkCheck size={17} /> : <Bookmark size={17} />}
              </button>
              <button data-testid="modal-close-btn" onClick={closeArticle}
                className={`h-9 w-9 rounded-full flex items-center justify-center transition-colors ${darkMode ? "text-slate-300 hover:bg-slate-700" : "text-slate-500 hover:bg-slate-100"}`}>
                <X size={17} />
              </button>
            </div>
          </div>

          {/* Image */}
          <div className="relative" onClick={handleDoubleTap} data-testid="article-doubletap-area">
            <img src={imageUrl} alt={title} className="w-full aspect-[2.2/1] object-cover select-none pointer-events-none"
              onError={(e) => { e.target.src = defaultImages["national"]; }} />

            {/* Mint Street Logo Watermark - bottom-right */}
            <div className="absolute bottom-2 right-2 pointer-events-none select-none">
              <div className="flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-black/45 backdrop-blur-sm">
                <img src="/tvr-logo.png" alt="Mint Street" className="h-4 w-auto" />
                <span className="text-[10px] font-bold text-white uppercase tracking-wider">Mint Street</span>
              </div>
            </div>

            {/* Double-tap heart animation */}
            <AnimatePresence>
              {showHeart && (
                <motion.div
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 1.5, opacity: 0 }}
                  transition={{ duration: 0.4, ease: "easeOut" }}
                  className="absolute inset-0 flex items-center justify-center pointer-events-none"
                  data-testid="doubletap-heart"
                >
                  <Heart size={72} fill="#ef4444" stroke="none" className="drop-shadow-lg" />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Content */}
          <div className="p-5">
            <div className="flex items-center gap-3 mb-3">
              <span className="px-2 py-1 rounded text-xs font-semibold text-white bg-orange-500">
                {categoryLabel}
              </span>
              {article.is_pinned && (
                <span className="px-2 py-1 rounded text-xs font-semibold text-white bg-red-600 animate-pulse">
                  BREAKING
                </span>
              )}
              <span className={`flex items-center gap-1 text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                <Clock size={12} />{getExactTime(article.published_at)} · {getTimeAgo(article.published_at)}
              </span>
            </div>
            <h1 className={`text-xl md:text-2xl font-bold mb-4 leading-tight ${darkMode ? "text-white" : "text-slate-900"}`}>
              {title}
            </h1>
            <p className={`text-base leading-relaxed mb-6 ${darkMode ? "text-slate-300" : "text-slate-700"}`}>
              {summary}
            </p>
            {article.seo_keywords?.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-4" data-testid="article-seo-tags">
                {article.seo_keywords.map((tag, i) => (
                  <span key={i} className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${darkMode ? "bg-slate-700 text-slate-300" : "bg-slate-100 text-slate-600"}`}>
                    #{tag}
                  </span>
                ))}
              </div>
            )}
            {/* Gesture hints */}
            {articlesList.length > 1 && (
              <div className={`text-center text-[11px] mt-2 ${darkMode ? "text-slate-500" : "text-slate-400"}`}>
                Swipe left/right to navigate &bull; Double-tap image to save
              </div>
            )}
            {articlesList.length <= 1 && (
              <div className={`text-center text-[11px] mt-2 ${darkMode ? "text-slate-500" : "text-slate-400"}`}>
                Double-tap image to save
              </div>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};
