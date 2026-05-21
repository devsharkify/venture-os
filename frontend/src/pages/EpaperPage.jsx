import { useState, useEffect, useRef, useCallback } from "react";
import { API } from "../App";
import axios from "axios";
import { Loader2, Sun, Moon, ChevronLeft, ChevronRight, Download, Calendar, ZoomIn, ZoomOut, Share2 } from "lucide-react";
import { NewspaperPage } from "../components/epaper/NewspaperPage";

const EpaperPage = () => {
  const [editions, setEditions] = useState([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedSlot, setSelectedSlot] = useState("evening");
  const [epaperData, setEpaperData] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showArchive, setShowArchive] = useState(false);
  const viewerRef = useRef(null);
  const pageRefs = useRef([]);
  const isScrollingTo = useRef(false);

  useEffect(() => { fetchEditions(); }, []);
  useEffect(() => { if (selectedDate && selectedSlot) fetchEpaper(selectedDate, selectedSlot); }, [selectedDate, selectedSlot]);

  const fetchEditions = async () => {
    try {
      const r = await axios.get(`${API}/epaper/editions`);
      const eds = r.data.editions || [];
      setEditions(eds);
      if (eds.length > 0) { setSelectedDate(eds[0].date); setSelectedSlot(eds[0].slot || "evening"); }
    } catch (e) { console.error(e); }
  };

  const fetchEpaper = async (date, slot) => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/epaper/${date}?lang=en&slot=${slot}`);
      setEpaperData(r.data);
      setCurrentPage(0);
      pageRefs.current = [];
      if (viewerRef.current) viewerRef.current.scrollTop = 0;
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const downloadPdf = async () => {
    setPdfLoading(true);
    try {
      const r = await axios.get(`${API}/epaper/${selectedDate}/pdf?lang=en&slot=${selectedSlot}`, { responseType: "blob", timeout: 60000 });
      const url = window.URL.createObjectURL(new Blob([r.data]));
      const a = document.createElement("a"); a.href = url; a.download = `tvr_${selectedDate}_${selectedSlot}_en.pdf`;
      document.body.appendChild(a); a.click(); a.remove(); window.URL.revokeObjectURL(url);
    } catch (e) { console.error(e); }
    setPdfLoading(false);
  };

  const shareEpaper = async () => {
    const t = `Venture OS - ${selectedSlot === "morning" ? "Morning" : "Evening"} - ${fmtDate(selectedDate)}`;
    if (navigator.share) { try { await navigator.share({ title: t, text: t, url: window.location.href }); } catch {} }
    else { window.open(`https://wa.me/?text=${encodeURIComponent(t + " " + window.location.href)}`, "_blank"); }
  };

  const fmtDate = (d) => {
    try { return new Date(d + "T12:00:00").toLocaleDateString("en-IN", { day: "numeric", month: "short" }); }
    catch { return d; }
  };
  const fmtDateFull = (d) => {
    if (!d) return "...";
    try { return new Date(d + "T12:00:00").toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short", year: "numeric" }); }
    catch { return d; }
  };
  const slotsForDate = (date) => editions.filter(e => e.date === date).map(e => e.slot);
  const selectEdition = (date, slot) => { setSelectedDate(date); setSelectedSlot(slot); setShowArchive(false); };

  const pages = epaperData?.pages || [];

  // IntersectionObserver for scroll tracking
  useEffect(() => {
    if (!pages.length || !viewerRef.current) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (isScrollingTo.current) return;
        let bestIdx = currentPage, bestRatio = 0;
        entries.forEach(entry => {
          const idx = parseInt(entry.target.dataset.pageIndex, 10);
          if (entry.isIntersecting && entry.intersectionRatio > bestRatio) { bestRatio = entry.intersectionRatio; bestIdx = idx; }
        });
        if (bestRatio > 0) setCurrentPage(bestIdx);
      },
      { root: viewerRef.current, threshold: [0.1, 0.3, 0.5] }
    );
    pageRefs.current.forEach(el => { if (el) observer.observe(el); });
    return () => observer.disconnect();
  }, [pages.length, loading]);

  const goToPage = useCallback((idx) => {
    const el = pageRefs.current[idx];
    if (!el) return;
    isScrollingTo.current = true;
    setCurrentPage(idx);
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    setTimeout(() => { isScrollingTo.current = false; }, 600);
  }, []);

  const uniqueDates = [...new Set(editions.map(e => e.date))];

  return (
    <div className="flex flex-col" style={{ background: "#b0b0b0", height: "calc(100vh - 60px)" }} data-testid="epaper-page">
      {/* COMPACT TOOLBAR */}
      <div className="flex items-center justify-center gap-1.5 px-2 py-1 flex-shrink-0 flex-wrap" style={{ background: "#222", borderBottom: "1px solid #444" }}>
        {/* Page nav */}
        <button onClick={() => goToPage(Math.max(0, currentPage - 1))} disabled={currentPage === 0} className="p-0.5 text-[#5A7090] disabled:opacity-30 hover:text-white" data-testid="epaper-prev-page"><ChevronLeft size={14} /></button>
        <span className="text-[11px] text-[#7A90A8] font-mono">{currentPage + 1}/{pages.length}</span>
        <button onClick={() => goToPage(Math.min(pages.length - 1, currentPage + 1))} disabled={currentPage >= pages.length - 1} className="p-0.5 text-[#5A7090] disabled:opacity-30 hover:text-white" data-testid="epaper-next-page"><ChevronRight size={14} /></button>
        <div className="w-px h-4 bg-[#1C2840]" />
        {/* AM/PM */}
        <div className="flex items-center rounded overflow-hidden border border-[#1C2840]" data-testid="epaper-slot-toggle">
          {["morning", "evening"].map(s => {
            const avail = slotsForDate(selectedDate).includes(s);
            const active = selectedSlot === s;
            return (
              <button key={s} data-testid={`epaper-slot-${s}`} onClick={() => avail && setSelectedSlot(s)} disabled={!avail}
                className="flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-semibold disabled:opacity-30"
                style={{ background: active ? "#c41e1e" : "transparent", color: active ? "#fff" : "#aaa" }}>
                {s === "morning" ? <Sun size={10} /> : <Moon size={10} />}
                {s === "morning" ? "AM" : "PM"}
              </button>
            );
          })}
        </div>
        <div className="w-px h-4 bg-[#1C2840]" />
        {/* Date picker */}
        <div className="relative">
          <button data-testid="epaper-date-picker" onClick={() => setShowDatePicker(!showDatePicker)}
            className="flex items-center gap-1 px-1.5 py-0.5 text-[11px] text-[#7A90A8] rounded hover:bg-[#131B2A] border border-[#1C2840]">
            <Calendar size={10} />{fmtDateFull(selectedDate)}
          </button>
          {showDatePicker && (
            <div className="absolute right-0 top-full mt-1 z-50 max-h-56 overflow-y-auto w-56 shadow-xl rounded bg-[#040609] border border-[#1C2840]">
              {editions.map(e => {
                const isActive = e.date === selectedDate && e.slot === selectedSlot;
                return (
                  <button key={`${e.date}_${e.slot}`} onClick={() => { selectEdition(e.date, e.slot); setShowDatePicker(false); }}
                    className="w-full text-left px-3 py-1.5 text-[11px] flex justify-between items-center hover:bg-[#0D1321] border-b border-[#131B2A]"
                    style={{ color: isActive ? "#c41e1e" : "#ccc", fontWeight: isActive ? 700 : 400 }}>
                    <span className="flex items-center gap-1">
                      {e.slot === "morning" ? <Sun size={9} className="text-yellow-400" /> : <Moon size={9} className="text-blue-400" />}
                      {fmtDateFull(e.date)}
                    </span>
                    <span className="text-[#4A6280] text-[10px]">{e.article_count}</span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
        <div className="w-px h-4 bg-[#1C2840]" />
        <button data-testid="epaper-share" onClick={shareEpaper} className="p-1 text-[#5A7090] hover:text-white"><Share2 size={13} /></button>
        <button data-testid="epaper-download-pdf" onClick={downloadPdf} disabled={pdfLoading}
          className="flex items-center gap-0.5 px-2 py-0.5 text-[10px] font-bold text-white rounded"
          style={{ background: pdfLoading ? "#555" : "#c41e1e" }}>
          {pdfLoading ? <span className="animate-spin">...</span> : <Download size={10} />}PDF
        </button>
      </div>

      {/* VIEWER - scroll-based pages */}
      <div className="flex-1 overflow-auto" ref={viewerRef} style={{ background: "#a0a0a0" }}>
        {loading ? (
          <div className="flex items-center justify-center h-full"><Loader2 size={28} className="animate-spin text-red-600" /></div>
        ) : pages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-[#4A6280] text-sm">No edition available</div>
        ) : (
          <div className="flex flex-col items-center py-2">
            {pages.map((pg, i) => (
              <div key={i} data-page-index={i} ref={el => { pageRefs.current[i] = el; }}
                className="w-full px-2 sm:px-4 md:px-0 mb-1" style={{ maxWidth: "820px" }}>
                <div style={{ boxShadow: "0 2px 16px rgba(0,0,0,0.35)", borderRadius: "2px", overflow: "hidden" }}>
                  <NewspaperPage articles={pg.articles} title={pg.title} date={selectedDate} pageNum={i + 1} totalPages={pages.length} te={false} slot={selectedSlot} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* COMPACT ARCHIVE - single line of small buttons */}
      <div className="flex-shrink-0 border-t" style={{ background: "#1a1a1a", borderColor: "#c41e1e" }}>
        <div className="flex items-center gap-1.5 px-3 py-1.5 overflow-x-auto" data-testid="epaper-archive">
          <span className="text-[10px] text-[#4A6280] font-semibold uppercase tracking-wide whitespace-nowrap flex-shrink-0">Editions:</span>
          {uniqueDates.slice(0, 14).map(date => {
            const slots = editions.filter(e => e.date === date);
            return slots.map(e => {
              const isActive = e.date === selectedDate && e.slot === selectedSlot;
              return (
                <button key={`${e.date}_${e.slot}`} data-testid={`archive-${e.date}-${e.slot}`}
                  onClick={() => selectEdition(e.date, e.slot)}
                  className="flex items-center gap-0.5 px-2 py-1 rounded whitespace-nowrap flex-shrink-0 transition-colors"
                  style={{
                    background: isActive ? "#c41e1e" : "#2a2a2a",
                    border: `1px solid ${isActive ? "#ff6b6b" : "#444"}`,
                    fontSize: "10px", fontWeight: isActive ? 700 : 500,
                    color: isActive ? "#fff" : "#aaa",
                  }}>
                  {e.slot === "morning" ? <Sun size={9} style={{ color: isActive ? "#fff" : "#eab308" }} /> : <Moon size={9} style={{ color: isActive ? "#fff" : "#60a5fa" }} />}
                  {fmtDate(e.date)}
                </button>
              );
            });
          })}
          {uniqueDates.length > 14 && (
            <button onClick={() => setShowArchive(!showArchive)}
              className="text-[10px] text-red-400 font-semibold whitespace-nowrap flex-shrink-0 hover:text-red-300">
              +{uniqueDates.length - 14} more
            </button>
          )}
        </div>
        {showArchive && (
          <div className="flex items-center gap-1 px-3 pb-1.5 overflow-x-auto flex-wrap">
            {uniqueDates.slice(14).map(date => {
              const slots = editions.filter(e => e.date === date);
              return slots.map(e => {
                const isActive = e.date === selectedDate && e.slot === selectedSlot;
                return (
                  <button key={`${e.date}_${e.slot}`} onClick={() => selectEdition(e.date, e.slot)}
                    className="flex items-center gap-0.5 px-1.5 py-0.5 rounded whitespace-nowrap flex-shrink-0"
                    style={{ background: isActive ? "#c41e1e" : "transparent", border: `1px solid ${isActive ? "#c41e1e" : "#444"}`,
                      fontSize: "9px", color: isActive ? "#fff" : "#777" }}>
                    {e.slot === "morning" ? <Sun size={8} /> : <Moon size={8} />}{fmtDate(e.date)}
                  </button>
                );
              });
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default EpaperPage;
