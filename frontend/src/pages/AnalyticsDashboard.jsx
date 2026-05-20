import { useState, useEffect, useContext, useCallback } from "react";
import axios from "axios";
import { API, AppContext } from "../App";
import {
  BarChart3, TrendingUp, Users, FileText, Eye, Download,
  RefreshCw, Loader2, Calendar, ArrowLeft
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";

export default function AnalyticsDashboard() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [articles, setArticles] = useState([]);
  const [downloading, setDownloading] = useState(false);

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const [overviewRes, articlesRes] = await Promise.all([
        axios.get(`${API}/analytics/overview`),
        axios.get(`${API}/analytics/articles?limit=20`)
      ]);
      setOverview(overviewRes.data);
      setArticles(articlesRes.data);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const downloadReport = async () => {
    try {
      setDownloading(true);
      const response = await axios.get(`${API}/analytics/report/csv`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analytics_report_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Download failed:", error);
    } finally {
      setDownloading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? "bg-slate-900" : "bg-slate-50"}`}>
        <Loader2 size={40} className="animate-spin text-orange-500" />
      </div>
    );
  }

  const summary = overview?.summary || {};

  return (
    <div data-testid="analytics-page" className={`min-h-screen ${darkMode ? "bg-slate-900" : "bg-slate-50"}`}>
      {/* Header */}
      <div className={`border-b py-4 px-4 sticky top-0 z-20 ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/admin")}
              className={darkMode ? "text-slate-300" : ""}
            >
              <ArrowLeft size={20} />
            </Button>
            <div className="flex items-center gap-2">
              <BarChart3 size={24} className="text-orange-500" />
              <h1 className={`text-xl font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
                Analytics Dashboard
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchAnalytics}
              className={darkMode ? "border-slate-600" : ""}
            >
              <RefreshCw size={14} className="mr-1" />
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={downloadReport}
              disabled={downloading}
              className="bg-green-600 hover:bg-green-700"
            >
              {downloading ? (
                <Loader2 size={14} className="animate-spin mr-1" />
              ) : (
                <Download size={14} className="mr-1" />
              )}
              Download CSV
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className={`p-4 rounded-xl border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
            <div className="flex items-center gap-2 mb-2">
              <Eye size={18} className="text-orange-500" />
              <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                Views Today
              </span>
            </div>
            <p className={`text-2xl font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
              {formatNumber(summary.views_today)}
            </p>
          </div>

          <div className={`p-4 rounded-xl border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp size={18} className="text-green-500" />
              <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                This Week
              </span>
            </div>
            <p className={`text-2xl font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
              {formatNumber(summary.views_week)}
            </p>
          </div>

          <div className={`p-4 rounded-xl border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
            <div className="flex items-center gap-2 mb-2">
              <Calendar size={18} className="text-purple-500" />
              <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                This Month
              </span>
            </div>
            <p className={`text-2xl font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
              {formatNumber(summary.views_month)}
            </p>
          </div>

          <div className={`p-4 rounded-xl border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
            <div className="flex items-center gap-2 mb-2">
              <Users size={18} className="text-orange-500" />
              <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                Total Users
              </span>
            </div>
            <p className={`text-2xl font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
              {formatNumber(summary.total_users)}
            </p>
          </div>
        </div>

        {/* Second Row Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className={`p-4 rounded-xl border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
            <div className="flex items-center gap-2 mb-1">
              <FileText size={16} className="text-orange-500" />
              <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                Total Articles
              </span>
            </div>
            <p className={`text-xl font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
              {summary.total_articles}
            </p>
          </div>

          <div className={`p-4 rounded-xl border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
            <div className="flex items-center gap-2 mb-1">
              <Users size={16} className="text-green-500" />
              <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                Reporters
              </span>
            </div>
            <p className={`text-xl font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
              {summary.approved_reporters}/{summary.total_reporters}
            </p>
          </div>

          <div className={`p-4 rounded-xl border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
            <div className="flex items-center gap-2 mb-1">
              <BarChart3 size={16} className="text-purple-500" />
              <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                Avg/Day
              </span>
            </div>
            <p className={`text-xl font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>
              {Math.round((summary.views_week || 0) / 7)}
            </p>
          </div>
        </div>

        {/* Daily Trend Chart (Simple bar representation) */}
        {overview?.daily_trend?.length > 0 && (
          <div className={`p-4 rounded-xl border mb-6 ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? "text-white" : "text-slate-900"}`}>
              Views Trend (Last 7 Days)
            </h3>
            <div className="flex items-end gap-2 h-32">
              {overview.daily_trend.map((day, index) => {
                const maxCount = Math.max(...overview.daily_trend.map(d => d.count));
                const height = maxCount > 0 ? (day.count / maxCount) * 100 : 0;
                return (
                  <div key={index} className="flex-1 flex flex-col items-center gap-1">
                    <span className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                      {day.count}
                    </span>
                    <div
                      className="w-full bg-orange-500 rounded-t transition-all"
                      style={{ height: `${Math.max(height, 5)}%` }}
                    />
                    <span className={`text-[10px] ${darkMode ? "text-slate-500" : "text-slate-400"}`}>
                      {day._id.slice(5)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Views by Category */}
        {overview?.views_by_category?.length > 0 && (
          <div className={`p-4 rounded-xl border mb-6 ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? "text-white" : "text-slate-900"}`}>
              Views by Category
            </h3>
            <div className="flex flex-wrap gap-2">
              {overview.views_by_category.map((cat, index) => (
                <Badge
                  key={index}
                  variant="outline"
                  className={`text-sm py-1 px-3 ${darkMode ? "border-slate-600 text-slate-300" : ""}`}
                >
                  {cat._id}: <span className="font-bold ml-1">{cat.views}</span>
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Top Articles Table */}
        <div className={`rounded-xl border overflow-hidden ${darkMode ? "bg-slate-800 border-slate-700" : "bg-[#070B12] border-slate-200"}`}>
          <div className="p-4 border-b border-slate-200 dark:border-slate-700">
            <h3 className={`font-semibold ${darkMode ? "text-white" : "text-slate-900"}`}>
              Top Performing Articles
            </h3>
          </div>
          <Table>
            <TableHeader>
              <TableRow className={darkMode ? "bg-slate-700/50" : "bg-slate-50"}>
                <TableHead className="w-8">#</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Category</TableHead>
                <TableHead className="text-right">Views</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {articles.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8 text-slate-500">
                    No data yet
                  </TableCell>
                </TableRow>
              ) : (
                articles.slice(0, 10).map((article, index) => (
                  <TableRow key={article.id}>
                    <TableCell className={`font-medium ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                      {index + 1}
                    </TableCell>
                    <TableCell>
                      <p className={`font-medium line-clamp-1 ${darkMode ? "text-white" : "text-slate-900"}`}>
                        {article.title}
                      </p>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className={darkMode ? "border-slate-600" : ""}>
                        {article.category}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <span className={`font-bold ${article.view_count > 0 ? "text-green-600" : darkMode ? "text-slate-500" : "text-slate-400"}`}>
                        {formatNumber(article.view_count)}
                      </span>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}

export { AnalyticsDashboard };
