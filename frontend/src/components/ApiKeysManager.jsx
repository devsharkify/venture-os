import { useState, useEffect, useCallback } from "react";
import { API } from "@/App";
import axios from "axios";
import { Key, Plus, Copy, Check, Trash2, ToggleLeft, ToggleRight, ExternalLink, BarChart3 } from "lucide-react";

export default function ApiKeysManager({ darkMode }) {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyLimit, setNewKeyLimit] = useState(1000);
  const [createdKey, setCreatedKey] = useState(null);
  const [copied, setCopied] = useState("");

  const fetchKeys = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/apikeys/list`);
      setKeys(r.data.keys || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchKeys(); }, [fetchKeys]);

  const createKey = async () => {
    if (!newKeyName.trim()) return;
    setCreating(true);
    try {
      const r = await axios.post(`${API}/apikeys/create?name=${encodeURIComponent(newKeyName)}&daily_limit=${newKeyLimit}`);
      setCreatedKey(r.data.api_key);
      setNewKeyName("");
      fetchKeys();
    } catch (e) { console.error(e); }
    finally { setCreating(false); }
  };

  const toggleKey = async (id) => {
    try {
      await axios.put(`${API}/apikeys/${id}/toggle`);
      fetchKeys();
    } catch (e) { console.error(e); }
  };

  const deleteKey = async (id) => {
    if (!window.confirm("Delete this API key permanently?")) return;
    try {
      await axios.delete(`${API}/apikeys/${id}`);
      fetchKeys();
    } catch (e) { console.error(e); }
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(""), 2000);
  };

  const bg = darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200";
  const txt = darkMode ? "text-slate-200" : "text-slate-800";
  const sub = darkMode ? "text-slate-400" : "text-slate-500";

  const baseUrl = window.location.origin;
  const exampleCode = `// Fetch latest news from Venture OS API
