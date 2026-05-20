const Masthead = ({ date, fD, slot }) => {
  const edLabel = slot === "morning" ? "Morning Edition" : "Evening Edition";
  return (
    <div style={{ marginBottom: "6px" }}>
      <div style={{ textAlign: "center", padding: "8px 0 4px", borderBottom: "5px double #F26B1F" }}>
        <div style={{ fontSize: "48px", fontWeight: 900, letterSpacing: "6px", fontFamily: "'Fraunces', Georgia, serif", color: "#F26B1F", lineHeight: 1, textTransform: "uppercase" }}>MINT STREET</div>
        <div style={{ fontSize: "8px", color: "#888", fontFamily: "system-ui", letterSpacing: "3px", textTransform: "uppercase", marginTop: "3px" }}>
          Where new money meets new ideas
        </div>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "9px", color: "#555", fontFamily: "system-ui", padding: "4px 0", borderBottom: "2px solid #1a1a1a" }}>
        <span style={{ fontWeight: 600 }}>{fD(date)}</span>
        <span style={{ letterSpacing: "2px", textTransform: "uppercase", fontSize: "8px", color: "#F26B1F", fontWeight: 700 }}>{edLabel}</span>
        <span>mintstreet.in</span>
      </div>
    </div>
  );
};

const InnerHeader = ({ title, date, pageNum, fD, slot }) => {
  const edTag = slot === "morning" ? "Morning" : "Evening";
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", borderBottom: "3px solid #1a1a1a", paddingBottom: "4px", marginBottom: "8px" }}>
      <span style={{ fontSize: "13px", fontWeight: 900, letterSpacing: "3px", textTransform: "uppercase", color: "#F26B1F" }}>MINT STREET</span>
      <span style={{ fontSize: "22px", fontWeight: 900, fontFamily: "'Fraunces', Georgia, serif", color: "#111" }}>{title}</span>
      <span style={{ fontSize: "8px", color: "#888", fontFamily: "system-ui" }}>{fD(date)} | {edTag} | Pg {pageNum}</span>
    </div>
  );
};

