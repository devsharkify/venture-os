import { useState, useEffect, useContext } from "react";
import { AppContext } from "../App";
import { Eye } from "lucide-react";

/**
 * Generates a realistic mocked visitor count based on time of day.
 * Pattern: 8AM start ~9,000, peaks at ~105,000 by 10PM, dips overnight.
 * Base of 72,000+ during active hours.
 */
function getMockedVisitors() {
  const now = new Date();
  const hour = now.getHours();
  const minute = now.getMinutes();
  const fractionalHour = hour + minute / 60;

  // Daily pattern: low overnight, ramp 8AM→10PM
  // Using a bell curve centered around 9PM (21:00)
  let base;
  if (fractionalHour < 6) {
    // Midnight-6AM: low traffic (2K-5K)
    base = 2000 + Math.floor(fractionalHour * 500);
  } else if (fractionalHour < 8) {
    // 6AM-8AM: ramp up (5K-9K)
    const t = (fractionalHour - 6) / 2;
    base = 5000 + Math.floor(t * 4000);
  } else if (fractionalHour < 22) {
    // 8AM-10PM: main traffic (9K→105K)
    // Linear-ish growth with some acceleration in evening
    const t = (fractionalHour - 8) / 14; // 0 to 1 over 14 hours
    const curved = Math.pow(t, 1.3); // Slightly accelerating
    base = 9000 + Math.floor(curved * 96000);
  } else {
    // 10PM-midnight: slight decline (105K→85K)
    const t = (fractionalHour - 22) / 2;
    base = 105000 - Math.floor(t * 20000);
  }

  // Add some randomness (±3%)
  const jitter = base * 0.03 * (Math.random() - 0.5);
  return Math.floor(base + jitter);
}

function formatCount(num) {
  if (num >= 100000) return `${(num / 1000).toFixed(1)}K`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

export const VisitorCounter = () => {
  const { darkMode } = useContext(AppContext);
  const [count, setCount] = useState(getMockedVisitors);

  useEffect(() => {
    // Update every 8-15 seconds with small increments
    const interval = setInterval(() => {
      setCount(prev => {
        const target = getMockedVisitors();
        // Smooth towards target with small steps
        const diff = target - prev;
        const step = Math.ceil(Math.abs(diff) * 0.15) * Math.sign(diff);
        return prev + step + Math.floor(Math.random() * 5);
      });
    }, 8000 + Math.random() * 7000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      data-testid="visitor-counter"
      className={`fixed left-3 bottom-20 z-40 flex items-center gap-2 px-3 py-2 rounded-lg border backdrop-blur-md transition-all ${
        darkMode
          ? "bg-[#070B12]/80 border-[#1C2840]/60 text-[#A0B4CC]"
          : "bg-white/80 border-[#1C2840]/80 text-[#A0B4CC] shadow-sm"
      }`}
    >
      <div className="relative">
        <Eye size={14} className="text-green-500" />
        <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-[#00D9C8] rounded-full animate-pulse" />
      </div>
      <div className="flex flex-col">
        <span className="text-xs font-bold tabular-nums leading-none">{formatCount(count)}</span>
        <span className={`text-[9px] leading-tight ${darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"}`}>visitors</span>
      </div>
    </div>
  );
};
