import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../App";
import { User, Phone, Moon, Sun, Globe, LogOut, Shield, UserPlus, ChevronRight } from "lucide-react";
import { Button } from "../components/ui/button";

export default function ProfilePage() {
  const { darkMode, toggleDarkMode, language, toggleLanguage, user, isLoggedIn, isAdmin, handleLogout } = useContext(AppContext);
  const navigate = useNavigate();
  const phone = localStorage.getItem("userPhone");

  return (
    <div data-testid="profile-page" className={`min-h-screen pb-24 ${darkMode ? "bg-slate-900" : "bg-slate-50"}`}>
      {/* Profile Header */}
      <div className="bg-gradient-to-br from-orange-500 to-orange-600 px-6 pt-8 pb-12">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center border-2 border-white/40">
            <User size={28} className="text-white" />
          </div>
          <div>
            <h1 className="text-white font-bold text-xl" data-testid="profile-name">
              {user?.name || (isLoggedIn ? "Reporter" : "Guest User")}
            </h1>
            {phone ? (
              <p className="text-white/80 text-sm flex items-center gap-1.5 mt-0.5">
                <Phone size={14} /> +91 {phone}
              </p>
            ) : (
              <p className="text-white/70 text-sm">Browsing as guest</p>
            )}
            {isAdmin && (
              <span className="inline-flex items-center gap-1 mt-1.5 px-2 py-0.5 bg-white/20 rounded-full text-white text-xs font-medium">
                <Shield size={12} /> Admin
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 -mt-6">
        {/* Settings Card */}
        <div className={`rounded-2xl shadow-sm border overflow-hidden mb-4 ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
          <h2 className={`px-4 pt-4 pb-2 text-xs font-semibold uppercase tracking-wider ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
            Settings
          </h2>

          {/* Dark Mode */}
          <button
            data-testid="toggle-darkmode-profile"
            onClick={toggleDarkMode}
            className={`w-full px-4 py-3.5 flex items-center justify-between border-b ${darkMode ? "border-slate-700 hover:bg-slate-700" : "border-slate-100 hover:bg-slate-50"} transition-colors`}
          >
            <div className="flex items-center gap-3">
              {darkMode ? <Moon size={20} className="text-yellow-400" /> : <Sun size={20} className="text-orange-500" />}
              <span className={`font-medium ${darkMode ? "text-white" : "text-slate-800"}`}>
                {darkMode ? "Dark Mode" : "Light Mode"}
              </span>
            </div>
            <div className={`w-10 h-6 rounded-full flex items-center px-0.5 transition-colors ${darkMode ? "bg-orange-500" : "bg-slate-300"}`}>
              <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform ${darkMode ? "translate-x-4" : ""}`} />
            </div>
          </button>

          {/* Language */}
          <button
            data-testid="toggle-language-profile"
            onClick={toggleLanguage}
            className={`w-full px-4 py-3.5 flex items-center justify-between ${darkMode ? "hover:bg-slate-700" : "hover:bg-slate-50"} transition-colors`}
          >
            <div className="flex items-center gap-3">
              <Globe size={20} className="text-orange-500" />
              <span className={`font-medium ${darkMode ? "text-white" : "text-slate-800"}`}>Language</span>
            </div>
            <span className={`text-sm ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
              {language === "en" ? "English" : "తెలుగు"}
            </span>
          </button>
        </div>

        {/* Actions Card */}
        <div className={`rounded-2xl shadow-sm border overflow-hidden mb-4 ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
          <h2 className={`px-4 pt-4 pb-2 text-xs font-semibold uppercase tracking-wider ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
            Quick Actions
          </h2>

          {!isLoggedIn && (
            <>
              <button
                data-testid="join-reporter-profile"
                onClick={() => navigate("/reporter/register")}
                className={`w-full px-4 py-3.5 flex items-center justify-between border-b ${darkMode ? "border-slate-700 hover:bg-slate-700" : "border-slate-100 hover:bg-slate-50"} transition-colors`}
              >
                <div className="flex items-center gap-3">
                  <UserPlus size={20} className="text-green-500" />
                  <div className="text-left">
                    <p className={`font-medium ${darkMode ? "text-white" : "text-slate-800"}`}>Become a Reporter</p>
                    <p className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>Apply to share local news</p>
                  </div>
                </div>
                <ChevronRight size={18} className={darkMode ? "text-slate-500" : "text-slate-400"} />
              </button>
              <button
                data-testid="login-reporter-profile"
                onClick={() => navigate("/reporter-login")}
                className={`w-full px-4 py-3.5 flex items-center justify-between border-b ${darkMode ? "border-slate-700 hover:bg-slate-700" : "border-slate-100 hover:bg-slate-50"} transition-colors`}
              >
                <div className="flex items-center gap-3">
                  <Phone size={20} className="text-orange-500" />
                  <span className={`font-medium ${darkMode ? "text-white" : "text-slate-800"}`}>Reporter Login</span>
                </div>
                <ChevronRight size={18} className={darkMode ? "text-slate-500" : "text-slate-400"} />
              </button>
            </>
          )}

          {isLoggedIn && (
            <button
              data-testid="reporter-dashboard-profile"
              onClick={() => navigate("/reporter/register")}
              className={`w-full px-4 py-3.5 flex items-center justify-between border-b ${darkMode ? "border-slate-700 hover:bg-slate-700" : "border-slate-100 hover:bg-slate-50"} transition-colors`}
            >
              <div className="flex items-center gap-3">
                <UserPlus size={20} className="text-green-500" />
                <span className={`font-medium ${darkMode ? "text-white" : "text-slate-800"}`}>Reporter Dashboard</span>
              </div>
              <ChevronRight size={18} className={darkMode ? "text-slate-500" : "text-slate-400"} />
            </button>
          )}

          {isAdmin && (
            <button
              data-testid="admin-panel-profile"
              onClick={() => navigate("/admin")}
              className={`w-full px-4 py-3.5 flex items-center justify-between border-b ${darkMode ? "border-slate-700 hover:bg-slate-700" : "border-slate-100 hover:bg-slate-50"} transition-colors`}
            >
              <div className="flex items-center gap-3">
                <Shield size={20} className="text-orange-500" />
                <span className={`font-medium ${darkMode ? "text-white" : "text-slate-800"}`}>Admin Panel</span>
              </div>
              <ChevronRight size={18} className={darkMode ? "text-slate-500" : "text-slate-400"} />
            </button>
          )}

          {isLoggedIn && (
            <button
              data-testid="logout-profile"
              onClick={handleLogout}
              className={`w-full px-4 py-3.5 flex items-center justify-between ${darkMode ? "hover:bg-slate-700" : "hover:bg-slate-50"} transition-colors`}
            >
              <div className="flex items-center gap-3">
                <LogOut size={20} className="text-red-500" />
                <span className="font-medium text-red-500">Logout</span>
              </div>
            </button>
          )}
        </div>

        {/* App Info */}
        <div className="text-center py-4">
          <img src="/tvr-logo.png" alt="Mint Street" className="h-8 w-auto mx-auto mb-2 opacity-50" />
          <p className={`text-xs ${darkMode ? "text-slate-600" : "text-slate-400"}`}>
            Mint Street v1.0
          </p>
        </div>
      </div>
    </div>
  );
}

export { ProfilePage };
