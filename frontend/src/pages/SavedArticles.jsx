import { useContext } from "react";
import { AppContext } from "../App";
import { NewsCard } from "../components/NewsCard";
import { Bookmark, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";

export default function SavedArticles() {
  const { darkMode, savedArticles } = useContext(AppContext);
  const navigate = useNavigate();

  return (
    <div data-testid="saved-articles-page" className={`min-h-screen ${darkMode ? "bg-[#070B12]" : "bg-[#0A0E18]"}`}>
      {/* Header Section */}
      <div className={`border-b py-4 px-4 ${darkMode ? "bg-[#0D1321] border-[#1C2840]" : "bg-[#070B12] border-[#131B2A]"}`}>
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <Button
              variant="ghost"
              size="icon"
              data-testid="back-btn"
              onClick={() => navigate("/")}
              className={`h-9 w-9 ${darkMode ? "text-[#A0B4CC] hover:text-white" : ""}`}
            >
              <ArrowLeft size={20} />
            </Button>
            <div className="flex items-center gap-2">
              <Bookmark size={22} className="text-[#2D7AFF]" />
              <h1 className={`text-xl font-bold ${darkMode ? "text-white" : "text-[#E2EAF6]"}`}>
                Saved Articles
              </h1>
            </div>
          </div>
          <p className={`text-sm ml-12 ${darkMode ? "text-[#7A90A8]" : "text-[#5A7090]"}`}>
            {`${savedArticles.length} article${savedArticles.length !== 1 ? "s" : ""} saved`}
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-4">
        {/* Empty State */}
        {savedArticles.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 ${darkMode ? "bg-[#0D1321]" : "bg-[#131B2A]"}`}>
              <Bookmark size={32} className={darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"} />
            </div>
            <h3 className={`text-lg font-semibold mb-2 ${darkMode ? "text-white" : "text-[#A0B4CC]"}`}>
              No saved articles
            </h3>
            <p className={`text-sm text-center max-w-xs ${darkMode ? "text-[#7A90A8]" : "text-[#5A7090]"}`}>
              Tap the bookmark icon on any article to save it for later
            </p>
            <Button
              data-testid="browse-news-btn"
              onClick={() => navigate("/")}
              className="mt-6 bg-[#2D7AFF] hover:bg-[#1A5FCC]"
            >
              Browse News
            </Button>
          </div>
        )}

        {/* Saved Articles Grid */}
        {savedArticles.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {savedArticles.map((article, index) => (
              <NewsCard key={article.id} article={article} index={index} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export { SavedArticles };
