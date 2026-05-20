import { useState, useContext, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, AppContext } from "../App";
import { toast } from "sonner";
import {
  Rocket, Phone, Mail, User, Lightbulb, FileText, Video,
  CheckCircle, Loader2, Upload, Award, Users, Target, Zap,
  Trophy, MapPin, ArrowRight, Share2
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";

export default function StartupApply() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [pdfUploading, setPdfUploading] = useState(false);
  const [videoUploading, setVideoUploading] = useState(false);
  const pdfInputRef = useRef(null);
  const videoInputRef = useRef(null);

  const [form, setForm] = useState({
    name: "",
    mobile: "",
    email: "",
    age: "",
    colony: "",
    area: "",
    city: "Hyderabad",
    is_woman_founder: false,
    idea: "",
    pitch_pdf_url: "",
    pitch_video_url: "",
  });

  const handleShareProgram = () => {
    // Share the branded mintstreet.in URL so the unfurl card shows the Mint Street domain.
    const shareUrl = "https://www.mintstreet.in/startup-apply";
    const shareTitle = "Hyderabad's Next 100 Startups · Mint Street × B The Change";
    const shareText = `${shareTitle}\n\nApply for up to ₹10L startup tech support. 100 founders selected. 50% reserved for women.\n\n${shareUrl}`;
    if (navigator.share) {
      navigator.share({ title: shareTitle, text: shareText, url: shareUrl }).catch(() => {});
    } else {
      window.open(`https://wa.me/?text=${encodeURIComponent(shareText)}`, "_blank");
    }
  };

  const handlePdfUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 15 * 1024 * 1024) {
      toast.error("PDF must be under 15MB");
      return;
    }
    try {
      setPdfUploading(true);
      const fd = new FormData();
      fd.append("file", file);
      const { data } = await axios.post(`${API}/upload/document`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setForm((p) => ({ ...p, pitch_pdf_url: data.url }));
      toast.success("Pitch deck uploaded");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally {
      setPdfUploading(false);
    }
  };

  const handleVideoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 50 * 1024 * 1024) {
      toast.error("Video must be under 50MB");
      return;
    }
    try {
      setVideoUploading(true);
      const fd = new FormData();
      fd.append("file", file);
      const { data } = await axios.post(`${API}/upload/video`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setForm((p) => ({ ...p, pitch_video_url: data.url }));
      toast.success("Pitch video uploaded");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally {
      setVideoUploading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.mobile || !form.email || !form.idea) {
      toast.error("Please fill name, mobile, email, and idea");
      return;
    }
    if (form.mobile.length !== 10) {
      toast.error("Mobile must be exactly 10 digits");
      return;
    }
    if (form.idea.trim().length < 30) {
      toast.error("Please describe your idea in at least 30 characters");
      return;
    }
    try {
      setSubmitting(true);
      const payload = {
        ...form,
        city: (form.city || "").trim() || "Hyderabad",
        age: form.age ? parseInt(form.age, 10) : null,
      };
      await axios.post(`${API}/startup/apply`, payload);
      setSubmitted(true);
      toast.success("Application submitted!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Submission failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div data-testid="startup-success-page" className={`min-h-screen flex items-center justify-center px-4 ${darkMode ? "bg-slate-900" : "bg-gradient-to-br from-orange-50 via-amber-50 to-rose-50"}`}>
        <div className={`max-w-md w-full rounded-3xl p-8 text-center border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-orange-200 shadow-xl"}`}>
          <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-5 shadow-lg shadow-emerald-500/30">
            <CheckCircle size={40} className="text-white" />
          </div>
          <h1 className={`text-2xl font-bold mb-3 ${darkMode ? "text-white" : "text-slate-900"}`}>Application Received!</h1>
          <p className={`text-sm leading-relaxed mb-6 ${darkMode ? "text-slate-300" : "text-slate-600"}`}>
            Thank you, <strong>{form.name}</strong>. Your startup application is in. Our team will review your idea and reach out within <strong>7-10 days</strong> on <strong>+91 {form.mobile}</strong>.
          </p>
          <Button
            data-testid="back-to-home-btn"
            onClick={() => navigate("/")}
            className="w-full bg-orange-500 hover:bg-orange-600 text-white"
          >
            Back to Home
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div data-testid="startup-apply-page" className={`min-h-screen pb-24 ${darkMode ? "bg-slate-950" : "bg-white"}`}>
      {/* ===== Compact Hero Card ===== */}
      <section className={`px-4 pt-5 pb-2 ${darkMode ? "bg-slate-950" : "bg-white"}`}>
        <div className="max-w-2xl mx-auto">
          <div className={`relative overflow-hidden rounded-2xl border ${darkMode ? "bg-slate-900 border-slate-800" : "bg-slate-50 border-slate-200"}`}>
            {/* Top orange accent line */}
            <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-orange-500 via-orange-400 to-amber-400" />
            {/* Side dot pattern */}
            <div
              className="absolute right-0 top-0 bottom-0 w-24 opacity-[0.4] pointer-events-none"
              style={{
                backgroundImage: `radial-gradient(${darkMode ? "rgba(251,146,60,0.25)" : "rgba(234,88,12,0.18)"} 1px, transparent 1px)`,
                backgroundSize: "14px 14px",
                maskImage: "linear-gradient(to left, black, transparent)",
                WebkitMaskImage: "linear-gradient(to left, black, transparent)",
              }}
            />

            <div className="relative px-5 py-5 sm:px-6 sm:py-6">
              {/* Partners badge */}
              <div className="flex items-center gap-2 mb-3">
                <span className={`inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[0.15em] ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                  Mint Street
                  <span className="text-orange-500 font-black">×</span>
                  B The Change
                </span>
              </div>

              {/* Headline — compact */}
              <h1 className={`font-black tracking-tight leading-[1.05] ${darkMode ? "text-white" : "text-slate-900"}`}>
                <span className={`block text-base sm:text-lg font-medium mb-0.5 ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                  Hyderabad's Next
                </span>
                <span className="block text-3xl sm:text-4xl">
                  <span className="relative inline-block">
                    <span className="relative z-10">100</span>
                    <span className="absolute left-0 right-0 bottom-0.5 h-2 bg-orange-400/45 -z-0" aria-hidden />
                  </span>{" "}
                  Startups
                </span>
              </h1>

              {/* Compact lede + stats inline */}
              <p className={`mt-3 text-xs sm:text-sm leading-relaxed ${darkMode ? "text-slate-300" : "text-slate-600"}`}>
                Selecting 100 young Hyderabad founders. Up to <strong className={darkMode ? "text-white" : "text-slate-900"}>₹10 lakh</strong> of product development support per founder.
              </p>

              {/* Inline stat row — compact pills */}
              <div className="mt-4 flex flex-wrap gap-1.5">
                <Pill darkMode={darkMode} label="₹100Cr Vision" />
                <Pill darkMode={darkMode} label="₹10L per founder" />
                <Pill darkMode={darkMode} label="50% women reserved" />
              </div>

              {/* Live status + Share */}
              <div className="mt-4 flex items-center justify-between gap-2 flex-wrap">
                <div className="flex items-center gap-2">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
                  </span>
                  <span className={`text-[11px] font-semibold ${darkMode ? "text-emerald-400" : "text-emerald-600"}`}>
                    Applications open
                  </span>
                  <span className={`text-[11px] ${darkMode ? "text-slate-500" : "text-slate-400"}`}>·</span>
                  <span className={`text-[11px] ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                    Limited to 100 seats
                  </span>
                </div>
                <button
                  data-testid="share-startup-program-btn"
                  onClick={handleShareProgram}
                  className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-semibold transition-colors ${
                    darkMode
                      ? "bg-slate-800 text-orange-400 hover:bg-slate-700 border border-slate-700"
                      : "bg-white text-orange-600 hover:bg-orange-50 border border-orange-200"
                  }`}
                >
                  <Share2 size={11} />
                  Share
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-2xl mx-auto px-4 pt-6">
        {/* Pitch Card */}
        <div className={`rounded-2xl p-5 mb-5 border shadow-sm ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
          <p className={`text-base font-semibold mb-2 ${darkMode ? "text-white" : "text-slate-900"}`}>
            Have a startup idea but don't know how to build it?
          </p>
          <p className={`text-sm leading-relaxed ${darkMode ? "text-slate-300" : "text-slate-600"}`}>
            We're selecting <strong>100 young founders</strong> from Hyderabad and turning their ideas into real, technology-ready startups, with <strong>up to ₹10 lakh worth of product development support</strong> per startup.
          </p>
          <p className={`mt-3 text-sm font-bold ${darkMode ? "text-orange-400" : "text-orange-600"}`}>
            You bring the idea. We build the product.
          </p>
        </div>

        {/* Who Can Apply */}
        <SectionCard darkMode={darkMode} icon={<Users size={18} />} title="Who Can Apply?" iconBg="bg-blue-500">
          <ul className="space-y-1.5 text-sm">
            <Bullet darkMode={darkMode}>Youth aged below 30 years</Bullet>
            <Bullet darkMode={darkMode}>Students, graduates, or early-stage entrepreneurs</Bullet>
            <Bullet darkMode={darkMode}>Individuals with a startup idea (no tech background needed)</Bullet>
            <Bullet darkMode={darkMode}>First-time founders are strongly encouraged</Bullet>
          </ul>
          <div className={`mt-3 p-2.5 rounded-lg text-xs font-semibold flex items-center gap-2 ${darkMode ? "bg-pink-900/30 text-pink-200" : "bg-pink-50 text-pink-700"}`}>
            <Award size={14} /> 50% of seats reserved for women founders
          </div>
        </SectionCard>

        {/* What You Get */}
        <SectionCard darkMode={darkMode} icon={<Trophy size={18} />} title="What You Get" iconBg="bg-emerald-500">
          <ul className="space-y-1.5 text-sm">
            <Bullet darkMode={darkMode}>Complete tech development (app / website / AI product)</Bullet>
            <Bullet darkMode={darkMode}>UI/UX + branding support</Bullet>
            <Bullet darkMode={darkMode}>MVP to launch-ready product</Bullet>
            <Bullet darkMode={darkMode}>Mentorship from IIM alumni &amp; startup experts</Bullet>
            <Bullet darkMode={darkMode}>Pitch deck + investor readiness</Bullet>
            <Bullet darkMode={darkMode}>Access to network, advisors &amp; demo day</Bullet>
          </ul>
        </SectionCard>

        {/* What We Look For */}
        <SectionCard darkMode={darkMode} icon={<Target size={18} />} title="What We Look For" iconBg="bg-purple-500">
          <ul className="space-y-1.5 text-sm">
            <Bullet darkMode={darkMode}>Strong, clear idea</Bullet>
            <Bullet darkMode={darkMode}>Problem-solving mindset</Bullet>
            <Bullet darkMode={darkMode}>Commitment to build</Bullet>
            <Bullet darkMode={darkMode}>Willingness to execute</Bullet>
          </ul>
          <p className={`mt-2 text-xs italic ${darkMode ? "text-slate-400" : "text-slate-500"}`}>(No need for funding, team, or coding skills)</p>
        </SectionCard>

        {/* How It Works */}
        <SectionCard darkMode={darkMode} icon={<Zap size={18} />} title="How It Works" iconBg="bg-orange-500">
          <ol className="space-y-2 text-sm">
            {["Apply with your idea", "Get shortlisted & interviewed", "Selected founders enter the accelerator", "We build your product with you", "You launch, scale, or raise funding"].map((step, i) => (
              <li key={i} className={`flex items-start gap-2.5 ${darkMode ? "text-slate-300" : "text-slate-700"}`}>
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-orange-500 text-white text-[10px] font-bold flex items-center justify-center mt-0.5">{i + 1}</span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </SectionCard>

        {/* Application Form */}
        <div id="apply-form" className={`rounded-2xl p-5 mb-6 border-2 ${darkMode ? "bg-slate-800 border-orange-500/40" : "bg-white border-orange-300 shadow-lg"}`}>
          <div className="flex items-center gap-2.5 mb-4">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center text-white">
              <Rocket size={18} />
            </div>
            <div>
              <h2 className={`font-bold text-lg ${darkMode ? "text-white" : "text-slate-900"}`}>Apply Now</h2>
              <p className={`text-xs ${darkMode ? "text-slate-400" : "text-slate-500"}`}>Limited to 100 founders. Slots fill fast.</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <FieldRow icon={<User size={14} />} label="Full Name *" darkMode={darkMode}>
              <Input data-testid="startup-name-input" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} placeholder="Your name" className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""} />
            </FieldRow>

            <FieldRow icon={<Phone size={14} />} label="Mobile Number *" darkMode={darkMode}>
              <Input
                data-testid="startup-mobile-input"
                value={form.mobile}
                onChange={(e) => setForm((p) => ({ ...p, mobile: e.target.value.replace(/\D/g, "").slice(0, 10) }))}
                placeholder="9876543210"
                maxLength={10}
                className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
              />
            </FieldRow>

            <FieldRow icon={<Mail size={14} />} label="Email *" darkMode={darkMode}>
              <Input data-testid="startup-email-input" type="email" value={form.email} onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))} placeholder="you@example.com" className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""} />
            </FieldRow>

            <div className="grid grid-cols-2 gap-3">
              <FieldRow icon={<User size={14} />} label="Age" darkMode={darkMode}>
                <Input data-testid="startup-age-input" type="number" min="16" max="35" value={form.age} onChange={(e) => setForm((p) => ({ ...p, age: e.target.value }))} placeholder="24" className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""} />
              </FieldRow>
              <FieldRow icon={<MapPin size={14} />} label="City" darkMode={darkMode}>
                <Input data-testid="startup-city-input" value={form.city} onChange={(e) => setForm((p) => ({ ...p, city: e.target.value }))} placeholder="Hyderabad" className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""} />
              </FieldRow>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <FieldRow icon={<MapPin size={14} />} label="Colony / Locality" darkMode={darkMode}>
                <Input data-testid="startup-colony-input" value={form.colony} onChange={(e) => setForm((p) => ({ ...p, colony: e.target.value }))} placeholder="e.g. Banjara Hills" className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""} />
              </FieldRow>
              <FieldRow icon={<MapPin size={14} />} label="Area / Zone" darkMode={darkMode}>
                <Input data-testid="startup-area-input" value={form.area} onChange={(e) => setForm((p) => ({ ...p, area: e.target.value }))} placeholder="e.g. Jubilee Hills" className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""} />
              </FieldRow>
            </div>

            <label className={`flex items-center gap-2 text-sm cursor-pointer ${darkMode ? "text-slate-300" : "text-slate-700"}`}>
              <input
                data-testid="startup-woman-checkbox"
                type="checkbox"
                checked={form.is_woman_founder}
                onChange={(e) => setForm((p) => ({ ...p, is_woman_founder: e.target.checked }))}
                className="w-4 h-4 accent-pink-500"
              />
              I am a woman founder (50% seats reserved)
            </label>

            <FieldRow icon={<Lightbulb size={14} />} label="Tech Business Idea *" darkMode={darkMode} hint="Min. 30 characters. Describe the problem, your solution, and target users.">
              <Textarea
                data-testid="startup-idea-input"
                value={form.idea}
                onChange={(e) => setForm((p) => ({ ...p, idea: e.target.value }))}
                placeholder="My startup idea is..."
                rows={5}
                className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
              />
              <p className={`text-[11px] mt-1 text-right ${form.idea.length >= 30 ? "text-emerald-500" : darkMode ? "text-slate-500" : "text-slate-400"}`}>{form.idea.length}/30 min</p>
            </FieldRow>

            {/* PDF Upload */}
            <div>
              <Label className={`text-sm ${darkMode ? "text-slate-200" : ""}`}><FileText size={14} className="inline mr-1.5" />Pitch Deck (PDF, optional)</Label>
              <input ref={pdfInputRef} type="file" accept=".pdf,.doc,.docx" onChange={handlePdfUpload} className="hidden" data-testid="startup-pdf-input" />
              <button
                type="button"
                onClick={() => pdfInputRef.current?.click()}
                disabled={pdfUploading}
                className={`mt-1.5 w-full px-4 py-3 rounded-lg border-2 border-dashed text-sm font-medium flex items-center justify-center gap-2 transition-all ${
                  form.pitch_pdf_url
                    ? darkMode ? "border-emerald-500 bg-emerald-500/10 text-emerald-300" : "border-emerald-400 bg-emerald-50 text-emerald-700"
                    : darkMode ? "border-slate-600 text-slate-300 hover:border-orange-500" : "border-slate-300 text-slate-600 hover:border-orange-400"
                }`}
              >
                {pdfUploading ? <><Loader2 size={16} className="animate-spin" /> Uploading...</> : form.pitch_pdf_url ? <><CheckCircle size={16} /> Pitch deck uploaded. Click to replace</> : <><Upload size={16} /> Upload Pitch Deck (PDF, max 15MB)</>}
              </button>
            </div>

            {/* Video Upload */}
            <div>
              <Label className={`text-sm ${darkMode ? "text-slate-200" : ""}`}><Video size={14} className="inline mr-1.5" />1-Minute Pitch Video (optional)</Label>
              <input ref={videoInputRef} type="file" accept="video/*" onChange={handleVideoUpload} className="hidden" data-testid="startup-video-input" />
              <button
                type="button"
                onClick={() => videoInputRef.current?.click()}
                disabled={videoUploading}
                className={`mt-1.5 w-full px-4 py-3 rounded-lg border-2 border-dashed text-sm font-medium flex items-center justify-center gap-2 transition-all ${
                  form.pitch_video_url
                    ? darkMode ? "border-emerald-500 bg-emerald-500/10 text-emerald-300" : "border-emerald-400 bg-emerald-50 text-emerald-700"
                    : darkMode ? "border-slate-600 text-slate-300 hover:border-orange-500" : "border-slate-300 text-slate-600 hover:border-orange-400"
                }`}
              >
                {videoUploading ? <><Loader2 size={16} className="animate-spin" /> Uploading...</> : form.pitch_video_url ? <><CheckCircle size={16} /> Video uploaded. Click to replace</> : <><Upload size={16} /> Upload 1-min Video Pitch (max 50MB)</>}
              </button>
            </div>

            <Button
              type="submit"
              data-testid="startup-submit-btn"
              disabled={submitting || pdfUploading || videoUploading}
              className="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white py-6 text-base font-bold shadow-lg shadow-orange-500/30"
            >
              {submitting ? (
                <><Loader2 size={18} className="animate-spin mr-2" /> Submitting...</>
              ) : (
                <><Rocket size={18} className="mr-2" /> Submit My Application <ArrowRight size={18} className="ml-2" /></>
              )}
            </Button>

            <p className={`text-[11px] text-center ${darkMode ? "text-slate-500" : "text-slate-400"}`}>
              By applying, you consent to be contacted by Mint Street &amp; B The Change regarding your application.
            </p>
          </form>
        </div>

        {/* Deadline */}
        <div className={`rounded-xl p-4 mb-6 text-center border ${darkMode ? "bg-amber-900/20 border-amber-700/40" : "bg-amber-50 border-amber-200"}`}>
          <p className={`text-sm font-semibold ${darkMode ? "text-amber-200" : "text-amber-800"}`}>
            ⏰ Limited to 100 founders only. Applications close once slots are filled.
          </p>
        </div>
      </div>
    </div>
  );
}

const Pill = ({ darkMode, label }) => (
  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-semibold border ${
    darkMode
      ? "bg-slate-800 border-slate-700 text-orange-300"
      : "bg-white border-orange-200 text-orange-700"
  }`}>
    {label}
  </span>
);

const SectionCard = ({ darkMode, icon, title, iconBg, children }) => (
  <div className={`rounded-2xl p-5 mb-4 border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200 shadow-sm"}`}>
    <div className="flex items-center gap-2.5 mb-3">
      <div className={`w-8 h-8 rounded-lg ${iconBg} text-white flex items-center justify-center flex-shrink-0`}>{icon}</div>
      <h3 className={`font-bold text-base ${darkMode ? "text-white" : "text-slate-900"}`}>{title}</h3>
    </div>
    <div className={darkMode ? "text-slate-300" : "text-slate-700"}>{children}</div>
  </div>
);

const Bullet = ({ children, darkMode }) => (
  <li className="flex items-start gap-2">
    <span className={`flex-shrink-0 w-1.5 h-1.5 rounded-full mt-1.5 ${darkMode ? "bg-orange-400" : "bg-orange-500"}`} />
    <span>{children}</span>
  </li>
);

const FieldRow = ({ icon, label, darkMode, hint, children }) => (
  <div className="space-y-1.5">
    <Label className={`text-sm ${darkMode ? "text-slate-200" : "text-slate-700"}`}>
      <span className="inline-flex items-center gap-1.5">{icon} {label}</span>
    </Label>
    {children}
    {hint && <p className={`text-[11px] ${darkMode ? "text-slate-500" : "text-slate-400"}`}>{hint}</p>}
  </div>
);

export { StartupApply };
