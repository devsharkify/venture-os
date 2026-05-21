import { useState, useEffect, useCallback, createContext } from "react";
import { HelmetProvider } from "react-helmet-async";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { registerServiceWorker } from "./utils/notifications";

// Components
import { Header } from "./components/Header";
import { BottomNav } from "./components/BottomNav";
import { NewsFeed } from "./pages/NewsFeed";
import { SavedArticles } from "./pages/SavedArticles";
import { AdminPanel } from "./pages/AdminPanel";
import { ArticleModal } from "./components/ArticleModal";
import { ShortsPlayer } from "./pages/SwipeReader";
import { VideoNews } from "./pages/VideoNews";
import LiveTV from "./pages/LiveTV";
import { ReporterRegister } from "./pages/ReporterRegister";
import { ReporterDashboard } from "./pages/ReporterDashboard";
import LoginPage from "./pages/LoginPage";
import { AnalyticsDashboard } from "./pages/AnalyticsDashboard";
import EpaperPage from "./pages/EpaperPage";
import ArticlePage from "./pages/ArticlePage";
import AgentsDashboard from "./pages/AgentsDashboard";
import StartupApply from "./pages/StartupApply";
import { VisitorCounter } from "./components/VisitorCounter";
import { Footer } from "./components/Footer";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfService from "./pages/TermsOfService";
import CookiePolicy from "./pages/CookiePolicy";
import Disclaimer from "./pages/Disclaimer";
import AdvertisePage from "./pages/AdvertisePage";
import WriteForUs from "./pages/WriteForUs";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://venture-os-production.up.railway.app";
export const API = `${BACKEND_URL}/api`;

// Attach admin phone header automatically on every request made by the logged-in admin.
// Backend routes gated with require_admin read X-Admin-Phone (or admin_phone query param).
axios.interceptors.request.use((config) => {
  const phone = localStorage.getItem("userPhone");
  if (phone) {
    config.headers = config.headers || {};
    config.headers["X-Admin-Phone"] = phone;
  }
  return config;
});

export const AppContext = createContext();

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