fetch("${baseUrl}/api/public/v1/feed?lang=en&limit=10", {
  headers: { "X-API-Key": "YOUR_API_KEY" }
})
.then(r => r.json())
.then(data => {
  data.articles.forEach(a => {
    console.log(a.title, a.image);
  });
});`;

  return (
    <div data-testid="api-keys-manager" className="space-y-4">
      {/* Create New Key */}
      <div className={`rounded-xl border p-5 ${bg}`}>
        <h3 className={`text-sm font-bold mb-3 flex items-center gap-2 ${txt}`}>
          <Key className="w-4 h-4 text-orange-500" /> Create API Key
        </h3>
        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <label className={`text-[11px] font-medium ${sub}`}>Partner Name</label>
            <input
              data-testid="api-key-name-input"
              value={newKeyName}
              onChange={e => setNewKeyName(e.target.value)}
              placeholder="e.g., MyNewsApp, PartnerSite"
              className={`w-full mt-1 px-3 py-2 rounded-lg border text-sm ${darkMode ? "bg-slate-700 border-slate-600 text-white" : "bg-white border-slate-300"}`}
            />
          </div>
          <div className="w-32">
            <label className={`text-[11px] font-medium ${sub}`}>Daily Limit</label>
            <input
              data-testid="api-key-limit-input"
              type="number"
              value={newKeyLimit}
              onChange={e => setNewKeyLimit(Number(e.target.value))}
              className={`w-full mt-1 px-3 py-2 rounded-lg border text-sm ${darkMode ? "bg-slate-700 border-slate-600 text-white" : "bg-white border-slate-300"}`}
            />
          </div>
          <button
            data-testid="create-api-key-btn"
            onClick={createKey}
            disabled={creating || !newKeyName.trim()}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm font-semibold hover:bg-orange-600 disabled:opacity-50 flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" /> Create
          </button>
        </div>

        {/* Show created key */}
        {createdKey && (
          <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <p className="text-xs font-bold text-green-700 dark:text-green-400 mb-1">API Key Created. Save it now!</p>
            <div className="flex items-center gap-2">
              <code data-testid="created-key-value" className="flex-1 text-xs font-mono bg-green-100 dark:bg-green-900/40 px-2 py-1.5 rounded break-all text-green-800 dark:text-green-300">
                {createdKey}
              </code>
              <button onClick={() => copyToClipboard(createdKey, "key")}
                className="p-1.5 rounded hover:bg-green-200 dark:hover:bg-green-800 transition-colors">
                {copied === "key" ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4 text-green-600" />}
              </button>
            </div>
            <p className="text-[10px] text-green-600 dark:text-green-500 mt-1">This key won't be shown again.</p>
          </div>
        )}
      </div>

      {/* API Keys List */}
      <div className={`rounded-xl border ${bg}`}>
        <div className="p-4 border-b border-slate-100 dark:border-slate-700">
          <h3 className={`text-sm font-bold flex items-center gap-2 ${txt}`}>
            <BarChart3 className="w-4 h-4 text-blue-500" /> Active API Keys ({keys.length})
          </h3>
        </div>
        <div className="divide-y divide-slate-100 dark:divide-slate-700">
          {loading ? (
            <p className={`p-4 text-sm ${sub}`}>Loading...</p>
          ) : keys.length === 0 ? (
            <p className={`p-4 text-sm ${sub}`}>No API keys yet. Create one above.</p>
          ) : (
            keys.map(k => (
              <div key={k.id} data-testid={`api-key-${k.id}`} className="p-4 flex items-center gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className={`text-sm font-semibold ${txt}`}>{k.name}</p>
                    <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded ${k.active ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"}`}>
                      {k.active ? "Active" : "Revoked"}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1">
                    <span className={`text-[11px] ${sub}`}>Key: <code className="font-mono">{k.key_prefix}</code></span>
                    <span className={`text-[11px] ${sub}`}>Today: {k.requests_today || 0}/{k.daily_limit || 1000}</span>
                    <span className={`text-[11px] ${sub}`}>Total: {k.total_requests || 0}</span>
                    {k.last_used && <span className={`text-[11px] ${sub}`}>Last: {new Date(k.last_used).toLocaleDateString()}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  <button data-testid={`toggle-key-${k.id}`} onClick={() => toggleKey(k.id)}
                    className={`p-1.5 rounded-lg transition-colors ${k.active ? "hover:bg-amber-50 text-amber-500" : "hover:bg-green-50 text-green-500"}`}
                    title={k.active ? "Revoke" : "Activate"}>
                    {k.active ? <ToggleRight className="w-5 h-5" /> : <ToggleLeft className="w-5 h-5" />}
                  </button>
                  <button data-testid={`delete-key-${k.id}`} onClick={() => deleteKey(k.id)}
                    className="p-1.5 rounded-lg hover:bg-red-50 text-red-400 transition-colors" title="Delete">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Integration Guide */}
      <div className={`rounded-xl border p-5 ${bg}`}>
        <h3 className={`text-sm font-bold mb-3 flex items-center gap-2 ${txt}`}>
          <ExternalLink className="w-4 h-4 text-indigo-500" /> Integration Guide
        </h3>
        <div className="space-y-3">
          <div>
            <h4 className={`text-xs font-semibold mb-1 ${txt}`}>Endpoints</h4>
            <div className="space-y-1">
              {[
                { method: "GET", path: "/api/public/v1/feed", desc: "Latest articles feed" },
                { method: "GET", path: "/api/public/v1/articles/{id}", desc: "Single article" },
                { method: "GET", path: "/api/public/v1/categories", desc: "All categories" },
                { method: "GET", path: "/api/public/v1/search?q=keyword", desc: "Search articles" },
              ].map((ep, i) => (
                <div key={i} className="flex items-center gap-2 text-[11px]">
                  <span className="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded font-mono font-bold">{ep.method}</span>
                  <code className={`font-mono ${sub}`}>{ep.path}</code>
                  <span className={`text-[10px] ${sub}`}>· {ep.desc}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <h4 className={`text-xs font-semibold ${txt}`}>Example Code</h4>
              <button onClick={() => copyToClipboard(exampleCode, "code")}
                className={`text-[10px] flex items-center gap-1 px-2 py-1 rounded ${sub} hover:bg-slate-100 dark:hover:bg-slate-700`}>
                {copied === "code" ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />} Copy
              </button>
            </div>
            <pre className={`p-3 rounded-lg text-[11px] font-mono leading-relaxed overflow-x-auto ${darkMode ? "bg-slate-900 text-slate-300" : "bg-slate-50 text-slate-700"}`}>
              {exampleCode}
            </pre>
          </div>

          <div>
            <h4 className={`text-xs font-semibold mb-1 ${txt}`}>Query Parameters</h4>
            <div className={`text-[11px] space-y-0.5 ${sub}`}>
              <p><code className="font-mono">lang</code> · <code>en</code> or <code>te</code> (default: en)</p>
              <p><code className="font-mono">category</code> · Filter by category ID</p>
              <p><code className="font-mono">page</code> · Page number (default: 1)</p>
              <p><code className="font-mono">limit</code> · Articles per page (max: 50)</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
