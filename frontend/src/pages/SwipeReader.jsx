import { useState, useEffect, useCallback, useRef } from "react";
import { ChevronUp, ChevronDown, Share2, Youtube, RefreshCw } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

export function ShortsPlayer() {
  const [shorts, setShorts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef(null);
  const touchRef = useRef({ startY: 0, startTime: 0 });
  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [containerHeight, setContainerHeight] = useState(0);

  const fetchShorts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/youtube/shorts?max_results=20`);
      const data = await res.json();
      setShorts(data.shorts || []);
    } catch (e) {
      console.error("Failed to fetch shorts:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchShorts(); }, [fetchShorts]);

  useEffect(() => {
    const updateHeight = () => {
      if (containerRef.current) {
        setContainerHeight(containerRef.current.offsetHeight);
      }
    };
    updateHeight();
    window.addEventListener("resize", updateHeight);
    return () => window.removeEventListener("resize", updateHeight);
  }, [loading]);

  const goTo = useCallback((index) => {
    const clamped = Math.max(0, Math.min(index, shorts.length - 1));
    setCurrentIndex(clamped);
    setDragOffset(0);
    setIsDragging(false);
  }, [shorts.length]);

  const onTouchStart = (e) => {
    touchRef.current = { startY: e.touches[0].clientY, startTime: Date.now() };
    setIsDragging(true);
  };

  const onTouchMove = (e) => {
    if (!isDragging) return;
    const dy = e.touches[0].clientY - touchRef.current.startY;
    setDragOffset(dy);
  };

  const onTouchEnd = () => {
    if (!isDragging) return;
    const velocity = Math.abs(dragOffset) / (Date.now() - touchRef.current.startTime) * 1000;
    const threshold = containerHeight * 0.15;

    if (dragOffset < -threshold || (dragOffset < 0 && velocity > 500)) {
      goTo(currentIndex + 1);
    } else if (dragOffset > threshold || (dragOffset > 0 && velocity > 500)) {
      goTo(currentIndex - 1);
    } else {
      setDragOffset(0);
      setIsDragging(false);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "ArrowUp") goTo(currentIndex - 1);
      if (e.key === "ArrowDown") goTo(currentIndex + 1);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [currentIndex, goTo]);

  // Mouse wheel
  const wheelTimeout = useRef(null);
  const onWheel = (e) => {
    if (wheelTimeout.current) return;
    wheelTimeout.current = setTimeout(() => { wheelTimeout.current = null; }, 600);
    if (e.deltaY > 0) goTo(currentIndex + 1);
    else if (e.deltaY < 0) goTo(currentIndex - 1);
  };

  const handleShare = (short) => {
    const url = `https://youtube.com/shorts/${short.id}`;
    if (navigator.share) {
      navigator.share({ title: short.title, url }).catch(() => {});
    } else {
      window.open(`https://wa.me/?text=${encodeURIComponent(`${short.title}\n${url}`)}`, "_blank");
    }
  };

  const current = shorts[currentIndex];

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center z-40" style={{ top: "56px", bottom: "64px" }}>
        <div className="text-center">
          <div className="w-10 h-10 border-3 border-red-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-white/50 text-sm mt-4">Loading Shorts...</p>
        </div>
      </div>
    );
  }

  if (shorts.length === 0) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center z-40" style={{ top: "56px", bottom: "64px" }}>
        <div className="text-center">
          <Youtube size={48} className="text-white/30 mx-auto mb-3" />
          <p className="text-white/60">No shorts available</p>
          <button onClick={fetchShorts} className="mt-4 flex items-center gap-2 text-red-500 text-sm mx-auto">
            <RefreshCw size={14} /> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="shorts-player"
      ref={containerRef}
      className="fixed inset-0 bg-black overflow-hidden z-40 select-none"
      style={{ top: "56px", bottom: "64px" }}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
      onWheel={onWheel}
    >
      {/* Shorts stack */}
      <div
        className="absolute inset-0"
        style={{
          transform: `translateY(${-currentIndex * 100 + (dragOffset / (containerHeight || 1)) * 100}%)`,
          transition: isDragging ? "none" : "transform 0.35s cubic-bezier(0.25, 0.1, 0.25, 1)",
        }}
      >
        {shorts.map((short, i) => (
          <div
            key={short.id}
            className="absolute inset-0 flex items-center justify-center"
            style={{ top: `${i * 100}%`, height: "100%" }}
          >
            {/* YouTube Shorts embed — autoplay only current */}
            {Math.abs(i - currentIndex) <= 1 ? (
              <iframe
                src={`https://www.youtube.com/embed/${short.id}?autoplay=${i === currentIndex ? 1 : 0}&mute=0&loop=1&playlist=${short.id}&controls=0&modestbranding=1&playsinline=1&rel=0&showinfo=0`}
                title={short.title}
                className="w-full h-full"
                style={{ border: "none", pointerEvents: "auto" }}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            ) : (
              <div className="w-full h-full bg-black flex items-center justify-center">
                <img src={short.thumbnail} alt="" className="w-full h-full object-cover opacity-50" />
              </div>
            )}

            {/* Overlay info */}
            <div className="absolute bottom-0 left-0 right-14 p-4 pointer-events-none" style={{ background: "linear-gradient(transparent, rgba(0,0,0,0.8))" }}>
              <p className="text-white font-semibold text-sm line-clamp-2 mb-1">{short.title}</p>
              <p className="text-white/60 text-xs">{short.channel_title}</p>
            </div>

            {/* Side actions */}
            <div className="absolute right-3 bottom-20 flex flex-col items-center gap-5">
              <button
                data-testid="share-short"
                onClick={() => handleShare(short)}
                className="flex flex-col items-center gap-1"
              >
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <Share2 size={18} className="text-white" />
                </div>
                <span className="text-white text-[10px]">Share</span>
              </button>
              <a
                href={`https://youtube.com/shorts/${short.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex flex-col items-center gap-1"
              >
                <div className="w-10 h-10 bg-red-600/80 rounded-full flex items-center justify-center">
                  <Youtube size={18} className="text-white" />
                </div>
                <span className="text-white text-[10px]">YouTube</span>
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Navigation arrows */}
      <div className="absolute right-3 top-1/2 -translate-y-1/2 flex flex-col gap-3 z-10">
        <button
          data-testid="shorts-up"
          onClick={() => goTo(currentIndex - 1)}
          disabled={currentIndex === 0}
          className="w-9 h-9 bg-white/15 backdrop-blur-sm rounded-full flex items-center justify-center disabled:opacity-30"
        >
          <ChevronUp size={20} className="text-white" />
        </button>
        <button
          data-testid="shorts-down"
          onClick={() => goTo(currentIndex + 1)}
          disabled={currentIndex === shorts.length - 1}
          className="w-9 h-9 bg-white/15 backdrop-blur-sm rounded-full flex items-center justify-center disabled:opacity-30"
        >
          <ChevronDown size={20} className="text-white" />
        </button>
      </div>

      {/* Progress dots */}
      <div className="absolute left-3 top-1/2 -translate-y-1/2 flex flex-col gap-1.5 z-10">
        {shorts.slice(Math.max(0, currentIndex - 3), currentIndex + 4).map((_, i) => {
          const actualIndex = Math.max(0, currentIndex - 3) + i;
          return (
            <div
              key={actualIndex}
              className={`rounded-full transition-all ${
                actualIndex === currentIndex ? "w-1.5 h-4 bg-red-500" : "w-1.5 h-1.5 bg-white/30"
              }`}
            />
          );
        })}
      </div>

      {/* Counter */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-black/50 backdrop-blur-sm text-white text-xs px-3 py-1 rounded-full z-10">
        {currentIndex + 1} / {shorts.length}
      </div>
    </div>
  );
}

export default ShortsPlayer;
