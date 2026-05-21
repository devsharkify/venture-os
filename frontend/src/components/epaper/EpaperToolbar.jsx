import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Maximize2, Calendar, Share2, Download, Loader2, Sun, Moon } from "lucide-react";

export const EpaperToolbar = ({ currentPage, totalPages, zoom, setZoom, goPage, selectedDate, selectedSlot, setSelectedSlot, showDatePicker, setShowDatePicker, editions, fmtDate, shareEpaper, downloadPdf, pdfLoading, slotsForDate, selectEdition }) => (
  <div className="flex items-center justify-center gap-2 px-3 py-1.5 flex-shrink-0 flex-wrap" style={{ background: "#222", borderBottom: "1px solid #444" }}>
    <button onClick={() => goPage(-1)} disabled={currentPage === 0} className="p-1 text-[#5A7090] disabled:opacity-30 hover:text-white" data-testid="epaper-prev-page"><ChevronLeft size={16} /></button>
    <span className="text-xs text-[#7A90A8] font-mono">Pg <strong className="text-white">{currentPage + 1}</strong>/{totalPages}</span>
    <button onClick={() => goPage(1)} disabled={currentPage >= totalPages - 1} className="p-1 text-[#5A7090] disabled:opacity-30 hover:text-white" data-testid="epaper-next-page"><ChevronRight size={16} /></button>
    <div className="w-px h-5 bg-[#1C2840]" />
    {/* Morning / Evening Toggle */}
    <div className="flex items-center rounded overflow-hidden border border-[#1C2840]" data-testid="epaper-slot-toggle">
      {["morning", "evening"].map(s => {
        const available = slotsForDate(selectedDate).includes(s);
        const active = selectedSlot === s;
        return (
          <button key={s} data-testid={`epaper-slot-${s}`}
            onClick={() => available && setSelectedSlot(s)}
            disabled={!available}
            className="flex items-center gap-1 px-2 py-1 text-[11px] font-semibold transition-colors disabled:opacity-30"
            style={{ background: active ? "#c41e1e" : "transparent", color: active ? "#fff" : "#aaa" }}>
            {s === "morning" ? <Sun size={11} /> : <Moon size={11} />}
            {s === "morning" ? "AM" : "PM"}
          </button>
        );
      })}
    </div>
    <div className="w-px h-5 bg-[#1C2840]" />
    <button onClick={() => setZoom(z => Math.max(0.2, z - 0.05))} className="p-1 text-[#5A7090] hover:text-white" data-testid="epaper-zoom-out"><ZoomOut size={14} /></button>
    <span className="text-[10px] text-[#5A7090] w-8 text-center font-mono">{Math.round(zoom * 100)}%</span>
    <button onClick={() => setZoom(z => Math.min(1, z + 0.05))} className="p-1 text-[#5A7090] hover:text-white" data-testid="epaper-zoom-in"><ZoomIn size={14} /></button>
    <button onClick={() => setZoom(0.38)} className="p-1 text-[#5A7090] hover:text-white"><Maximize2 size={13} /></button>
    <div className="w-px h-5 bg-[#1C2840]" />
    <div className="relative">
      <button data-testid="epaper-date-picker" onClick={() => setShowDatePicker(!showDatePicker)} className="flex items-center gap-1 px-2 py-1 text-xs text-[#7A90A8] rounded hover:bg-[#131B2A] border border-[#1C2840]">
        <Calendar size={11} />{fmtDate(selectedDate)}
      </button>
      {showDatePicker && (
        <div className="absolute right-0 top-full mt-1 z-50 max-h-64 overflow-y-auto w-64 shadow-xl rounded bg-[#040609] border border-[#1C2840]">
          {editions.map(e => {
            const isActive = e.date === selectedDate && e.slot === selectedSlot;
            return (
              <button key={`${e.date}_${e.slot}`} onClick={() => { selectEdition(e.date, e.slot); setShowDatePicker(false); }}
                className="w-full text-left px-3 py-2 text-[11px] flex justify-between items-center hover:bg-[#0D1321] border-b border-[#131B2A]"
                style={{ color: isActive ? "#c41e1e" : "#ccc", fontWeight: isActive ? 700 : 400 }}>
                <span className="flex items-center gap-1.5">
                  {e.slot === "morning" ? <Sun size={10} className="text-yellow-400" /> : <Moon size={10} className="text-blue-400" />}
                  {fmtDate(e.date)}
                </span>
                <span className="flex items-center gap-2">
                  <span className="text-[10px] uppercase" style={{ color: e.slot === "morning" ? "#eab308" : "#60a5fa" }}>{e.slot === "morning" ? "AM" : "PM"}</span>
                  <span className="text-[#4A6280]">{e.article_count}</span>
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
    <button data-testid="epaper-share" onClick={shareEpaper} className="flex items-center gap-1 px-2 py-1 text-xs text-[#7A90A8] rounded hover:bg-[#131B2A] border border-[#1C2840]">
      <Share2 size={11} />Share
    </button>
    <button data-testid="epaper-download-pdf" onClick={downloadPdf} disabled={pdfLoading}
      className="flex items-center gap-1 px-3 py-1 text-xs font-bold text-white rounded"
      style={{ background: pdfLoading ? "#555" : "#c41e1e" }}>
      {pdfLoading ? <Loader2 size={11} className="animate-spin" /> : <Download size={11} />}PDF
    </button>
  </div>
);
