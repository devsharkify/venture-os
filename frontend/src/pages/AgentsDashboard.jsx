import { useState, useEffect, useContext, useCallback } from "react";
import { API, AppContext } from "@/App";
import axios from "axios";
import {
  Loader2, Play, Clock, FileText, AlertTriangle, TrendingUp,
  Newspaper, Bot, ChevronRight, RefreshCw, Hash, Share2,
  Activity, Gauge, Zap, AlertCircle, Globe, Copy, Check
} from "lucide-react";

const T = {
  en: {
    title: "AI Agents", editor: "News Editor Agent", investigator: "Investigative Reporter",
    seo: "Social Media Expert", tech: "Tech Performance",
    run: "Run Agent", runAll: "Run All", running: "Analyzing...",
    editorial: "Today's Editorial", heroStories: "Hero Stories", duplicates: "Duplicates Found",
    mergedFrom: "Merged from", articles: "articles analyzed", lastRun: "Last run",
    topics: "Tracked Topics", events: "events tracked", report: "Latest Report",
    timeline: "Event Timeline", noReport: "No report yet. Run the agent first.",
    newEvents: "new events", matched: "articles matched", viewReport: "View Report",
    noData: "No data yet", runEditor: "Run Editor", runInvestigator: "Run Investigation",
    runSeo: "Run SEO", runTech: "Run Report",
    trendingKeywords: "Trending Keywords", contentGaps: "Content Gaps",
    socialPosts: "Social Media Posts", seoScore: "SEO Score",
    strategy: "Strategy Report", hashtags: "Hashtag Sets", postTimes: "Best Post Times",
    healthScore: "Health Score", avgResponse: "Avg Response", p95: "P95 Latency",
    errors: "Errors", requests: "Requests", slowEndpoints: "Slow Endpoints",
    anomalies: "Anomalies", topEndpoints: "Top Endpoints", copied: "Copied!",
    tweets: "Ready-to-Post Tweets", igCaptions: "Instagram Captions",
  },
};

// ─── Score Ring Component ────────────────────────────────────
function ScoreRing({ score, size = 64, color = "#ea580c", label }) {
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="currentColor" strokeWidth="4" className="text-slate-200 dark:text-slate-700" />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="4" strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round" className="transition-all duration-700" />
      </svg>
      <span className="absolute text-sm font-black" style={{ color, marginTop: size / 2 - 10 }}>{score}</span>
      {label && <span className="text-[10px] text-slate-500 mt-1">{label}</span>}
    </div>
  );
}