function AppContent() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    return saved ? JSON.parse(saved) : false;
  });
  const [isLoggedIn, setIsLoggedIn] = useState(() => !!localStorage.getItem("userPhone"));
  const [isAdmin, setIsAdmin] = useState(() => localStorage.getItem("userPhone") === "7386917770");
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });
  const [categories, setCategories] = useState({});
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [articlesList, setArticlesList] = useState([]);
  const [articleIndex, setArticleIndex] = useState(-1);
  const [savedArticles, setSavedArticles] = useState(() => {
    const saved = localStorage.getItem("savedArticles");
    return saved ? JSON.parse(saved) : [];
  });
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("darkMode", JSON.stringify(darkMode));
  }, [darkMode]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get(`${API}/news/categories`);
        setCategories(response.data.categories);
      } catch (e) {
        console.error("Failed to fetch categories:", e);
      }
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    localStorage.setItem("savedArticles", JSON.stringify(savedArticles));
  }, [savedArticles]);

  // Service worker only (no breaking news popup)
  useEffect(() => {
    registerServiceWorker();
  }, []);

  const toggleDarkMode = useCallback(() => {
    setDarkMode(prev => !prev);
  }, []);

  const handleLoginSuccess = useCallback((userData, isAdminUser) => {
    setUser(userData);
    setIsLoggedIn(true);
    setIsAdmin(isAdminUser || false);
    if (isAdminUser) {
      navigate("/admin");
    } else {
      // Check if reporter exists
      const phone = userData.phone;
      axios.get(`${API}/reporter/check/${phone}`).then(r => {
        if (r.data && r.data.registered && r.data.id) {
          navigate(`/reporter/dashboard/${r.data.id}`);
        } else {
          navigate("/reporter/register");
        }
      }).catch(() => navigate("/reporter/register"));
    }
  }, [navigate]);

  const handleLogout = useCallback(() => {
    localStorage.removeItem("user");
    localStorage.removeItem("userPhone");
    setUser(null);
    setIsLoggedIn(false);
    setIsAdmin(false);
    navigate("/");
  }, [navigate]);

  const saveArticle = useCallback((article) => {
    setSavedArticles(prev => {
      const exists = prev.some(a => a.id === article.id);
      if (exists) {
        toast.success("Article removed from saved");
        return prev.filter(a => a.id !== article.id);
      } else {
        toast.success("Article saved!");
        return [...prev, article];
      }
    });
  }, []);

  const isArticleSaved = useCallback((articleId) => {
    return savedArticles.some(a => a.id === articleId);
  }, [savedArticles]);

  const openArticle = useCallback((article, list = []) => {
    // Open as full page instead of modal
    const articleId = article._id || article.id;
    if (articleId) {
      navigate(`/news/${articleId}`);
    }
  }, [navigate]);

  const closeArticle = useCallback(() => {
    setSelectedArticle(null);
    setArticlesList([]);
    setArticleIndex(-1);
  }, []);

  const goNextArticle = useCallback(() => {
    if (articlesList.length > 0 && articleIndex < articlesList.length - 1) {
      const next = articleIndex + 1;
      setArticleIndex(next);
      setSelectedArticle(articlesList[next]);
    }
  }, [articlesList, articleIndex]);

  const goPrevArticle = useCallback(() => {
    if (articlesList.length > 0 && articleIndex > 0) {
      const prev = articleIndex - 1;
      setArticleIndex(prev);
      setSelectedArticle(articlesList[prev]);
    }
  }, [articlesList, articleIndex]);

  const contextValue = {
    darkMode, toggleDarkMode,
    categories, savedArticles, saveArticle,
    isArticleSaved, openArticle, closeArticle,
    selectedArticle, articlesList, articleIndex,
    goNextArticle, goPrevArticle,
    user, isLoggedIn, isAdmin, handleLogout
  };

  const isAdminPage = location.pathname === "/admin" || location.pathname === "/analytics" || location.pathname === "/agents";
  const isSwipeMode = false; // Keep header/nav on all pages
  const isReporterPage = location.pathname.startsWith("/reporter");
  const isLoginPage = location.pathname === "/reporter-login";
  const isLivePage = location.pathname === "/live";
  const isEpaperPage = location.pathname === "/epaper";
  const isStartupPage = location.pathname === "/startup-apply";
  const showFloatingLive = !isAdminPage && !isSwipeMode && !isReporterPage && !isLoginPage && !isLivePage && !isEpaperPage && !isStartupPage;

  // Protect admin route
  if (isAdminPage && !isAdmin) {
    return (
      <AppContext.Provider value={contextValue}>
        <div className={`min-h-screen flex items-center justify-center ${darkMode ? "dark bg-[#070B12]" : "bg-[#0A0E18]"}`}>
          <div className="text-center p-8">
            <p className="text-lg font-semibold text-[#A0B4CC] mb-2">Admin Access Required</p>
            <p className="text-sm text-[#5A7090] mb-4">Only authorized users can access the admin panel.</p>
            <button onClick={() => navigate("/")} className="text-[#2D7AFF] font-medium">Go to Home</button>
          </div>
          <Toaster position="top-center" richColors theme={darkMode ? "dark" : "light"} />
        </div>
      </AppContext.Provider>
    );
  }

  return (
    <AppContext.Provider value={contextValue}>
      <div className={`min-h-screen ${darkMode ? "dark" : ""}`} style={{ background: "var(--vos-bg)", color: "var(--vos-text)" }}>
        <ScrollToTop />
        {!isSwipeMode && !isReporterPage && !isLoginPage && <Header />}
        <main className={`${isAdminPage || isSwipeMode || isReporterPage ? "" : "safe-area-bottom"}`}>
          <Routes>
            <Route path="/" element={<NewsFeed />} />
            <Route path="/swipe" element={<ShortsPlayer />} />
            <Route path="/videos" element={<VideoNews />} />
            <Route path="/live" element={<LiveTV />} />
            <Route path="/saved" element={<SavedArticles />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route path="/reporter/register" element={<ReporterRegister />} />
            <Route path="/reporter/dashboard/:reporterId" element={<ReporterDashboard />} />
            <Route path="/reporter-login" element={<LoginPage onLoginSuccess={handleLoginSuccess} />} />
            <Route path="/epaper" element={<EpaperPage />} />
            <Route path="/news/:id" element={<ArticlePage />} />
            <Route path="/agents" element={<AgentsDashboard />} />
            <Route path="/startup-apply" element={<StartupApply />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/terms" element={<TermsOfService />} />
            <Route path="/cookie-policy" element={<CookiePolicy />} />
            <Route path="/disclaimer" element={<Disclaimer />} />
            <Route path="/advertise" element={<AdvertisePage />} />
            <Route path="/write-for-us" element={<WriteForUs />} />
          </Routes>
        </main>
        <Footer />
        {!isSwipeMode && <ArticleModal />}
        <Toaster position="top-center" richColors theme={darkMode ? "dark" : "light"} />
      </div>
    </AppContext.Provider>
  );
}

function App() {
  return (
    <HelmetProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </HelmetProvider>
  );
}

export default App;