const CmykFooter = ({ pageNum, totalPages, date, fD }) => (
  <div style={{ marginTop: "auto", paddingTop: "6px", borderTop: "2px solid #1a1a1a", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
    <div style={{ display: "flex", gap: "3px" }}>
      {["#00bcd4", "#e91e63", "#ffeb3b", "#212121"].map((c, i) => (
        <div key={i} style={{ width: "6px", height: "6px", borderRadius: "50%", background: c }} />
      ))}
    </div>
    <div style={{ fontSize: "7px", color: "#999", fontFamily: "system-ui" }}>mintstreet.in &bull; Page {pageNum}/{totalPages} &bull; {fD(date)}</div>
    <div style={{ display: "flex", gap: "3px" }}>
      {["#212121", "#ffeb3b", "#e91e63", "#00bcd4"].map((c, i) => (
        <div key={i} style={{ width: "6px", height: "6px", borderRadius: "50%", background: c }} />
      ))}
    </div>
  </div>
);

export const NewspaperPage = ({ articles, title, date, pageNum, totalPages, slot }) => {
  const hF = "'Fraunces', Georgia, serif";
  const bF = "'PT Serif', Georgia, serif";
  const fD = (d) => { try { return new Date(d + "T12:00:00").toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" }); } catch { return d; } };

  if (!articles.length) return null;

  // Re-sort: longest summaries first for prominent positions, short ones to tail
  const sorted = [...articles].sort((a, b) => (b.summary?.length || 0) - (a.summary?.length || 0));
  const hero = sorted[0];
  const sub = sorted[1];
  const mid = sorted.slice(2, 5);
  const bottom = sorted.slice(5, 8);
  const tail = sorted.slice(8);

  return (
    <div style={{ background: "#fefcf7", fontFamily: bF, color: "#1a1a1a", width: "100%", position: "relative", overflow: "hidden", display: "flex", flexDirection: "column" }}>
      {/* Newsprint texture */}
      <div style={{ position: "absolute", inset: 0, opacity: 0.025, background: "repeating-linear-gradient(0deg,#000 0px,transparent 1px,transparent 3px)", pointerEvents: "none", zIndex: 1 }} />
      <div style={{ position: "relative", zIndex: 2, padding: "14px 20px 10px", display: "flex", flexDirection: "column", flex: 1 }}>
        {pageNum === 1 ? <Masthead date={date} fD={fD} slot={slot} /> : <InnerHeader title={title} date={date} pageNum={pageNum} fD={fD} slot={slot} />}

        {/* ROW 1: HERO + SUB - full width */}
        <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: "0", borderBottom: "2px solid #1a1a1a", marginBottom: "8px" }}>
          <div style={{ padding: "0 14px 10px 0", borderRight: "1px solid #ccc" }}>
            {hero.image && <img src={hero.image} alt="" style={{ width: "100%", height: "220px", objectFit: "cover", display: "block" }} onError={e => e.target.style.display = "none"} />}
            <h1 style={{ fontSize: "32px", fontWeight: 900, lineHeight: 1.08, fontFamily: hF, color: "#111", margin: "8px 0 6px" }}>{hero.title}</h1>
            <p style={{ fontSize: "13px", lineHeight: 1.65, color: "#333", textAlign: "justify" }}>{hero.summary}</p>
          </div>
          <div style={{ paddingLeft: "14px", display: "flex", flexDirection: "column", justifyContent: "flex-start" }}>
            {sub && (
              <>
                {sub.image && <img src={sub.image} alt="" style={{ width: "100%", height: "140px", objectFit: "cover", display: "block", marginBottom: "6px" }} onError={e => e.target.style.display = "none"} />}
                <h2 style={{ fontSize: sub.image ? "22px" : "26px", fontWeight: 900, lineHeight: 1.1, fontFamily: hF, color: "#111", marginBottom: "5px" }}>{sub.title}</h2>
                <p style={{ fontSize: sub.image ? "12px" : "13px", lineHeight: 1.65, color: "#444", textAlign: "justify" }}>{sub.summary}</p>
              </>
            )}
          </div>
        </div>

        {/* ROW 2: 3 MID ARTICLES - equal columns, stretch to fill */}
        {mid.length > 0 && (
          <div style={{ display: "grid", gridTemplateColumns: `repeat(${mid.length}, 1fr)`, gap: "0", borderBottom: "2px solid #1a1a1a", marginBottom: "8px", alignItems: "stretch" }}>
            {mid.map((a, i) => (
              <div key={a.id} style={{ padding: "8px 12px", borderRight: i < mid.length - 1 ? "1px solid #ccc" : "none", display: "flex", flexDirection: "column" }}>
                {a.image && <img src={a.image} alt="" style={{ width: "100%", height: "100px", objectFit: "cover", display: "block", marginBottom: "6px" }} onError={e => e.target.style.display = "none"} />}
                <h3 style={{ fontSize: "16px", fontWeight: 800, lineHeight: 1.15, fontFamily: hF, color: "#1a1a1a", marginBottom: "4px" }}>{a.title}</h3>
                <p style={{ fontSize: "11px", lineHeight: 1.55, color: "#444", textAlign: "justify", flex: 1 }}>{a.summary}</p>
              </div>
            ))}
          </div>
        )}

        {/* ROW 3: 3 BOTTOM ARTICLES - compact, stretch */}
        {bottom.length > 0 && (
          <div style={{ display: "grid", gridTemplateColumns: `repeat(${bottom.length}, 1fr)`, gap: "0", borderBottom: "1px solid #ccc", marginBottom: "8px", alignItems: "stretch" }}>
            {bottom.map((a, i) => (
              <div key={a.id} style={{ padding: "6px 10px", borderRight: i < bottom.length - 1 ? "1px solid #ccc" : "none", display: "flex", flexDirection: "column" }}>
                {a.image && i === 0 && <img src={a.image} alt="" style={{ float: "left", width: "40%", height: "70px", objectFit: "cover", marginRight: "8px", marginBottom: "4px" }} onError={e => e.target.style.display = "none"} />}
                <h4 style={{ fontSize: "14px", fontWeight: 700, lineHeight: 1.15, fontFamily: hF, color: "#1a1a1a", marginBottom: "3px" }}>{a.title}</h4>
                <p style={{ fontSize: "10.5px", lineHeight: 1.5, color: "#555", textAlign: "justify", flex: 1 }}>{a.summary}</p>
                <div style={{ clear: "both" }} />
              </div>
            ))}
          </div>
        )}

        {/* ROW 4: TAIL - dense multi-column */}
        {tail.length > 0 && (
          <div style={{ columnCount: Math.min(4, Math.max(2, tail.length)), columnGap: "14px", columnRule: "1px solid #ddd", flex: 1 }}>
            {tail.map((a) => (
              <div key={a.id} style={{ breakInside: "avoid", marginBottom: "8px", paddingBottom: "6px", borderBottom: "0.5px solid #e0e0e0" }}>
                <h5 style={{ fontSize: "13px", fontWeight: 700, lineHeight: 1.15, fontFamily: hF, color: "#1a1a1a", marginBottom: "2px" }}>{a.title}</h5>
                <p style={{ fontSize: "10px", lineHeight: 1.5, color: "#555", textAlign: "justify" }}>{a.summary}</p>
              </div>
            ))}
          </div>
        )}

        <CmykFooter pageNum={pageNum} totalPages={totalPages} date={date} fD={fD} />
      </div>
    </div>
  );
};
