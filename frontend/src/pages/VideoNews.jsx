import { useState, useEffect, useCallback } from "react";
import { Play, RefreshCw, Youtube, Clock, ChevronRight, Users } from "lucide-react";
import { Button } from "../components/ui/button";

const API = process.env.REACT_APP_BACKEND_URL;

const formatCount = (n) => {
  if (!n) return "0";
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n.toString();
};

const timeAgo = (dateStr) => {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days}d ago`;
  return `${Math.floor(days / 7)}w ago`;
};

function ChannelPill({ ch, active, onClick }) {
  return (
    <button
      data-testid={`channel-pill-${ch.id}`}
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap border transition-all shrink-0 ${
        active
          ? "bg-red-600 text-white border-red-600 shadow-sm"
          : "bg-[#070B12] dark:bg-[#0D1321] text-[#7A90A8] dark:text-[#A0B4CC] border-[#1C2840] dark:border-[#1C2840] hover:border-red-300"
      }`}
    >
      {ch.thumbnail && <img src={ch.thumbnail} alt="" className="w-5 h-5 rounded-full" />}
      <span>{ch.name}</span>
      {ch.subscriber_count > 0 && (
        <span className={`text-[10px] ${active ? "text-white/70" : "text-[#7A90A8]"}`}>{formatCount(ch.subscriber_count)}</span>
      )}
    </button>
  );
}

