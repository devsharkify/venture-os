export const PageThumbnail = ({ page }) => {
  const a = page.articles;
  return (
    <div style={{ padding: "2px", fontSize: "3px", lineHeight: 1.2, minHeight: "120px", overflow: "hidden", background: "#fefcf7" }}>
      <div style={{ textAlign: "center", fontSize: "5px", fontWeight: 900, color: "#c41e1e", borderBottom: "0.5px solid #aaa", paddingBottom: "1px", marginBottom: "1px" }}>KAIZER NEWS</div>
      {a[0] && (
        <div style={{ marginBottom: "1px" }}>
          {a[0].image && <div style={{ width: "100%", height: "14px", overflow: "hidden", background: "#ddd" }}><img src={a[0].image} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} onError={e => e.target.style.display = "none"} /></div>}
          <div style={{ fontSize: "3.5px", fontWeight: 900, lineHeight: 1.1, marginTop: "1px" }}>{a[0]?.title?.slice(0, 40)}</div>
        </div>
      )}
      <div style={{ columnCount: 3, columnGap: "1px", fontSize: "2px", color: "#666" }}>
        {a.slice(1, 12).map((x, i) => <div key={i} style={{ breakInside: "avoid", marginBottom: "0.5px" }}><span style={{ fontWeight: 700, fontSize: "2px" }}>{x.title?.slice(0, 20)}</span></div>)}
      </div>
    </div>
  );
};
