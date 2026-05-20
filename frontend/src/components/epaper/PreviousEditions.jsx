import { useState } from "react";
import { Archive, ChevronDown, Sun, Moon } from "lucide-react";

export const PreviousEditions = ({ recentDates, editions, olderByMonth, selectedDate, selectedSlot, selectEdition, fmtDate }) => {
  const [showOlder, setShowOlder] = useState(false);
  const months = Object.keys(olderByMonth);

  const getDayName = (d) => {
    try { return new Date(d + "T12:00:00").toLocaleDateString("en-IN", { weekday: "short" }); } catch { return ""; }
  };
  const getDayNum = (d) => {
    try { return new Date(d + "T12:00:00").getDate(); } catch { return ""; }
  };
  const getMonthShort = (d) => {
    try { return new Date(d + "T12:00:00").toLocaleDateString("en-IN", { month: "short" }); } catch { return ""; }
  };
  const slotsFor = (date) => editions.filter(e => e.date === date);
  const scrollToTop = () => window.scrollTo({ top: 0, behavior: "smooth" });

  return (
    <div style={{ background: "#1a1a1a", borderTop: "4px solid #F26B1F" }} data-testid="epaper-archive">
      <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "28px 20px 0" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
          <Archive size={20} style={{ color: "#F26B1F" }} />
          <h2 style={{ fontSize: "22px", fontWeight: 800, color: "#fff", fontFamily: "'Fraunces', Georgia, serif", letterSpacing: "0.5px" }}>
            Previous Editions
          </h2>
        </div>
        <p style={{ fontSize: "13px", color: "#888", marginBottom: "20px" }}>
          Browse past morning and evening editions of Mint Street ePaper
        </p>

        {/* Recent 7 Days */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: "12px", marginBottom: "28px" }}>
          {recentDates.map(date => {
            const slots = slotsFor(date);
            const totalCount = slots.reduce((s, e) => s + e.article_count, 0);
            return (
              <div key={date} data-testid={`archive-card-${date}`}
                style={{ background: "#2a2a2a", border: selectedDate === date ? "2px solid #F26B1F" : "1px solid #3a3a3a", borderRadius: "8px", padding: "14px 10px", textAlign: "center" }}>
                <div style={{
                  width: "44px", height: "44px", borderRadius: "50%",
                  background: selectedDate === date ? "rgba(196,30,30,0.2)" : "#333",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  margin: "0 auto 8px", fontSize: "20px", fontWeight: 900,
                  color: selectedDate === date ? "#F26B1F" : "#ccc", fontFamily: "'Fraunces', serif",
                }}>{getDayNum(date)}</div>
                <div style={{ fontSize: "11px", fontWeight: 700, color: "#ddd", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  {getDayName(date)}, {getMonthShort(date)}
                </div>
                <div style={{ fontSize: "10px", color: "#777", marginTop: "2px", marginBottom: "8px" }}>{totalCount} articles</div>
                <div style={{ display: "flex", gap: "6px", justifyContent: "center" }}>
                  {["morning", "evening"].map(s => {
                    const ed = slots.find(e => e.slot === s);
                    const isActive = selectedDate === date && selectedSlot === s;
                    return (
                      <button key={s} data-testid={`archive-${date}-${s}`}
                        onClick={() => { if (ed) { selectEdition(date, s); scrollToTop(); } }}
                        disabled={!ed}
                        style={{
                          flex: 1, padding: "5px 4px", borderRadius: "4px", cursor: ed ? "pointer" : "default",
                          background: isActive ? "#F26B1F" : ed ? "#3a3a3a" : "#2a2a2a",
                          border: isActive ? "1px solid #ff6b6b" : "1px solid #444",
                          opacity: ed ? 1 : 0.3, fontSize: "10px", fontWeight: 700,
                          color: isActive ? "#fff" : "#aaa",
                          display: "flex", alignItems: "center", justifyContent: "center", gap: "3px",
                        }}>
                        {s === "morning" ? <Sun size={10} style={{ color: isActive ? "#fff" : "#eab308" }} /> : <Moon size={10} style={{ color: isActive ? "#fff" : "#60a5fa" }} />}
                        {s === "morning" ? "AM" : "PM"}
                        {ed && <span style={{ fontSize: "8px", color: isActive ? "rgba(255,255,255,0.6)" : "#666" }}>({ed.article_count})</span>}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Older Editions */}
        {months.length > 0 && (
          <div style={{ borderTop: "1px solid #333", paddingTop: "16px", paddingBottom: "24px" }}>
            <button data-testid="archive-show-older" onClick={() => setShowOlder(!showOlder)}
              style={{ display: "flex", alignItems: "center", gap: "8px", background: "none", border: "none", cursor: "pointer", color: "#F26B1F", fontSize: "14px", fontWeight: 700, padding: "0", marginBottom: showOlder ? "16px" : "0" }}>
              <Archive size={16} />Older Editions
              <ChevronDown size={16} style={{ transform: showOlder ? "rotate(180deg)" : "rotate(0)", transition: "transform 0.2s" }} />
            </button>
            {showOlder && (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {months.map(month => (
                  <div key={month}>
                    <div style={{ fontSize: "12px", fontWeight: 700, color: "#888", textTransform: "uppercase", letterSpacing: "1px", marginBottom: "8px", paddingBottom: "4px", borderBottom: "1px solid #333" }}>{month}</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                      {olderByMonth[month].map(e => {
                        const isActive = e.date === selectedDate && e.slot === selectedSlot;
                        return (
                          <button key={`${e.date}_${e.slot}`} data-testid={`archive-link-${e.date}-${e.slot}`}
                            onClick={() => { selectEdition(e.date, e.slot); scrollToTop(); }}
                            style={{
                              background: isActive ? "#F26B1F" : "transparent",
                              border: `1px solid ${isActive ? "#F26B1F" : "#444"}`,
                              borderRadius: "4px", padding: "5px 10px", cursor: "pointer", fontSize: "12px",
                              color: isActive ? "#fff" : "#aaa", fontWeight: isActive ? 700 : 400,
                              display: "flex", alignItems: "center", gap: "4px",
                            }}>
                            {e.slot === "morning" ? <Sun size={10} style={{ color: isActive ? "#fff" : "#eab308" }} /> : <Moon size={10} style={{ color: isActive ? "#fff" : "#60a5fa" }} />}
                            {fmtDate(e.date)}
                            <span style={{ color: isActive ? "rgba(255,255,255,0.6)" : "#666", fontSize: "10px" }}>({e.article_count})</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
