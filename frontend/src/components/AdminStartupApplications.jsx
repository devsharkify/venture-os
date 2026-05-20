import { useState, useEffect, useContext, useCallback } from "react";
import axios from "axios";
import { API, AppContext } from "../App";
import { toast } from "sonner";
import {
  Rocket, Loader2, Download, RefreshCw, FileText, Video, MapPin,
  CheckCircle, XCircle, Clock, Eye, Award, Phone, Mail, User, Calendar,
} from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "./ui/table";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "./ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "./ui/select";
import { formatDistanceToNow } from "date-fns";

const STATUSES = ["submitted", "shortlisted", "interviewed", "selected", "rejected"];

export const AdminStartupApplications = () => {
  const { darkMode } = useContext(AppContext);
  const adminPhone = localStorage.getItem("userPhone") || "";
  const authHeaders = { headers: { "X-Admin-Phone": adminPhone } };

  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [selectedApp, setSelectedApp] = useState(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchApplications = useCallback(async () => {
    try {
      setLoading(true);
      setFetchError(null);
      const url = statusFilter === "all"
        ? `${API}/admin/startup-applications`
        : `${API}/admin/startup-applications?status=${statusFilter}`;
      const { data } = await axios.get(url, { headers: { "X-Admin-Phone": adminPhone } });
      setApplications(data);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || "Failed to load applications";
      setFetchError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, adminPhone]);

  useEffect(() => { fetchApplications(); }, [fetchApplications]);

  const updateStatus = async (id, newStatus, reason = "") => {
    try {
      const params = new URLSearchParams({ status: newStatus });
      if (reason) params.set("reason", reason);
      await axios.post(`${API}/admin/startup-applications/${id}/update-status?${params.toString()}`, null, authHeaders);
      toast.success(`Marked as ${newStatus}`);
      fetchApplications();
      if (selectedApp?.id === id) setSelectedApp((prev) => prev && { ...prev, status: newStatus });
    } catch (err) {
      toast.error(err.response?.data?.detail || "Update failed");
    }
  };

  const downloadCSV = () => {
    // window.open cannot set headers, so pass admin_phone via query string (also accepted by backend).
    const base = `${API}/admin/startup-applications/export`;
    const params = new URLSearchParams({ admin_phone: adminPhone });
    if (statusFilter !== "all") params.set("status", statusFilter);
    window.open(`${base}?${params.toString()}`, "_blank");
    toast.success("Downloading CSV...");
  };

  const filtered = applications.filter((a) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      a.name?.toLowerCase().includes(q) ||
      a.mobile?.includes(q) ||
      a.email?.toLowerCase().includes(q) ||
      a.idea?.toLowerCase().includes(q) ||
      a.colony?.toLowerCase().includes(q) ||
      a.area?.toLowerCase().includes(q) ||
      a.city?.toLowerCase().includes(q)
    );
  });

  const counts = STATUSES.reduce((acc, s) => {
    acc[s] = applications.filter((a) => a.status === s).length;
    return acc;
  }, {});

  const getStatusBadge = (status) => {
    const map = {
      submitted: { cls: "bg-blue-100 text-blue-800", icon: Clock, label: "Submitted" },
      shortlisted: { cls: "bg-purple-100 text-purple-800", icon: Award, label: "Shortlisted" },
      interviewed: { cls: "bg-amber-100 text-amber-800", icon: User, label: "Interviewed" },
      selected: { cls: "bg-green-100 text-green-800", icon: CheckCircle, label: "Selected" },
      rejected: { cls: "bg-red-100 text-red-800", icon: XCircle, label: "Rejected" },
    };
    const cfg = map[status] || map.submitted;
    const Icon = cfg.icon;
    return (
      <Badge className={`${cfg.cls} hover:${cfg.cls} font-medium`}>
        <Icon size={11} className="mr-1" />{cfg.label}
      </Badge>
    );
  };

  const fmtTime = (s) => { try { return formatDistanceToNow(new Date(s), { addSuffix: true }); } catch { return ""; } };

  return (
    <div data-testid="admin-startup-section">
      {/* Header + actions */}
      <div className={`rounded-xl p-4 mb-4 border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200"}`}>
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center text-white">
              <Rocket size={20} />
            </div>
            <div>
              <h2 className={`text-lg font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
                Startup Applications · Hyderabad's Next 100
              </h2>
              <p className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-600"}`}>
                {applications.length} total · stored in MongoDB <code className="text-orange-600">startup_applications</code>
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button data-testid="startup-refresh-btn" variant="outline" size="sm" onClick={fetchApplications}>
              <RefreshCw size={14} className={`mr-1.5 ${loading ? "animate-spin" : ""}`} /> Refresh
            </Button>
            <Button data-testid="startup-export-csv-btn" onClick={downloadCSV} className="bg-emerald-600 hover:bg-emerald-700 text-white" size="sm">
              <Download size={14} className="mr-1.5" /> Download Excel (CSV)
            </Button>
          </div>
        </div>

        {/* Status pills */}
        <div className="flex flex-wrap gap-2 mt-4">
          <button
            onClick={() => setStatusFilter("all")}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${statusFilter === "all" ? "bg-orange-500 text-white" : darkMode ? "bg-slate-700 text-slate-300" : "bg-white border border-slate-200 text-slate-600"}`}
          >
            All ({applications.length})
          </button>
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1 rounded-full text-xs font-semibold capitalize transition-all ${statusFilter === s ? "bg-orange-500 text-white" : darkMode ? "bg-slate-700 text-slate-300" : "bg-white border border-slate-200 text-slate-600"}`}
            >
              {s} ({counts[s] || 0})
            </button>
          ))}
        </div>
      </div>

      {/* Search */}
      <Input
        data-testid="startup-search-input"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search by name, mobile, email, idea, area..."
        className={`mb-4 ${darkMode ? "bg-slate-800 border-slate-700 text-white" : ""}`}
      />

      {/* Table */}
      <div className={`rounded-lg border overflow-hidden ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
        <Table>
          <TableHeader>
            <TableRow className={darkMode ? "bg-slate-700" : "bg-slate-50"}>
              <TableHead>Founder</TableHead>
              <TableHead>Contact</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Idea</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Applied</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={7} className="text-center py-8"><Loader2 className="animate-spin mx-auto" /></TableCell></TableRow>
            ) : fetchError ? (
              <TableRow><TableCell colSpan={7} className="text-center py-8">
                <div className="flex flex-col items-center gap-2">
                  <XCircle size={24} className="text-red-500" />
                  <p className="text-sm text-red-600">{fetchError}</p>
                  <Button size="sm" variant="outline" onClick={fetchApplications}><RefreshCw size={12} className="mr-1" />Retry</Button>
                </div>
              </TableCell></TableRow>
            ) : filtered.length === 0 ? (
              <TableRow><TableCell colSpan={7} className="text-center py-8 text-slate-500">No applications {searchQuery ? "match your search" : "yet"}</TableCell></TableRow>
            ) : (
              filtered.map((app) => (
                <TableRow key={app.id} data-testid={`startup-app-row-${app.id}`}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${app.is_woman_founder ? "bg-pink-100 text-pink-700" : "bg-orange-100 text-orange-700"}`}>
                        {app.name?.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className={`font-medium text-sm ${darkMode ? "text-white" : "text-slate-900"}`}>{app.name}</p>
                        {app.age && <p className="text-[11px] text-slate-500">Age {app.age}{app.is_woman_founder ? " · Woman founder" : ""}</p>}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <p className="text-xs text-slate-700 dark:text-slate-300">+91 {app.mobile}</p>
                    <p className="text-[11px] text-slate-500">{app.email}</p>
                  </TableCell>
                  <TableCell className="text-xs text-slate-600 dark:text-slate-400">
                    {[app.colony, app.area, app.city].filter(Boolean).join(", ") || "N/A"}
                  </TableCell>
                  <TableCell><p className="text-xs text-slate-700 dark:text-slate-300 line-clamp-2 max-w-xs">{app.idea}</p></TableCell>
                  <TableCell>{getStatusBadge(app.status)}</TableCell>
                  <TableCell className="text-xs text-slate-500">{fmtTime(app.created_at)}</TableCell>
                  <TableCell>
                    <div className="flex justify-end gap-1.5">
                      <Button data-testid={`startup-view-${app.id}`} size="sm" variant="ghost" className="h-8" onClick={() => setSelectedApp(app)}><Eye size={14} /></Button>
                      <Select onValueChange={(v) => updateStatus(app.id, v)}>
                        <SelectTrigger className="h-8 w-[100px] text-xs">
                          <SelectValue placeholder="Action" />
                        </SelectTrigger>
                        <SelectContent>
                          {STATUSES.filter((s) => s !== app.status).map((s) => (
                            <SelectItem key={s} value={s} className="capitalize">{s}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Detail dialog */}
      <Dialog open={!!selectedApp} onOpenChange={() => setSelectedApp(null)}>
        <DialogContent className={`max-w-2xl ${darkMode ? "bg-slate-800 border-slate-700" : ""}`}>
          <DialogHeader>
            <DialogTitle className={darkMode ? "text-white" : ""}>Application Details</DialogTitle>
          </DialogHeader>
          {selectedApp && (
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className={`text-xl font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>{selectedApp.name}</h3>
                  <p className={`text-sm ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                    Applied {fmtTime(selectedApp.created_at)}
                  </p>
                </div>
                {getStatusBadge(selectedApp.status)}
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <DetailRow icon={<Phone size={13} />} label="Mobile" value={`+91 ${selectedApp.mobile}`} darkMode={darkMode} />
                <DetailRow icon={<Mail size={13} />} label="Email" value={selectedApp.email} darkMode={darkMode} />
                <DetailRow icon={<User size={13} />} label="Age" value={selectedApp.age || "N/A"} darkMode={darkMode} />
                <DetailRow icon={<Award size={13} />} label="Founder type" value={selectedApp.is_woman_founder ? "Woman founder" : "Founder"} darkMode={darkMode} />
                <DetailRow icon={<MapPin size={13} />} label="Colony" value={selectedApp.colony || "N/A"} darkMode={darkMode} />
                <DetailRow icon={<MapPin size={13} />} label="Area" value={selectedApp.area || "N/A"} darkMode={darkMode} />
                <DetailRow icon={<MapPin size={13} />} label="City" value={selectedApp.city || "N/A"} darkMode={darkMode} />
                <DetailRow icon={<Calendar size={13} />} label="Submitted" value={new Date(selectedApp.created_at).toLocaleString()} darkMode={darkMode} />
              </div>

              <div>
                <p className={`text-xs font-semibold mb-1 ${darkMode ? "text-slate-400" : "text-slate-500"}`}>BUSINESS IDEA</p>
                <p className={`text-sm leading-relaxed p-3 rounded-lg ${darkMode ? "bg-slate-900 text-slate-200" : "bg-slate-50 text-slate-800"}`}>
                  {selectedApp.idea}
                </p>
              </div>

              {(selectedApp.pitch_pdf_url || selectedApp.pitch_video_url) && (
                <div className="flex gap-2">
                  {selectedApp.pitch_pdf_url && (
                    <a href={selectedApp.pitch_pdf_url} target="_blank" rel="noopener noreferrer" className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-orange-100 text-orange-700 hover:bg-orange-200 text-sm font-medium">
                      <FileText size={14} /> View Pitch Deck
                    </a>
                  )}
                  {selectedApp.pitch_video_url && (
                    <a href={selectedApp.pitch_video_url} target="_blank" rel="noopener noreferrer" className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-purple-100 text-purple-700 hover:bg-purple-200 text-sm font-medium">
                      <Video size={14} /> Watch Pitch Video
                    </a>
                  )}
                </div>
              )}

              {selectedApp.rejection_reason && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
                  <strong>Rejection reason:</strong> {selectedApp.rejection_reason}
                </div>
              )}
            </div>
          )}
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setSelectedApp(null)}>Close</Button>
            {selectedApp && selectedApp.status !== "selected" && (
              <Button data-testid="startup-mark-selected-btn" onClick={() => updateStatus(selectedApp.id, "selected")} className="bg-green-600 hover:bg-green-700">
                <CheckCircle size={14} className="mr-1" /> Mark Selected
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const DetailRow = ({ icon, label, value, darkMode }) => (
  <div>
    <p className={`text-[11px] font-semibold uppercase tracking-wide flex items-center gap-1 ${darkMode ? "text-slate-500" : "text-slate-400"}`}>{icon} {label}</p>
    <p className={`text-sm mt-0.5 ${darkMode ? "text-slate-200" : "text-slate-800"}`}>{value}</p>
  </div>
);
