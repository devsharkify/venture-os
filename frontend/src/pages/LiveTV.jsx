import { useState, useEffect, useContext } from "react";
import { AppContext } from "../App";
import { API } from "../App";
import axios from "axios";
import { Radio, Tv, X } from "lucide-react";

export default function LiveTV() {
  const { darkMode } = useContext(AppContext);
  const [channels, setChannels] = useState([]);
  const [activeChannel, setActiveChannel] = useState(null);

  useEffect(() => {
    axios.get(`${API}/live-tv`).then(r => {
      setChannels(r.data);
      if (r.data.length > 0) setActiveChannel(r.data[0]);
    }).catch(() => {});
  }, []);

  return (
    <div data-testid="live-tv-page" className={`min-h-screen ${darkMode ? "bg-[#070B12]" : "bg-[#0A0E18]"}`}>
      {/* Live Banner */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 py-3 px-4 sticky top-14 z-20">
        <div className="max-w-7xl mx-auto flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-[#070B12] rounded-full animate-pulse" />
            <Tv size={20} className="text-white" />
          </div>
          <h1 className="text-white font-bold text-lg">Live TV</h1>
          <span className="ml-auto text-white/70 text-xs">{channels.length} channels</span>
        </div>
      </div>

      {/* Player */}
      {activeChannel ? (
        <div className="max-w-5xl mx-auto">
          <div className="relative w-full aspect-video bg-black">
            <iframe
              data-testid="live-player"
              src={`https://www.youtube.com/embed/${activeChannel.youtube_id}?autoplay=1&mute=1`}
              title={activeChannel.name}
              className="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
          <div className={`px-4 py-3 border-b ${darkMode ? "bg-[#0D1321] border-[#1C2840]" : "bg-[#070B12] border-[#1C2840]"}`}>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-2 py-1 bg-red-600 rounded text-white text-xs font-bold">
                <Radio size={12} /> LIVE
              </div>
              <h2 className={`font-semibold text-lg ${darkMode ? "text-white" : "text-[#E2EAF6]"}`}>
                {activeChannel.name}
              </h2>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20">
          <Tv size={48} className={darkMode ? "text-[#7A90A8]" : "text-[#7A90A8]"} />
          <p className={`mt-4 ${darkMode ? "text-[#7A90A8]" : "text-[#5A7090]"}`}>
            No live channels available
          </p>
        </div>
      )}

      {/* Channel List */}
      {channels.length > 1 && (
        <div className="max-w-5xl mx-auto px-4 py-4">
          <h3 className={`text-sm font-semibold mb-3 ${darkMode ? "text-[#7A90A8]" : "text-[#5A7090]"}`}>
            OTHER CHANNELS
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {channels.filter(c => c.id !== activeChannel?.id).map(ch => (
              <button
                key={ch.id}
                data-testid={`channel-${ch.id}`}
                onClick={() => setActiveChannel(ch)}
                className={`rounded-xl overflow-hidden border transition-all hover:scale-[1.02] ${
                  darkMode ? "bg-[#0D1321] border-[#1C2840] hover:border-[#2D7AFF]" : "bg-[#070B12] border-[#1C2840] hover:border-orange-400"
                }`}
              >
                <div className="relative aspect-video">
                  <img
                    src={`https://img.youtube.com/vi/${ch.youtube_id}/hqdefault.jpg`}
                    alt={ch.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2 left-2 flex items-center gap-1 px-1.5 py-0.5 bg-red-600 rounded text-white text-[10px] font-bold">
                    <div className="w-1.5 h-1.5 bg-[#070B12] rounded-full animate-pulse" /> LIVE
                  </div>
                </div>
                <div className="p-2">
                  <p className={`text-sm font-medium truncate ${darkMode ? "text-white" : "text-[#E2EAF6]"}`}>
                    {ch.name}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export { LiveTV };
