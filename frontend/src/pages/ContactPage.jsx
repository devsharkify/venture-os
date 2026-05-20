import { useContext, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AppContext } from "../App";

export default function ContactPage() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();

  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [toast, setToast] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: wire up to backend / mail relay. For now, stubbed.
    setToast("Thanks - we'll get back within 48 hours.");
    setForm({ name: "", email: "", subject: "", message: "" });
    setTimeout(() => setToast(""), 4000);
  };

  const inputBase = `w-full rounded-lg px-3 py-2 text-[14px] border focus:outline-none focus:ring-2 focus:ring-mint/40 ${
    darkMode
      ? "bg-slate-800 border-slate-700 text-slate-100 placeholder-slate-500"
      : "bg-white border-slate-200 text-slate-800 placeholder-slate-400"
  }`;

  return (
    <div className={`min-h-screen ${darkMode ? "bg-ink text-cream" : "bg-paper text-ink"}`}>
      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-[13px] mb-8" aria-label="Breadcrumb">
          <Link to="/" className="hover:underline text-mint">
            Home
          </Link>
          <span className={darkMode ? "text-slate-500" : "text-slate-400"}>/</span>
          <span className={darkMode ? "text-slate-300" : "text-slate-600"}>Contact</span>
        </nav>

        {/* Heading */}
        <header className="mb-10">
          <h1 className="font-display font-bold text-[36px] sm:text-[44px] leading-tight mb-4">
            Contact Mint Street
          </h1>
          <div className="w-16 h-[3px] rounded mb-5 bg-mint" />
          <p className="text-[15px] leading-relaxed text-slate-600 dark:text-slate-300">
            Tip, pitch, complaint or compliment &mdash; we read everything. The fastest route is
            email, but the form below lands in the same inbox.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          {/* Left: contact details */}
          <section
            className={`rounded-xl p-6 border ${
              darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200 shadow-sm"
            }`}
          >
            <h2 className="font-display text-[16px] font-bold mb-4 text-ink dark:text-cream">
              Reach us
            </h2>

            <div className="space-y-3 text-[14px] text-slate-600 dark:text-slate-300">
              <p>
                <span className="font-semibold text-slate-700 dark:text-slate-200 block">
                  Newsroom
                </span>
                <a href="mailto:editor@mintstreet.in" className="hover:underline text-mint">
                  editor@mintstreet.in
                </a>
              </p>
              <p>
                <span className="font-semibold text-slate-700 dark:text-slate-200 block">
                  Advertising
                </span>
                <a href="mailto:advertise@mintstreet.in" className="hover:underline text-mint">
                  advertise@mintstreet.in
                </a>
              </p>
              <p>
                <span className="font-semibold text-slate-700 dark:text-slate-200 block">
                  Careers
                </span>
                <a href="mailto:careers@mintstreet.in" className="hover:underline text-mint">
                  careers@mintstreet.in
                </a>
              </p>
              <p>
                <span className="font-semibold text-slate-700 dark:text-slate-200 block">
                  Legal
                </span>
                <a href="mailto:legal@mintstreet.in" className="hover:underline text-mint">
                  legal@mintstreet.in
                </a>
              </p>
              <p>
                <span className="font-semibold text-slate-700 dark:text-slate-200 block">
                  Phone
                </span>
                +91 40 4242 0000
              </p>
              <p>
                <span className="font-semibold text-slate-700 dark:text-slate-200 block">
                  Office
                </span>
               
                <br />
                Plot 14, HUDA Tech Park, Madhapur
                <br />
                Hyderabad &ndash; 500081
                <br />
                Also in Bengaluru
              </p>
            </div>

            <div className="mt-5 pt-5 border-t border-slate-200 dark:border-slate-700">
              <h3 className="text-[13px] font-bold mb-2 text-slate-700 dark:text-slate-200 uppercase tracking-wider">
                Follow
              </h3>
              <div className="flex flex-wrap gap-3 text-[13px]">
                <a
                  href="https://twitter.com/mintstreet_in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline text-mint"
                >
                  @mintstreet_in
                </a>
                <a
                  href="https://www.linkedin.com/company/mintstreet"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline text-mint"
                >
                  /company/mintstreet
                </a>
                <a
                  href="https://instagram.com/mintstreet.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline text-mint"
                >
                  @mintstreet.in
                </a>
              </div>
            </div>
          </section>

          {/* Right: form */}
          <section
            className={`rounded-xl p-6 border ${
              darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200 shadow-sm"
            }`}
          >
            <h2 className="font-display text-[16px] font-bold mb-4 text-ink dark:text-cream">
              Send a note
            </h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block text-[13px] font-medium mb-1 text-slate-700 dark:text-slate-200">
                  Name
                </label>
                <input
                  name="name"
                  type="text"
                  value={form.name}
                  onChange={handleChange}
                  required
                  className={inputBase}
                  placeholder="Your name"
                />
              </div>
              <div>
                <label className="block text-[13px] font-medium mb-1 text-slate-700 dark:text-slate-200">
                  Email
                </label>
                <input
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                  required
                  className={inputBase}
                  placeholder="you@example.com"
                />
              </div>
              <div>
                <label className="block text-[13px] font-medium mb-1 text-slate-700 dark:text-slate-200">
                  Subject
                </label>
                <input
                  name="subject"
                  type="text"
                  value={form.subject}
                  onChange={handleChange}
                  required
                  className={inputBase}
                  placeholder="What is this about?"
                />
              </div>
              <div>
                <label className="block text-[13px] font-medium mb-1 text-slate-700 dark:text-slate-200">
                  Message
                </label>
                <textarea
                  name="message"
                  rows={5}
                  value={form.message}
                  onChange={handleChange}
                  required
                  className={inputBase}
                  placeholder="Tell us more…"
                />
              </div>
              <button
                type="submit"
                className="inline-flex items-center justify-center px-4 py-2 rounded-lg text-[14px] font-semibold text-white bg-mint hover:opacity-90 transition"
              >
                Send message
              </button>
              {toast && (
                <p className="text-[13px] mt-2 text-mint font-medium">{toast}</p>
              )}
            </form>
          </section>
        </div>

        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-[14px] font-medium hover:underline text-mint"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Go back
        </button>
      </div>
    </div>
  );
}
