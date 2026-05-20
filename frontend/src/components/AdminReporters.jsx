import { useState, useEffect, useContext, useCallback } from "react";
import axios from "axios";
import { API, AppContext } from "../App";
import { toast } from "sonner";
import { 
  User, CheckCircle, XCircle, Clock, Loader2, 
  RefreshCw, FileText, Video, Mic, Eye
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../components/ui/dialog";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../components/ui/tabs";
import { formatDistanceToNow } from "date-fns";

export const AdminReporters = () => {
  const { language, darkMode } = useContext(AppContext);
  
  const [reporters, setReporters] = useState([]);
  const [reporterNews, setReporterNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [selectedReporter, setSelectedReporter] = useState(null);
  const [selectedNews, setSelectedNews] = useState(null);
  const [rejectReason, setRejectReason] = useState("");
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [rejectType, setRejectType] = useState(null); // 'reporter' or 'news'
  const [rejectId, setRejectId] = useState(null);

  const fetchReporters = useCallback(async () => {
    try {
      setLoading(true);
      setFetchError(null);
      const response = await axios.get(`${API}/admin/reporters`);
      setReporters(response.data);
    } catch (error) {
      console.error("Failed to fetch reporters:", error);
      const msg = error.response?.data?.detail || error.message || "Failed to load reporters";
      setFetchError(msg);
      toast.error(`Failed to load reporters: ${msg}`);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchReporterNews = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/admin/reporter-news`);
      setReporterNews(response.data);
    } catch (error) {
      console.error("Failed to fetch reporter news:", error);
      toast.error("Failed to load reporter submissions");
    }
  }, []);

  useEffect(() => {
    fetchReporters();
    fetchReporterNews();
  }, [fetchReporters, fetchReporterNews]);

  const approveReporter = async (reporterId) => {
    try {
      await axios.post(`${API}/admin/reporters/${reporterId}/approve`);
      toast.success("Reporter approved!");
      fetchReporters();
    } catch (error) {
      toast.error("Failed to approve reporter");
    }
  };

  const rejectReporter = async () => {
    try {
      await axios.post(`${API}/admin/reporters/${rejectId}/reject?reason=${encodeURIComponent(rejectReason)}`);
      toast.success("Reporter rejected");
      setShowRejectDialog(false);
      setRejectReason("");
      fetchReporters();
    } catch (error) {
      toast.error("Failed to reject reporter");
    }
  };

  const approveNews = async (newsId) => {
    try {
      await axios.post(`${API}/admin/reporter-news/${newsId}/approve`);
      toast.success("News approved and published!");
      fetchReporterNews();
    } catch (error) {
      toast.error("Failed to approve news");
    }
  };

  const rejectNews = async () => {
    try {
      await axios.post(`${API}/admin/reporter-news/${rejectId}/reject?reason=${encodeURIComponent(rejectReason)}`);
      toast.success("News rejected");
      setShowRejectDialog(false);
      setRejectReason("");
      fetchReporterNews();
    } catch (error) {
      toast.error("Failed to reject news");
    }
  };

  const openRejectDialog = (type, id) => {
    setRejectType(type);
    setRejectId(id);
    setRejectReason("");
    setShowRejectDialog(true);
  };

  const handleReject = () => {
    if (rejectType === "reporter") {
      rejectReporter();
    } else {
      rejectNews();
    }
  };

  const getTimeAgo = (dateStr) => {
    try {
      return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
    } catch {
      return "";
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "approved":
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100"><CheckCircle size={12} className="mr-1" />Approved</Badge>;
      case "rejected":
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100"><XCircle size={12} className="mr-1" />Rejected</Badge>;
      default:
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100"><Clock size={12} className="mr-1" />Pending</Badge>;
    }
  };

  const getNewsTypeIcon = (type) => {
    switch (type) {
      case "video_url":
        return <Video size={14} className="text-red-500" />;
      case "reporter_video":
        return <Mic size={14} className="text-purple-500" />;
      default:
        return <FileText size={14} className="text-orange-500" />;
    }
  };

  const pendingReporters = reporters.filter(r => r.status === "pending");
  const pendingNews = reporterNews.filter(n => n.status === "pending");

  return (
    <div data-testid="admin-reporters-section">
      <Tabs defaultValue="reporters" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-4">
          <TabsTrigger value="reporters" className="relative">
            Reporters
            {pendingReporters.length > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {pendingReporters.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="news" className="relative">
            Reporter News
            {pendingNews.length > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {pendingNews.length}
              </span>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Reporters Tab */}
        <TabsContent value="reporters">
          <div className="flex justify-between items-center mb-4">
            <h3 className={`font-semibold ${darkMode ? "text-white" : "text-slate-900"}`}>
              Reporter Applications ({reporters.length})
            </h3>
            <Button variant="ghost" size="sm" onClick={fetchReporters}>
              <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            </Button>
          </div>

          <div className={`rounded-lg border overflow-hidden ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
            <Table>
              <TableHeader>
                <TableRow className={darkMode ? "bg-slate-700" : "bg-slate-50"}>
                  <TableHead>Reporter</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Applied</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8">
                      <Loader2 className="animate-spin mx-auto" />
                    </TableCell>
                  </TableRow>
                ) : fetchError ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8">
                      <div data-testid="reporters-error-state" className="flex flex-col items-center gap-3">
                        <XCircle size={28} className="text-red-500" />
                        <p className="text-sm text-red-600 font-medium">{fetchError}</p>
                        <Button
                          size="sm"
                          variant="outline"
                          data-testid="reporters-retry-btn"
                          onClick={fetchReporters}
                          className="text-orange-600 border-orange-300 hover:bg-orange-50"
                        >
                          <RefreshCw size={14} className="mr-1.5" />
                          Retry
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : reporters.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8 text-slate-500">
                      No reporter applications yet
                    </TableCell>
                  </TableRow>
                ) : (
                  reporters.map((reporter) => (
                    <TableRow key={reporter.id} data-testid={`reporter-row-${reporter.id}`}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          {reporter.photo ? (
                            <img src={reporter.photo} alt="" className="w-10 h-10 rounded-full object-cover" />
                          ) : (
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${darkMode ? "bg-slate-600" : "bg-slate-200"}`}>
                              <User size={18} className="text-slate-500" />
                            </div>
                          )}
                          <div>
                            <p className={`font-medium ${darkMode ? "text-white" : "text-slate-900"}`}>{reporter.name}</p>
                            <p className="text-xs text-slate-500">{reporter.reporter_id}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <p className={`text-sm ${darkMode ? "text-slate-300" : "text-slate-700"}`}>{reporter.phone}</p>
                        <p className="text-xs text-slate-500">{reporter.location || "N/A"}</p>
                      </TableCell>
                      <TableCell>{getStatusBadge(reporter.status)}</TableCell>
                      <TableCell className="text-sm text-slate-500">{getTimeAgo(reporter.created_at)}</TableCell>
                      <TableCell>
                        <div className="flex justify-end gap-2">
                          {reporter.status === "pending" && (
                            <>
                              <Button
                                size="sm"
                                data-testid={`approve-reporter-${reporter.id}`}
                                onClick={() => approveReporter(reporter.id)}
                                className="bg-green-600 hover:bg-green-700 h-8"
                              >
                                <CheckCircle size={14} className="mr-1" />
                                Approve
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                data-testid={`reject-reporter-${reporter.id}`}
                                onClick={() => openRejectDialog("reporter", reporter.id)}
                                className="text-red-600 border-red-300 hover:bg-red-50 h-8"
                              >
                                <XCircle size={14} className="mr-1" />
                                Reject
                              </Button>
                            </>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => setSelectedReporter(reporter)}
                            className="h-8"
                          >
                            <Eye size={14} />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>

        {/* Reporter News Tab */}
        <TabsContent value="news">
          <div className="flex justify-between items-center mb-4">
            <h3 className={`font-semibold ${darkMode ? "text-white" : "text-slate-900"}`}>
              Reporter Submissions ({reporterNews.length})
            </h3>
            <Button variant="ghost" size="sm" onClick={fetchReporterNews}>
              <RefreshCw size={16} />
            </Button>
          </div>

          <div className={`rounded-lg border overflow-hidden ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
            <Table>
              <TableHeader>
                <TableRow className={darkMode ? "bg-slate-700" : "bg-slate-50"}>
                  <TableHead>News</TableHead>
                  <TableHead>Reporter</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reporterNews.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8 text-slate-500">
                      No reporter news submissions yet
                    </TableCell>
                  </TableRow>
                ) : (
                  reporterNews.map((news) => (
                    <TableRow key={news.id} data-testid={`reporter-news-row-${news.id}`}>
                      <TableCell>
                        <div className="max-w-xs">
                          <p className={`font-medium line-clamp-1 ${darkMode ? "text-white" : "text-slate-900"}`}>{news.title}</p>
                          <p className="text-xs text-slate-500 line-clamp-1">{news.summary}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <p className={`text-sm ${darkMode ? "text-slate-300" : "text-slate-700"}`}>{news.reporter_name}</p>
                        <p className="text-xs text-slate-500">{news.reporter_id}</p>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          {getNewsTypeIcon(news.news_type)}
                          <span className="text-xs text-slate-500 capitalize">{news.news_type.replace("_", " ")}</span>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(news.status)}</TableCell>
                      <TableCell>
                        <div className="flex justify-end gap-2">
                          {news.status === "pending" && (
                            <>
                              <Button
                                size="sm"
                                data-testid={`approve-news-${news.id}`}
                                onClick={() => approveNews(news.id)}
                                className="bg-green-600 hover:bg-green-700 h-8"
                              >
                                <CheckCircle size={14} className="mr-1" />
                                Publish
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                data-testid={`reject-news-${news.id}`}
                                onClick={() => openRejectDialog("news", news.id)}
                                className="text-red-600 border-red-300 hover:bg-red-50 h-8"
                              >
                                <XCircle size={14} />
                              </Button>
                            </>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => setSelectedNews(news)}
                            className="h-8"
                          >
                            <Eye size={14} />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>

      {/* Reject Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent className={darkMode ? "bg-slate-800 border-slate-700" : ""}>
          <DialogHeader>
            <DialogTitle className={darkMode ? "text-white" : ""}>
              Reject {rejectType === "reporter" ? "Reporter" : "News"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className={`text-sm font-medium ${darkMode ? "text-slate-200" : ""}`}>
                Rejection Reason (Optional)
              </label>
              <Input
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Enter reason for rejection..."
                className={`mt-1 ${darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}`}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRejectDialog(false)}>Cancel</Button>
            <Button onClick={handleReject} className="bg-red-600 hover:bg-red-700">
              Confirm Reject
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reporter Details Dialog */}
      <Dialog open={!!selectedReporter} onOpenChange={() => setSelectedReporter(null)}>
        <DialogContent className={darkMode ? "bg-slate-800 border-slate-700" : ""}>
          <DialogHeader>
            <DialogTitle className={darkMode ? "text-white" : ""}>Reporter Details</DialogTitle>
          </DialogHeader>
          {selectedReporter && (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                {selectedReporter.photo ? (
                  <img src={selectedReporter.photo} alt="" className="w-16 h-16 rounded-full object-cover" />
                ) : (
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center ${darkMode ? "bg-slate-600" : "bg-slate-200"}`}>
                    <User size={24} />
                  </div>
                )}
                <div>
                  <h3 className={`text-lg font-semibold ${darkMode ? "text-white" : ""}`}>{selectedReporter.name}</h3>
                  <p className="text-sm text-slate-500">{selectedReporter.reporter_id}</p>
                  {getStatusBadge(selectedReporter.status)}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-slate-500">Phone</p>
                  <p className={darkMode ? "text-white" : ""}>{selectedReporter.phone}</p>
                </div>
                <div>
                  <p className="text-slate-500">Email</p>
                  <p className={darkMode ? "text-white" : ""}>{selectedReporter.email || "N/A"}</p>
                </div>
                <div>
                  <p className="text-slate-500">Location</p>
                  <p className={darkMode ? "text-white" : ""}>{selectedReporter.location || "N/A"}</p>
                </div>
                <div>
                  <p className="text-slate-500">News Submitted</p>
                  <p className={darkMode ? "text-white" : ""}>{selectedReporter.news_submitted}</p>
                </div>
              </div>
              {selectedReporter.bio && (
                <div>
                  <p className="text-slate-500 text-sm">Bio</p>
                  <p className={`text-sm ${darkMode ? "text-slate-300" : ""}`}>{selectedReporter.bio}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* News Details Dialog */}
      <Dialog open={!!selectedNews} onOpenChange={() => setSelectedNews(null)}>
        <DialogContent className={`max-w-2xl ${darkMode ? "bg-slate-800 border-slate-700" : ""}`}>
          <DialogHeader>
            <DialogTitle className={darkMode ? "text-white" : ""}>News Submission Details</DialogTitle>
          </DialogHeader>
          {selectedNews && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                {getNewsTypeIcon(selectedNews.news_type)}
                <span className="text-sm text-slate-500 capitalize">{selectedNews.news_type.replace("_", " ")}</span>
                {getStatusBadge(selectedNews.status)}
              </div>
              
              <div>
                <h3 className={`text-lg font-semibold ${darkMode ? "text-white" : ""}`}>{selectedNews.title}</h3>
                {selectedNews.title_te && (
                  <p className={`font-telugu ${darkMode ? "text-slate-300" : "text-slate-600"}`}>{selectedNews.title_te}</p>
                )}
              </div>
              
              <div>
                <p className={`text-sm ${darkMode ? "text-slate-300" : "text-slate-700"}`}>{selectedNews.summary}</p>
                {selectedNews.summary_te && (
                  <p className={`text-sm font-telugu mt-2 ${darkMode ? "text-slate-400" : "text-slate-600"}`}>{selectedNews.summary_te}</p>
                )}
              </div>

              {selectedNews.image && (
                <img src={selectedNews.image} alt="" className="w-full h-48 object-cover rounded-lg" />
              )}

              {selectedNews.video_url && (
                <div>
                  <p className="text-sm text-slate-500 mb-1">Video URL:</p>
                  <a href={selectedNews.video_url} target="_blank" rel="noopener noreferrer" className="text-orange-500 text-sm break-all">
                    {selectedNews.video_url}
                  </a>
                </div>
              )}

              {selectedNews.reporter_video_url && (
                <div>
                  <p className="text-sm text-slate-500 mb-1">Reporter Video URL:</p>
                  <a href={selectedNews.reporter_video_url} target="_blank" rel="noopener noreferrer" className="text-orange-500 text-sm break-all">
                    {selectedNews.reporter_video_url}
                  </a>
                </div>
              )}

              <div className="flex items-center gap-4 text-sm text-slate-500">
                <span>By: {selectedNews.reporter_name} ({selectedNews.reporter_id})</span>
                <span>•</span>
                <span>{getTimeAgo(selectedNews.created_at)}</span>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};