export default function VideoNews() {
  const [channels, setChannels] = useState([]);
  const [videos, setVideos] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState("all");
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("videos");

  useEffect(() => {
    fetch(`${API}/api/youtube/channels`)
      .then(r => r.json())
      .then(d => setChannels(d.channels || []))
      .catch(() => {});
  }, []);

  const fetchContent = useCallback(async (channelId) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/youtube/videos?channel_id=${channelId}&max_results=12`);
      const data = await res.json();
      setVideos(data.videos || []);
    } catch (e) {
      console.error("Failed to fetch:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchContent(selectedChannel); }, [selectedChannel, fetchContent]);

  const activeChannel = channels.find(c => c.id === selectedChannel);
  const totalSubs = channels.reduce((a, c) => a + (c.subscriber_count || 0), 0);
  const totalVideos = channels.reduce((a, c) => a + (c.video_count || 0), 0);

  return (
    <div data-testid="video-news-page" className="min-h-screen bg-[#0A0E18] dark:bg-[#070B12] pb-24">
      {/* Network Banner */}
      <div className="bg-gradient-to-br from-red-700 via-red-600 to-rose-500 pt-5 pb-4 px-4 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10" style={{backgroundImage: "radial-gradient(circle at 20% 50%, white 1px, transparent 1px)", backgroundSize: "30px 30px"}} />
        <div className="max-w-5xl mx-auto relative z-10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#070B12]/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                <Youtube size={22} className="text-white" />
              </div>
              <div className="text-white">
                <h1 className="text-lg font-bold">
                  Venture OS Network
                </h1>
                <div className="flex items-center gap-3 text-xs text-white/70">
                  <span>{channels.length} channels</span>
                  <span>{formatCount(totalSubs)} total subscribers</span>
                  <span>{formatCount(totalVideos)} videos</span>
                </div>
              </div>
            </div>
          </div>

          {/* Channel pills */}
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide -mx-1 px-1">
            <ChannelPill
              ch={{ id: "all", name: "All Channels", thumbnail: "", subscriber_count: 0 }}
              active={selectedChannel === "all"}
              onClick={() => setSelectedChannel("all")}
            />
            {channels.map(ch => (
              <ChannelPill key={ch.id} ch={ch} active={selectedChannel === ch.id} onClick={() => setSelectedChannel(ch.id)} />
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-[#070B12] dark:bg-[#0D1321] border-b border-[#1C2840] dark:border-[#1C2840] sticky top-14 z-20">
        <div className="max-w-5xl mx-auto flex items-center px-4">
          {[
            { id: "videos", label: "Long Videos", icon: Play },
            { id: "channels", label: "Channels", icon: Users },
          ].map(t => (
            <button
              key={t.id}
              data-testid={`tab-${t.id}`}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.id ? "border-red-600 text-red-600" : "border-transparent text-[#5A7090] hover:text-[#A0B4CC] dark:text-[#7A90A8]"
              }`}
            >
              <t.icon size={15} /> {t.label}
            </button>
          ))}
          <div className="ml-auto">
            <Button variant="ghost" size="sm" data-testid="refresh-videos-btn" onClick={() => fetchContent(selectedChannel)} disabled={loading}>
              <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-4 py-5">
        {loading && tab !== "channels" ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <div className="w-10 h-10 border-3 border-red-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-[#5A7090]">Loading...</p>
          </div>
        ) : (
          <>
            {/* VIDEOS GRID */}
            {tab === "videos" && (
              <div data-testid="videos-section">
                {activeChannel && selectedChannel !== "all" && (
                  <div className="flex items-center gap-3 mb-4 p-3 bg-[#070B12] dark:bg-[#0D1321] rounded-xl border border-[#131B2A] dark:border-[#1C2840]">
                    {activeChannel.thumbnail && <img src={activeChannel.thumbnail} alt="" className="w-10 h-10 rounded-full" />}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm text-[#E2EAF6] dark:text-white truncate">
                        {activeChannel.name}
                      </h3>
                      <p className="text-[11px] text-[#5A7090]">{formatCount(activeChannel.subscriber_count)} subscribers</p>
                    </div>
                    <a href={`https://www.youtube.com/@${activeChannel.handle}`} target="_blank" rel="noopener noreferrer">
                      <Button size="sm" className="bg-red-600 hover:bg-red-700 text-white text-xs h-7 px-3">
                        <Youtube size={12} className="mr-1" /> Subscribe
                      </Button>
                    </a>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {videos.map(video => (
                    <div
                      key={video.id}
                      data-testid={`video-card-${video.id}`}
                      className="bg-[#070B12] dark:bg-[#0D1321] rounded-xl overflow-hidden shadow-sm border border-[#131B2A] dark:border-[#1C2840]/50 cursor-pointer group hover:shadow-md transition-all"
                      onClick={() => setSelectedVideo(video)}
                    >
                      <div className="relative aspect-video">
                        <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" loading="lazy" />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 flex items-center justify-center transition-all">
                          <div className="w-12 h-12 bg-red-600/90 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <Play size={22} className="text-white ml-0.5" fill="white" />
                          </div>
                        </div>
                      </div>
                      <div className="p-3">
                        <h4 className="font-medium text-sm text-[#E2EAF6] dark:text-white line-clamp-2 leading-snug">{video.title}</h4>
                        <div className="flex items-center gap-2 mt-2 text-[11px] text-[#5A7090]">
                          <span>{video.channel_title}</span>
                          <span className="flex items-center gap-0.5"><Clock size={10} />{timeAgo(video.published_at)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {videos.length === 0 && !loading && (
                  <div className="text-center py-16">
                    <Youtube size={40} className="text-[#A0B4CC] mx-auto mb-3" />
                    <p className="text-[#5A7090]">No videos found</p>
                  </div>
                )}
              </div>
            )}

            {/* CHANNELS LIST */}
            {tab === "channels" && (
              <div data-testid="channels-section" className="space-y-3">
                <p className="text-sm text-[#5A7090] mb-4">
                  {channels.length} channels &middot; {formatCount(totalSubs)} total subscribers
                </p>
                {channels.map((ch, i) => (
                  <div
                    key={ch.id}
                    data-testid={`channel-row-${ch.id}`}
                    className="flex items-center gap-3 p-3 bg-[#070B12] dark:bg-[#0D1321] rounded-xl border border-[#131B2A] dark:border-[#1C2840] hover:shadow-sm transition-shadow cursor-pointer"
                    onClick={() => { setSelectedChannel(ch.id); setTab("videos"); }}
                  >
                    <span className="text-xs font-bold text-[#7A90A8] w-5 text-right">{i + 1}</span>
                    <img src={ch.thumbnail} alt={ch.name} className="w-11 h-11 rounded-full border border-[#1C2840] dark:border-[#1C2840]" onError={(e) => { e.target.src = "https://via.placeholder.com/44?text=CH"; }} />
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm text-[#E2EAF6] dark:text-white truncate">
                        {ch.name}
                      </h3>
                      <div className="flex items-center gap-3 text-[11px] text-[#5A7090] mt-0.5">
                        <span>{formatCount(ch.subscriber_count)} subs</span>
                        <span>{formatCount(ch.video_count)} videos</span>
                        <span>{formatCount(ch.view_count)} views</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <a href={`https://www.youtube.com/@${ch.handle}`} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}>
                        <Button size="sm" variant="outline" className="text-red-600 border-red-200 hover:bg-red-50 text-[11px] h-7 px-2">
                          <Youtube size={12} className="mr-1" /> Subscribe
                        </Button>
                      </a>
                      <ChevronRight size={16} className="text-[#7A90A8]" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Video Player Modal */}
      {selectedVideo && (
        <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4" onClick={() => setSelectedVideo(null)}>
          <div className="w-full max-w-4xl aspect-video" onClick={e => e.stopPropagation()}>
            <iframe
              src={`https://www.youtube.com/embed/${selectedVideo.id}?autoplay=1`}
              title={selectedVideo.title}
              className="w-full h-full rounded-xl"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
          <button className="absolute top-4 right-4 text-white/70 hover:text-white text-3xl font-light" onClick={() => setSelectedVideo(null)}>
            &#x2715;
          </button>
        </div>
      )}
    </div>
  );
}

export { VideoNews };