// ─── Copy Button ─────────────────────────────────────────────
function CopyBtn({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <button onClick={copy} className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
      {copied ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3 text-slate-400" />}
    </button>
  );
}


// ═══════════════════════════════════════════════════════════
// EDITOR SECTION
// ═══════════════════════════════════════════════════════════

function EditorSection({ lang }) {
  const t = T[lang] || T.en;
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  const fetchReport = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/agents/editor/latest`);
      if (r.data.report) setReport(r.data.report);
    } catch (e) { console.error(e); }
    finally { setFetching(false); }
  }, []);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  const runAgent = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/agents/editor/run`);
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        try {
          const r = await axios.get(`${API}/agents/editor/latest`);
          if (r.data.report && (!report || r.data.report.id !== report?.id)) {
            setReport(r.data.report);
            setLoading(false);
            clearInterval(poll);
          }
        } catch (e) { /* retry */ }
        if (attempts > 20) { setLoading(false); clearInterval(poll); }
      }, 5000);
    } catch (e) { console.error(e); setLoading(false); }
  };

  if (fetching) return <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-orange-500" /></div>;

  return (
    <div data-testid="editor-agent-section">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center">
            <Newspaper className="w-4 h-4 text-orange-500" />
          </div>
          <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">{t.editor}</h2>
        </div>
        <button data-testid="run-editor-btn" onClick={runAgent} disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-full bg-orange-500 text-white hover:bg-orange-600 disabled:opacity-50 transition-all">
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
          {loading ? t.running : t.runEditor}
        </button>
      </div>

      {!report ? (
        <p className="text-sm text-slate-400 text-center py-6">{t.noData}</p>
      ) : (
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-100 dark:border-slate-700">
              <p className="text-xl font-bold text-orange-500">{report.total_articles}</p>
              <p className="text-[10px] text-slate-500 uppercase tracking-wide">{t.articles}</p>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-100 dark:border-slate-700">
              <p className="text-xl font-bold text-blue-500">{report.hero_picks?.length || 0}</p>
              <p className="text-[10px] text-slate-500 uppercase tracking-wide">{t.heroStories}</p>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-100 dark:border-slate-700">
              <p className="text-xl font-bold text-red-500">{report.duplicate_groups?.length || 0}</p>
              <p className="text-[10px] text-slate-500 uppercase tracking-wide">{t.duplicates}</p>
            </div>
          </div>

          {report.editorial_en && (
            <div className="bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-lg p-4 border border-orange-100 dark:border-orange-800/30">
              <h3 className="text-xs font-bold text-orange-600 dark:text-orange-400 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> {t.editorial}
              </h3>
              <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                {report.editorial_en}
              </p>
            </div>
          )}

          {report.hero_articles?.length > 0 && (
            <div>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">{t.heroStories}</h3>
              <div className="space-y-1.5">
                {report.hero_articles.map((a, i) => (
                  <div key={i} className="flex items-start gap-2 bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-orange-500 text-white text-[10px] font-bold flex items-center justify-center">{i + 1}</span>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 line-clamp-2">{a.title}</p>
                      <p className="text-[10px] text-slate-400">{a.source}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <p className="text-[10px] text-slate-400 flex items-center gap-1">
            <Clock className="w-3 h-3" /> {t.lastRun}: {new Date(report.created_at).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// INVESTIGATOR SECTION
// ═══════════════════════════════════════════════════════════

function TopicCard({ topic, lang, onViewReport }) {
  const t = T[lang] || T.en;
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const runInvestigation = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/agents/investigator/run/${topic.id}`);
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        try {
          const r = await axios.get(`${API}/agents/investigator/report/${topic.id}`);
          if (r.data.report) {
            setResult({ matched: r.data.report.matched_articles || 0, new_events: r.data.report.new_events || 0 });
            setLoading(false);
            clearInterval(poll);
          }
        } catch (e) { /* retry */ }
        if (attempts > 20) { setLoading(false); clearInterval(poll); }
      }, 5000);
    } catch (e) { console.error(e); setLoading(false); }
  };

  return (
    <div data-testid={`topic-${topic.id}`} className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-100 dark:border-slate-700 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">
            {topic.name_en}
          </h3>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-[10px] text-slate-400 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" /> {topic.event_count || 0} {t.events}
            </span>
            {topic.last_analyzed && (
              <span className="text-[10px] text-slate-400 flex items-center gap-1">
                <Clock className="w-3 h-3" /> {new Date(topic.last_analyzed).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        <span className={`w-2 h-2 rounded-full ${topic.active ? "bg-green-500" : "bg-slate-300"}`} />
      </div>
      <div className="flex gap-2">
        <button data-testid={`run-topic-${topic.id}`} onClick={runInvestigation} disabled={loading}
          className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 disabled:opacity-50 transition-all">
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
          {loading ? t.running : t.runInvestigator}
        </button>
        <button data-testid={`view-report-${topic.id}`} onClick={() => onViewReport(topic.id)}
          className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 transition-all">
          <FileText className="w-3 h-3" /> {t.viewReport}
        </button>
      </div>
      {result && (
        <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-100 dark:border-green-800/30">
          <p className="text-xs text-green-700 dark:text-green-400 font-medium">
            {result.matched} {t.matched} / {result.new_events} {t.newEvents}
          </p>
        </div>
      )}
    </div>
  );
}

function ReportView({ topicId, lang, onBack }) {
  const t = T[lang] || T.en;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const r = await axios.get(`${API}/agents/investigator/report/${topicId}`);
        setData(r.data);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    };
    fetchData();
  }, [topicId]);

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-indigo-500" /></div>;
  if (!data || !data.report) return <p className="text-sm text-slate-400 text-center py-8">{t.noReport}</p>;

  const report = data.report;
  const events = data.events || [];
  const topic = data.topic || {};

  return (
    <div data-testid="investigation-report-view">
      <button onClick={onBack} className="text-xs text-indigo-500 font-medium mb-3 flex items-center gap-1 hover:text-indigo-600">
        &larr; Back to topics
      </button>
      <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 mb-1">
        {topic.name_en}
      </h2>
      <p className="text-[10px] text-slate-400 mb-4">{events.length} {t.events} / {t.lastRun}: {new Date(report.created_at).toLocaleString()}</p>

      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl p-4 border border-indigo-100 dark:border-indigo-800/30 mb-4">
        <h3 className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wide mb-2 flex items-center gap-1.5">
          <Bot className="w-3.5 h-3.5" /> {t.report}
        </h3>
        <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
          {report.report_en}
        </p>
      </div>

      <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3 flex items-center gap-1.5">
        <Clock className="w-3.5 h-3.5" /> {t.timeline}
      </h3>
      <div className="relative pl-4 border-l-2 border-indigo-200 dark:border-indigo-800 space-y-3">
        {events.map((e, i) => (
          <div key={e.id || i} className="relative">
            <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-indigo-400 border-2 border-white dark:border-slate-900" />
            <div className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-100 dark:border-slate-700 shadow-sm">
              <div className="flex items-start gap-2">
                {e.image && <img src={e.image} alt="" className="w-12 h-12 rounded-md object-cover flex-shrink-0" />}
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 line-clamp-2">{e.title}</p>
                  <p className="text-[10px] text-slate-500 mt-0.5 line-clamp-2">{e.summary}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[9px] text-indigo-500 font-medium">{e.source}</span>
                    {e.published_at && <span className="text-[9px] text-slate-400">{new Date(e.published_at).toLocaleDateString()}</span>}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function InvestigatorSection({ lang }) {
  const t = T[lang] || T.en;
  const [topics, setTopics] = useState([]);
  const [fetching, setFetching] = useState(true);
  const [activeReport, setActiveReport] = useState(null);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const r = await axios.get(`${API}/agents/investigator/topics`);
        setTopics(r.data.topics || []);
      } catch (e) { console.error(e); }
      finally { setFetching(false); }
    };
    fetchTopics();
  }, []);

  if (fetching) return <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-indigo-500" /></div>;

  if (activeReport) {
    return <ReportView topicId={activeReport} lang={lang} onBack={() => setActiveReport(null)} />;
  }

  return (
    <div data-testid="investigator-agent-section">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center">
            <TrendingUp className="w-4 h-4 text-indigo-500" />
          </div>
          <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">{t.investigator}</h2>
        </div>
      </div>
      <div className="space-y-3">
        {topics.map(topic => (
          <TopicCard key={topic.id} topic={topic} lang={lang} onViewReport={setActiveReport} />
        ))}
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// SEO / SOCIAL MEDIA EXPERT SECTION
// ═══════════════════════════════════════════════════════════

function SeoSection({ lang }) {
  const t = T[lang] || T.en;
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [tab, setTab] = useState("overview");
  const [seoStats, setSeoStats] = useState(null);

  const fetchReport = useCallback(async () => {
    try {
      const [reportRes, statsRes] = await Promise.all([
        axios.get(`${API}/agents/seo/latest`),
        axios.get(`${API}/seo-engine/stats`).catch(() => ({ data: null }))
      ]);
      if (reportRes.data.report) setReport(reportRes.data.report);
      if (statsRes.data) setSeoStats(statsRes.data);
    } catch (e) { console.error(e); }
    finally { setFetching(false); }
  }, []);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  const runAgent = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/agents/seo/run`);
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        try {
          const r = await axios.get(`${API}/agents/seo/latest`);
          if (r.data.report && (!report || r.data.report.id !== report?.id)) {
            setReport(r.data.report);
            setLoading(false);
            clearInterval(poll);
          }
        } catch (e) { /* retry */ }
        if (attempts > 24) { setLoading(false); clearInterval(poll); }
      }, 5000);
    } catch (e) { console.error(e); setLoading(false); }
  };

  if (fetching) return <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-emerald-500" /></div>;

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "social", label: t.socialPosts },
    { id: "strategy", label: t.strategy },
    { id: "infra", label: "SEO Infra" },
  ];

  return (
    <div data-testid="seo-agent-section">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
            <Globe className="w-4 h-4 text-emerald-500" />
          </div>
          <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">{t.seo}</h2>
        </div>
        <button data-testid="run-seo-btn" onClick={runAgent} disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-full bg-emerald-500 text-white hover:bg-emerald-600 disabled:opacity-50 transition-all">
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
          {loading ? t.running : t.runSeo}
        </button>
      </div>

      {!report ? (
        <p className="text-sm text-slate-400 text-center py-6">{t.noData}</p>
      ) : (
        <div className="space-y-3">
          {/* Score + Stats Row */}
          <div className="flex items-center gap-4">
            <div className="relative flex items-center justify-center">
              <ScoreRing score={report.seo_score || 0} color="#10b981" label={t.seoScore} />
            </div>
            <div className="flex-1 grid grid-cols-2 gap-2">
              <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                <p className="text-lg font-bold text-emerald-500">{report.trending_keywords?.length || 0}</p>
                <p className="text-[10px] text-slate-500">{t.trendingKeywords}</p>
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                <p className="text-lg font-bold text-amber-500">{report.content_gaps?.length || 0}</p>
                <p className="text-[10px] text-slate-500">{t.contentGaps}</p>
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                <p className="text-lg font-bold text-blue-500">{report.tweets?.length || 0}</p>
                <p className="text-[10px] text-slate-500">{t.tweets}</p>
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                <p className="text-lg font-bold text-purple-500">{report.total_articles_analyzed || 0}</p>
                <p className="text-[10px] text-slate-500">{t.articles}</p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-0.5">
            {tabs.map(tb => (
              <button key={tb.id} onClick={() => setTab(tb.id)}
                className={`flex-1 text-[11px] font-semibold py-1.5 rounded-md transition-all ${
                  tab === tb.id ? "bg-white dark:bg-slate-700 text-slate-800 dark:text-white shadow-sm" : "text-slate-500 hover:text-slate-700"
                }`}>{tb.label}</button>
            ))}
          </div>

          {/* Tab Content */}
          {tab === "overview" && (
            <div className="space-y-3">
              {/* Trending Keywords */}
              {report.trending_keywords?.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <Hash className="w-3.5 h-3.5 text-emerald-500" /> {t.trendingKeywords}
                  </h3>
                  <div className="flex flex-wrap gap-1.5">
                    {report.trending_keywords.map((kw, i) => (
                      <span key={i} className="px-2 py-1 text-[11px] font-medium rounded-full bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-800/30">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Content Gaps */}
              {report.content_gaps?.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500" /> {t.contentGaps}
                  </h3>
                  <div className="space-y-1.5">
                    {report.content_gaps.map((gap, i) => (
                      <div key={i} className="flex items-start gap-2 bg-amber-50 dark:bg-amber-900/20 rounded-lg p-2.5 border border-amber-100 dark:border-amber-800/30">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-slate-700 dark:text-slate-300">{gap}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* SEO Meta Suggestions */}
              {report.meta_suggestions?.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">SEO Optimization</h3>
                  <div className="space-y-2">
                    {report.meta_suggestions.map((m, i) => (
                      <div key={i} className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-100 dark:border-slate-700">
                        <p className="text-[10px] text-slate-400 line-through">{m.original_title}</p>
                        <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 mt-1">{m.optimized_title}</p>
                        <p className="text-[10px] text-slate-500 mt-1">{m.meta_description}</p>
                        <span className="inline-block mt-1 px-1.5 py-0.5 text-[9px] font-medium bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 rounded">{m.focus_keyword}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {tab === "social" && (
            <div className="space-y-3">
              {/* Tweets */}
              {report.tweets?.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <Share2 className="w-3.5 h-3.5 text-blue-500" /> {t.tweets}
                  </h3>
                  <div className="space-y-2">
                    {report.tweets.map((tweet, i) => (
                      <div key={i} className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-100 dark:border-slate-700">
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed flex-1">{tweet}</p>
                          <CopyBtn text={tweet} />
                        </div>
                        <p className="text-[10px] text-slate-400 mt-1">{tweet.length}/280 chars</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Instagram Captions */}
              {report.instagram_captions?.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <Share2 className="w-3.5 h-3.5 text-pink-500" /> {t.igCaptions}
                  </h3>
                  <div className="space-y-2">
                    {report.instagram_captions.map((caption, i) => (
                      <div key={i} className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-100 dark:border-slate-700">
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed flex-1">{caption}</p>
                          <CopyBtn text={caption} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Hashtag Sets */}
              {report.hashtag_sets?.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <Hash className="w-3.5 h-3.5 text-purple-500" /> {t.hashtags}
                  </h3>
                  {report.hashtag_sets.map((set, i) => (
                    <div key={i} className="mb-2 bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-100 dark:border-slate-700">
                      <div className="flex items-start justify-between">
                        <div className="flex flex-wrap gap-1">
                          {(Array.isArray(set) ? set : [set]).map((tag, ti) => (
                            <span key={ti} className="text-[11px] text-purple-600 dark:text-purple-400 font-medium">{tag}</span>
                          ))}
                        </div>
                        <CopyBtn text={Array.isArray(set) ? set.join(" ") : set} />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Best Posting Times */}
              {report.best_posting_times?.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-teal-500" /> {t.postTimes}
                  </h3>
                  <div className="space-y-1.5">
                    {report.best_posting_times.map((time, i) => (
                      <div key={i} className="flex items-center gap-2 bg-teal-50 dark:bg-teal-900/20 rounded-lg p-2.5 border border-teal-100 dark:border-teal-800/30">
                        <Clock className="w-3.5 h-3.5 text-teal-500 flex-shrink-0" />
                        <p className="text-xs text-slate-700 dark:text-slate-300">{time}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {tab === "strategy" && report.strategy_report && (
            <div className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 rounded-lg p-4 border border-emerald-100 dark:border-emerald-800/30">
              <h3 className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> {t.strategy}
              </h3>
              <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                {report.strategy_report}
              </p>
            </div>
          )}

          {tab === "infra" && (
            <div className="space-y-3">
              {/* SEO Health Score */}
              {seoStats && (
                <div className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-100 dark:border-slate-700">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">SEO Health Score</h3>
                    <div className="relative flex items-center justify-center">
                      <ScoreRing score={seoStats.health_score || 0} size={52} color={seoStats.health_score >= 70 ? "#10b981" : seoStats.health_score >= 40 ? "#eab308" : "#ef4444"} />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <div className="text-center p-2 rounded-lg bg-slate-50 dark:bg-slate-700/50">
                      <p className="text-lg font-bold text-emerald-500">{seoStats.recent_24h || 0}</p>
                      <p className="text-[9px] text-slate-500 uppercase">New Today</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-slate-50 dark:bg-slate-700/50">
                      <p className="text-lg font-bold text-blue-500">{seoStats.recent_with_seo || 0}</p>
                      <p className="text-[9px] text-slate-500 uppercase">With SEO</p>
                    </div>
                  </div>
                </div>
              )}

              {/* SEO Coverage Breakdown */}
              {seoStats && (
                <div className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-100 dark:border-slate-700">
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">Coverage Breakdown</h3>
                  {[
                    { label: "SEO Meta (Title + Desc)", value: seoStats.seo_coverage_percent, count: seoStats.with_seo_meta, color: "#10b981" },
                    { label: "Images", value: Math.min(100, seoStats.image_coverage_percent), count: seoStats.with_images, color: "#3b82f6" },
                    { label: "Source Links", value: seoStats.link_coverage_percent, count: seoStats.with_links, color: "#f59e0b" },
                  ].map((item, i) => (
                    <div key={i} className="mb-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[11px] font-medium text-slate-600 dark:text-slate-400">{item.label}</span>
                        <span className="text-[11px] font-bold" style={{ color: item.color }}>{item.value}% ({item.count})</span>
                      </div>
                      <div className="h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${item.value}%`, backgroundColor: item.color }} />
                      </div>
                    </div>
                  ))}
                  <div className="flex justify-between text-[10px] text-slate-400 mt-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                    <span>Total: {seoStats.total_articles} articles</span>
                    <span>{seoStats.without_seo_meta} need SEO meta</span>
                  </div>
                </div>
              )}

              {/* SEO Infrastructure Status */}
              <div className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-100 dark:border-slate-700">
                <h3 className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide mb-3">Active SEO Infrastructure</h3>
                <div className="space-y-2">
                  {[
                    { label: "Sitemap.xml", desc: `${seoStats?.total_articles || 0} articles + Google News tags`, url: "/sitemap.xml", status: true },
                    { label: "RSS Feed", desc: "Google News compatible with keywords", url: "/rss.xml", status: true },
                    { label: "robots.txt", desc: "Googlebot-News + crawl-delay rules", url: "/robots.txt", status: true },
                    { label: "IndexNow", desc: "Auto-ping Bing & Yandex on new articles", status: true },
                    { label: "JSON-LD Schema", desc: "NewsArticle + BreadcrumbList + WebSite", status: true },
                    { label: "Open Graph", desc: "Full article:section, article:tag, og:image", status: true },
                    { label: "Twitter Cards", desc: "summary_large_image with category labels", status: true },
                    { label: "Related Articles", desc: "Internal linking via category + keyword match", status: true },
                    { label: "Canonical URLs", desc: "Proper canonical on every article page", status: true },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-b border-slate-50 dark:border-slate-700 last:border-0">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-green-500" />
                        <div>
                          <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">{item.label}</p>
                          <p className="text-[10px] text-slate-400">{item.desc}</p>
                        </div>
                      </div>
                      {item.url && (
                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-[10px] text-emerald-500 font-medium hover:underline">
                          View
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* How it works */}
              <div className="bg-emerald-50 dark:bg-emerald-900/20 rounded-lg p-4 border border-emerald-100 dark:border-emerald-800/30">
                <h3 className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide mb-2">How Auto-SEO Works</h3>
                <div className="space-y-1.5 text-xs text-slate-600 dark:text-slate-400">
                  <p>1. Every new article gets AI-generated SEO title, meta description & keywords</p>
                  <p>2. Google News sitemap with publication tags auto-updates every 30 minutes</p>
                  <p>3. New URLs instantly submitted to Bing/Yandex via IndexNow</p>
                  <p>4. Server-rendered pages with NewsArticle + BreadcrumbList JSON-LD</p>
                  <p>5. Hreflang tags for bilingual content (English + Telugu)</p>
                  <p>6. Related articles engine for internal link building</p>
                  <p>7. Rich social previews via Open Graph & Twitter Cards</p>
                </div>
              </div>
            </div>
          )}

          <p className="text-[10px] text-slate-400 flex items-center gap-1">
            <Clock className="w-3 h-3" /> {t.lastRun}: {new Date(report.created_at).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// TECH PERFORMANCE SECTION
// ═══════════════════════════════════════════════════════════

function TechSection({ lang }) {
  const t = T[lang] || T.en;
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  const fetchReport = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/agents/tech/latest`);
      if (r.data.report) setReport(r.data.report);
    } catch (e) { console.error(e); }
    finally { setFetching(false); }
  }, []);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  const runAgent = async () => {
    setLoading(true);
    try {
      const r = await axios.post(`${API}/agents/tech/run`);
      if (r.data.report) setReport(r.data.report);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  if (fetching) return <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-cyan-500" /></div>;

  const lh = report?.last_hour || {};
  const healthColor = (report?.health_score || 0) >= 80 ? "#06b6d4" : ((report?.health_score || 0) >= 50 ? "#eab308" : "#ef4444");

  return (
    <div data-testid="tech-agent-section">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center">
            <Activity className="w-4 h-4 text-cyan-500" />
          </div>
          <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">{t.tech}</h2>
        </div>
        <button data-testid="run-tech-btn" onClick={runAgent} disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-full bg-cyan-500 text-white hover:bg-cyan-600 disabled:opacity-50 transition-all">
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3" />}
          {loading ? t.running : t.runTech}
        </button>
      </div>

      {!report ? (
        <p className="text-sm text-slate-400 text-center py-6">{t.noData}</p>
      ) : (
        <div className="space-y-3">
          {/* Health + Key Metrics */}
          <div className="flex items-center gap-4">
            <div className="relative flex items-center justify-center">
              <ScoreRing score={report.health_score || 0} color={healthColor} label={t.healthScore} />
            </div>
            <div className="flex-1 grid grid-cols-2 gap-2">
              <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                <p className="text-lg font-bold text-cyan-500">{lh.avg_response_ms || 0}<span className="text-[10px] font-normal text-slate-400">ms</span></p>
                <p className="text-[10px] text-slate-500">{t.avgResponse}</p>
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                <p className="text-lg font-bold text-amber-500">{lh.p95_response_ms || 0}<span className="text-[10px] font-normal text-slate-400">ms</span></p>
                <p className="text-[10px] text-slate-500">{t.p95}</p>
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                <p className="text-lg font-bold text-blue-500">{lh.total_requests || 0}</p>
                <p className="text-[10px] text-slate-500">{t.requests}</p>
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                <p className="text-lg font-bold text-red-500">{lh.error_count || 0}</p>
                <p className="text-[10px] text-slate-500">{t.errors}</p>
              </div>
            </div>
          </div>

          {/* Top Endpoints */}
          {report.top_endpoints?.length > 0 && (
            <div>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <Gauge className="w-3.5 h-3.5 text-cyan-500" /> {t.topEndpoints}
              </h3>
              <div className="space-y-1.5">
                {report.top_endpoints.map((ep, i) => {
                  const barWidth = Math.min(100, (ep.avg_ms / (report.top_endpoints[0]?.avg_ms || 1)) * 100);
                  const barColor = ep.avg_ms > 500 ? "bg-red-500" : ep.avg_ms > 200 ? "bg-amber-500" : "bg-emerald-500";
                  return (
                    <div key={i} className="bg-white dark:bg-slate-800 rounded-lg p-2.5 border border-slate-100 dark:border-slate-700">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-[11px] font-mono text-slate-700 dark:text-slate-300 truncate flex-1">{ep.endpoint}</p>
                        <span className="text-[11px] font-bold text-slate-600 dark:text-slate-400 ml-2">{ep.avg_ms}ms</span>
                      </div>
                      <div className="h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                        <div className={`h-full ${barColor} rounded-full transition-all duration-500`} style={{ width: `${barWidth}%` }} />
                      </div>
                      <div className="flex gap-3 mt-1">
                        <span className="text-[9px] text-slate-400">{ep.requests} reqs</span>
                        <span className="text-[9px] text-slate-400">max {ep.max_ms}ms</span>
                        {ep.errors > 0 && <span className="text-[9px] text-red-400">{ep.errors} errors</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Slow Endpoints */}
          {report.slow_endpoints?.length > 0 && (
            <div>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-red-500" /> {t.slowEndpoints}
              </h3>
              <div className="space-y-1.5">
                {report.slow_endpoints.map((ep, i) => (
                  <div key={i} className="flex items-center justify-between bg-red-50 dark:bg-red-900/20 rounded-lg p-2.5 border border-red-100 dark:border-red-800/30">
                    <p className="text-xs font-mono text-red-700 dark:text-red-400 truncate flex-1">{ep.endpoint}</p>
                    <span className="text-xs font-bold text-red-600 dark:text-red-400 ml-2">{ep.avg_ms}ms</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Anomalies */}
          {report.anomalies?.length > 0 && (
            <div>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <AlertCircle className="w-3.5 h-3.5 text-amber-500" /> {t.anomalies}
              </h3>
              <div className="space-y-1.5">
                {report.anomalies.map((a, i) => (
                  <div key={i} className="flex items-center justify-between bg-amber-50 dark:bg-amber-900/20 rounded-lg p-2.5 border border-amber-100 dark:border-amber-800/30">
                    <p className="text-xs font-mono text-amber-700 dark:text-amber-400 truncate flex-1">{a.endpoint}</p>
                    <span className="text-xs font-bold text-amber-600">{a.error_rate}% errors</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <p className="text-[10px] text-slate-400 flex items-center gap-1">
            <Clock className="w-3 h-3" /> {t.lastRun}: {new Date(report.created_at).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// MAIN DASHBOARD
// ═══════════════════════════════════════════════════════════

export default function AgentsDashboard() {
  const t = T.en;
  const [activeTab, setActiveTab] = useState("editor");

  const agentTabs = [
    { id: "editor", label: t.editor, icon: Newspaper, color: "orange" },
    { id: "investigator", label: t.investigator, icon: TrendingUp, color: "indigo" },
    { id: "seo", label: t.seo, icon: Globe, color: "emerald" },
    { id: "tech", label: t.tech, icon: Activity, color: "cyan" },
  ];

  return (
    <div data-testid="agents-dashboard" className="max-w-lg mx-auto px-4 pt-2 pb-24">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Bot className="w-5 h-5 text-orange-500" />
        <h1 className="text-lg font-bold text-slate-800 dark:text-slate-100">{t.title}</h1>
      </div>

      {/* Agent Tab Selector */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-1 no-scrollbar">
        {agentTabs.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button key={tab.id} data-testid={`agent-tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg whitespace-nowrap transition-all ${
                isActive
                  ? `bg-${tab.color}-500 text-white shadow-sm`
                  : `bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700`
              }`}
              style={isActive ? { backgroundColor: tab.color === "orange" ? "#f97316" : tab.color === "indigo" ? "#6366f1" : tab.color === "emerald" ? "#10b981" : "#06b6d4" } : {}}
            >
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Active Agent Section */}
      <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4">
        {activeTab === "editor" && <EditorSection lang="en" />}
        {activeTab === "investigator" && <InvestigatorSection lang="en" />}
        {activeTab === "seo" && <SeoSection lang="en" />}
        {activeTab === "tech" && <TechSection lang="en" />}
      </div>
    </div>
  );
}
