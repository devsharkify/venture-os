import { useState, useEffect, useContext, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { API, AppContext } from "../App";
import { toast } from "sonner";
import { 
  User, Clock, CheckCircle, XCircle, AlertCircle, 
  Plus, FileText, Video, Mic, Download, Loader2,
  ArrowLeft, RefreshCw
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { VideoRecorder } from "../components/VideoRecorder";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../components/ui/dialog";
import { formatDistanceToNow } from "date-fns";
import { FileUpload } from "../components/FileUpload";

export default function ReporterDashboard() {
  const { reporterId } = useParams();
  const { language, darkMode, categories } = useContext(AppContext);
  const navigate = useNavigate();
  
  const [reporter, setReporter] = useState(null);
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showIdCard, setShowIdCard] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [idCardData, setIdCardData] = useState(null);
  
  const [newsForm, setNewsForm] = useState({
    title: "",
    title_te: "",
    summary: "",
    summary_te: "",
    category: "local",
    news_type: "text",
    image: "",
    video_url: "",
    reporter_video_url: "",
    location: ""
  });

  const fetchReporter = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/reporter/${reporterId}`);
      setReporter(response.data);
    } catch (error) {
      console.error("Failed to fetch reporter:", error);
      toast.error("Reporter not found");
      navigate("/reporter/register");
    } finally {
      setLoading(false);
    }
  }, [reporterId, navigate]);

  const fetchNews = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/reporter/${reporterId}/news`);
      setNews(response.data);
    } catch (error) {
      console.error("Failed to fetch news:", error);
    }
  }, [reporterId]);

  const fetchIdCard = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/reporter/${reporterId}/id-card`);
      setIdCardData(response.data);
      setShowIdCard(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to get ID card");
    }
  }, [reporterId]);

  useEffect(() => {
    fetchReporter();
    fetchNews();
  }, [fetchReporter, fetchNews]);

  const handleSubmitNews = async () => {
    if (!newsForm.title || !newsForm.summary) {
      toast.error(language === "en" ? "Title and summary are required" : "శీర్షిక మరియు సారాంశం అవసరం");
      return;
    }

    try {
      setSubmitting(true);
      // Map record_video type to reporter_video for backend
      const submitData = { ...newsForm };
      if (submitData.news_type === "record_video") {
        submitData.news_type = "reporter_video";
      }
      await axios.post(`${API}/reporter/${reporterId}/submit-news`, submitData);
      toast.success(language === "en" ? "News submitted for review!" : "వార్త సమీక్ష కోసం సమర్పించబడింది!");
      setShowSubmitModal(false);
      resetNewsForm();
      fetchNews();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to submit news");
    } finally {
      setSubmitting(false);
    }
  };

  const resetNewsForm = () => {
    setNewsForm({
      title: "",
      title_te: "",
      summary: "",
      summary_te: "",
      category: "local",
      news_type: "text",
      image: "",
      video_url: "",
      reporter_video_url: "",
      location: ""
    });
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
        return <Badge className="bg-green-100 text-green-800"><CheckCircle size={12} className="mr-1" />Approved</Badge>;
      case "rejected":
        return <Badge className="bg-red-100 text-red-800"><XCircle size={12} className="mr-1" />Rejected</Badge>;
      default:
        return <Badge className="bg-yellow-100 text-yellow-800"><Clock size={12} className="mr-1" />Pending</Badge>;
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

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? "bg-slate-900" : "bg-slate-50"}`}>
        <Loader2 size={40} className="animate-spin text-orange-500" />
      </div>
    );
  }

  if (!reporter) return null;

  return (
    <div data-testid="reporter-dashboard-page" className={`min-h-screen ${darkMode ? "bg-slate-900" : "bg-slate-50"}`}>
      {/* Header */}
      <div className={`border-b py-4 px-4 ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/")}
              className={darkMode ? "text-slate-300" : ""}
            >
              <ArrowLeft size={20} />
            </Button>
            <div className="flex items-center gap-3">
              {reporter.photo ? (
                <img src={reporter.photo} alt={reporter.name} className="w-12 h-12 rounded-full object-cover" />
              ) : (
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${darkMode ? "bg-slate-700" : "bg-slate-200"}`}>
                  <User size={24} className={darkMode ? "text-slate-400" : "text-slate-500"} />
                </div>
              )}
              <div>
                <h1 className={`text-lg font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
                  {reporter.name}
                </h1>
                <div className="flex items-center gap-2">
                  <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                    {reporter.reporter_id}
                  </span>
                  {getStatusBadge(reporter.status)}
                </div>
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => { fetchReporter(); fetchNews(); }}
          >
            <RefreshCw size={18} />
          </Button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Status Alert */}
        {reporter.status === "pending" && (
          <div className="mb-6 p-4 rounded-lg bg-yellow-100 border border-yellow-300">
            <div className="flex items-center gap-2">
              <AlertCircle size={20} className="text-yellow-600" />
              <p className={`font-medium text-yellow-800 ${language === "te" ? "font-telugu" : ""}`}>
                {language === "en" ? "Your registration is pending approval" : "మీ రిజిస్ట్రేషన్ ఆమోదం కోసం పెండింగ్‌లో ఉంది"}
              </p>
            </div>
            <p className={`text-sm text-yellow-700 mt-1 ${language === "te" ? "font-telugu" : ""}`}>
              {language === "en" 
                ? "You'll be able to submit news once approved by admin."
                : "అడ్మిన్ ఆమోదించిన తర్వాత మీరు వార్తలను సమర్పించగలరు."}
            </p>
          </div>
        )}

        {reporter.status === "rejected" && (
          <div className="mb-6 p-4 rounded-lg bg-red-100 border border-red-300">
            <div className="flex items-center gap-2">
              <XCircle size={20} className="text-red-600" />
              <p className="font-medium text-red-800">
                {language === "en" ? "Your registration was rejected" : "మీ రిజిస్ట్రేషన్ తిరస్కరించబడింది"}
              </p>
            </div>
            {reporter.rejection_reason && (
              <p className="text-sm text-red-700 mt-1">Reason: {reporter.rejection_reason}</p>
            )}
          </div>
        )}

        {/* Stats */}
        {reporter.status === "approved" && (
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className={`p-4 rounded-lg border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
              <p className="text-2xl font-bold text-orange-500">{reporter.news_submitted}</p>
              <p className={`text-sm ${darkMode ? "text-slate-400" : "text-slate-600"}`}>
                {language === "en" ? "Submitted" : "సమర్పించిన"}
              </p>
            </div>
            <div className={`p-4 rounded-lg border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
              <p className="text-2xl font-bold text-green-600">{reporter.news_approved}</p>
              <p className={`text-sm ${darkMode ? "text-slate-400" : "text-slate-600"}`}>
                {language === "en" ? "Approved" : "ఆమోదించిన"}
              </p>
            </div>
            <div className={`p-4 rounded-lg border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
              <p className="text-2xl font-bold text-purple-600">
                {reporter.news_submitted > 0 ? Math.round((reporter.news_approved / reporter.news_submitted) * 100) : 0}%
              </p>
              <p className={`text-sm ${darkMode ? "text-slate-400" : "text-slate-600"}`}>
                {language === "en" ? "Success Rate" : "విజయ రేటు"}
              </p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        {reporter.status === "approved" && (
          <div className="flex gap-3 mb-6">
            <Button
              data-testid="submit-news-btn"
              onClick={() => setShowSubmitModal(true)}
              className="bg-orange-500 hover:bg-orange-600 flex-1"
            >
              <Plus size={18} className="mr-2" />
              {language === "en" ? "Submit News" : "వార్త సమర్పించండి"}
            </Button>
            <Button
              data-testid="download-id-btn"
              onClick={fetchIdCard}
              variant="outline"
              className={darkMode ? "border-slate-600 text-slate-200" : ""}
            >
              <Download size={18} className="mr-2" />
              {language === "en" ? "ID Card" : "ID కార్డ్"}
            </Button>
          </div>
        )}

        {/* News List */}
        <div className={`rounded-lg border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
          <div className="p-4 border-b border-slate-200 dark:border-slate-700">
            <h2 className={`font-semibold ${darkMode ? "text-white" : "text-slate-900"}`}>
              {language === "en" ? "Your Submissions" : "మీ సమర్పణలు"}
            </h2>
          </div>
          
          {news.length === 0 ? (
            <div className="p-8 text-center">
              <FileText size={40} className={`mx-auto mb-3 ${darkMode ? "text-slate-600" : "text-slate-400"}`} />
              <p className={darkMode ? "text-slate-400" : "text-slate-500"}>
                {language === "en" ? "No news submitted yet" : "ఇంకా వార్తలు సమర్పించలేదు"}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-700">
              {news.map((item) => (
                <div key={item.id} className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {getNewsTypeIcon(item.news_type)}
                        <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                          {item.news_type === "text" ? "Text" : item.news_type === "video_url" ? "Video URL" : "Reporter Video"}
                        </span>
                        <span className={`text-xs ${darkMode ? "text-slate-500" : "text-slate-400"}`}>
                          • {getTimeAgo(item.created_at)}
                        </span>
                      </div>
                      <h3 className={`font-medium line-clamp-1 ${darkMode ? "text-white" : "text-slate-900"}`}>
                        {language === "en" ? item.title : (item.title_te || item.title)}
                      </h3>
                      <p className={`text-sm line-clamp-2 mt-1 ${darkMode ? "text-slate-400" : "text-slate-600"}`}>
                        {language === "en" ? item.summary : (item.summary_te || item.summary)}
                      </p>
                    </div>
                    {getStatusBadge(item.status)}
                  </div>
                  {item.status === "rejected" && item.rejection_reason && (
                    <p className="text-xs text-red-500 mt-2">Reason: {item.rejection_reason}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Submit News Modal */}
      <Dialog open={showSubmitModal} onOpenChange={setShowSubmitModal}>
        <DialogContent className={`max-w-2xl max-h-[90vh] overflow-y-auto ${darkMode ? "bg-slate-800 border-slate-700" : ""}`}>
          <DialogHeader>
            <DialogTitle className={darkMode ? "text-white" : ""}>
              {language === "en" ? "Submit News" : "వార్త సమర్పించండి"}
            </DialogTitle>
          </DialogHeader>

          <Tabs value={newsForm.news_type} onValueChange={(v) => setNewsForm(prev => ({ ...prev, news_type: v }))}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="text" data-testid="news-type-text">
                <FileText size={14} className="mr-1" />
                {language === "en" ? "Text" : "టెక్స్ట్"}
              </TabsTrigger>
              <TabsTrigger value="video_url" data-testid="news-type-video">
                <Video size={14} className="mr-1" />
                {language === "en" ? "Video" : "వీడియో"}
              </TabsTrigger>
              <TabsTrigger value="reporter_video" data-testid="news-type-reporter">
                <Mic size={14} className="mr-1" />
                {language === "en" ? "Upload" : "అప్‌లోడ్"}
              </TabsTrigger>
              <TabsTrigger value="record_video" data-testid="news-type-record">
                <Video size={14} className="mr-1" />
                {language === "en" ? "Record" : "రికార్డ్"}
              </TabsTrigger>
            </TabsList>

            <div className="mt-4 space-y-4">
              {/* Title */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className={darkMode ? "text-slate-200" : ""}>Title (English) *</Label>
                  <Input
                    data-testid="news-title-input"
                    value={newsForm.title}
                    onChange={(e) => setNewsForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="News headline"
                    className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                  />
                </div>
                <div className="space-y-2">
                  <Label className={darkMode ? "text-slate-200" : ""}>Title (Telugu)</Label>
                  <Input
                    data-testid="news-title-te-input"
                    value={newsForm.title_te}
                    onChange={(e) => setNewsForm(prev => ({ ...prev, title_te: e.target.value }))}
                    placeholder="తెలుగులో శీర్షిక"
                    className={`font-telugu ${darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}`}
                  />
                </div>
              </div>

              {/* Summary */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className={darkMode ? "text-slate-200" : ""}>Summary (English) *</Label>
                  <Textarea
                    data-testid="news-summary-input"
                    value={newsForm.summary}
                    onChange={(e) => setNewsForm(prev => ({ ...prev, summary: e.target.value }))}
                    placeholder="News details"
                    rows={4}
                    className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                  />
                </div>
                <div className="space-y-2">
                  <Label className={darkMode ? "text-slate-200" : ""}>Summary (Telugu)</Label>
                  <Textarea
                    data-testid="news-summary-te-input"
                    value={newsForm.summary_te}
                    onChange={(e) => setNewsForm(prev => ({ ...prev, summary_te: e.target.value }))}
                    placeholder="తెలుగులో వివరాలు"
                    rows={4}
                    className={`font-telugu ${darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}`}
                  />
                </div>
              </div>

              {/* Category & Location */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className={darkMode ? "text-slate-200" : ""}>Category</Label>
                  <Select 
                    value={newsForm.category} 
                    onValueChange={(v) => setNewsForm(prev => ({ ...prev, category: v }))}
                  >
                    <SelectTrigger className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(categories).map(([key, value]) => (
                        <SelectItem key={key} value={key}>{value.en}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className={darkMode ? "text-slate-200" : ""}>Location</Label>
                  <Input
                    data-testid="news-location-input"
                    value={newsForm.location}
                    onChange={(e) => setNewsForm(prev => ({ ...prev, location: e.target.value }))}
                    placeholder="Where this news happened"
                    className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                  />
                </div>
              </div>

              {/* Image Upload */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-slate-200" : ""}>
                  {language === "en" ? "News Image" : "వార్త ఇమేజ్"}
                </Label>
                <FileUpload 
                  type="image"
                  currentUrl={newsForm.image}
                  onUpload={(url) => setNewsForm(prev => ({ ...prev, image: url }))}
                />
              </div>

              {/* Video URL (for video_url type) */}
              <TabsContent value="video_url" className="mt-0">
                <div className="space-y-2">
                  <Label className={darkMode ? "text-slate-200" : ""}>YouTube Video URL *</Label>
                  <Input
                    data-testid="news-video-url-input"
                    value={newsForm.video_url}
                    onChange={(e) => setNewsForm(prev => ({ ...prev, video_url: e.target.value }))}
                    placeholder="https://youtube.com/watch?v=..."
                    className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                  />
                </div>
              </TabsContent>

              {/* Reporter Video Upload */}
              <TabsContent value="reporter_video" className="mt-0">
                <div className="space-y-2">
                  <Label className={darkMode ? "text-slate-200" : ""}>
                    {language === "en" ? "Upload Your Video *" : "మీ వీడియో అప్‌లోడ్ చేయండి *"}
                  </Label>
                  <FileUpload 
                    type="video"
                    currentUrl={newsForm.reporter_video_url}
                    onUpload={(url) => setNewsForm(prev => ({ ...prev, reporter_video_url: url }))}
                  />
                  <p className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                    {language === "en" 
                      ? "Record yourself reporting the news (like a news anchor)"
                      : "వార్తలను రిపోర్ట్ చేస్తూ మిమ్మల్ని రికార్డ్ చేయండి (న్యూస్ యాంకర్ లాగా)"}
                  </p>
                </div>
              </TabsContent>

              {/* Record Video (in-app) */}
              <TabsContent value="record_video" className="mt-0">
                <div className="space-y-2">
                  <Label className={darkMode ? "text-slate-200" : ""}>
                    {language === "en" ? "Record Video from Camera" : "కెమెరా నుండి వీడియో రికార్డ్ చేయండి"}
                  </Label>
                  <VideoRecorder onUpload={(url) => setNewsForm(prev => ({ ...prev, reporter_video_url: url }))} />
                </div>
              </TabsContent>
            </div>
          </Tabs>

          <DialogFooter className="mt-6">
            <Button variant="outline" onClick={() => setShowSubmitModal(false)}>
              Cancel
            </Button>
            <Button
              data-testid="submit-news-confirm-btn"
              onClick={handleSubmitNews}
              disabled={submitting || !newsForm.title || !newsForm.summary}
              className="bg-orange-500 hover:bg-orange-600"
            >
              {submitting ? (
                <>
                  <Loader2 size={16} className="animate-spin mr-2" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle size={16} className="mr-2" />
                  Submit News
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ID Card Modal */}
      <Dialog open={showIdCard} onOpenChange={setShowIdCard}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Digital ID Card</DialogTitle>
          </DialogHeader>
          
          {idCardData && (
            <div 
              data-testid="reporter-id-card"
              className="bg-gradient-to-br from-orange-500 to-orange-700 rounded-xl p-6 text-white"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold">Mint Street</h3>
                  <p className="text-xs text-orange-200">Citizen Reporter</p>
                </div>
                <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                  <img src="/tvr-logo.png" alt="Mint Street" className="w-8 h-8 object-contain" />
                </div>
              </div>

              <div className="flex gap-4 mb-4">
                {idCardData.photo ? (
                  <img 
                    src={idCardData.photo} 
                    alt={idCardData.name}
                    className="w-20 h-20 rounded-lg object-cover border-2 border-white/30"
                  />
                ) : (
                  <div className="w-20 h-20 rounded-lg bg-white/20 flex items-center justify-center border-2 border-white/30">
                    <User size={32} />
                  </div>
                )}
                <div>
                  <h2 className="text-xl font-bold">{idCardData.name}</h2>
                  <p className="text-sm text-orange-200">{idCardData.designation}</p>
                  <p className="text-2xl font-mono font-bold mt-1">{idCardData.reporter_id}</p>
                </div>
              </div>

              <div className="space-y-1 text-sm">
                <p><span className="text-orange-200">Location:</span> {idCardData.location || "N/A"}</p>
                <p><span className="text-orange-200">Phone:</span> {idCardData.phone}</p>
                <p><span className="text-orange-200">Valid Until:</span> {idCardData.valid_until}</p>
              </div>

              <div className="mt-4 pt-4 border-t border-white/20 text-center">
                <p className="text-xs text-orange-200">This is a digital ID for Mint Street citizen reporters</p>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button 
              onClick={() => {
                // Create downloadable image (in production would use canvas/html2canvas)
                toast.success("ID Card saved! Take a screenshot to download.");
              }}
              className="w-full"
            >
              <Download size={16} className="mr-2" />
              Save ID Card
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export { ReporterDashboard };
