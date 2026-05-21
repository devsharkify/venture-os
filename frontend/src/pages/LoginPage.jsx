import { useState, useContext, useEffect } from "react";
import { AppContext } from "../App";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "../App";
import { toast } from "sonner";
import { Phone, Loader2, Shield, ChevronLeft, UserPlus } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

export default function LoginPage({ onLoginSuccess }) {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();
  const [step, setStep] = useState("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);

  const [resendCooldown, setResendCooldown] = useState(0);

  const handleSendOtp = async () => {
    if (phone.length !== 10) {
      toast.error("Enter valid 10-digit number");
      return;
    }
    try {
      setLoading(true);
      await axios.post(`${API}/auth/send-otp`, { mobile: phone, country_code: "91" });
      toast.success("OTP sent!");
      setStep("otp");
      setResendCooldown(30);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to send OTP");
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    if (resendCooldown > 0) return;
    try {
      setLoading(true);
      setOtp("");
      await axios.post(`${API}/auth/resend-otp`, { mobile: phone });
      toast.success("OTP resent!");
      setResendCooldown(30);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to resend OTP");
    } finally {
      setLoading(false);
    }
  };

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => setResendCooldown(prev => prev > 0 ? prev - 1 : 0), 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const handleVerifyOtp = async () => {
    if (otp.length !== 6) {
      toast.error("Enter 6-digit OTP");
      return;
    }
    try {
      setLoading(true);
      const response = await axios.post(`${API}/auth/verify-otp`, { mobile: phone, otp, country_code: "91" });
      toast.success("Login successful!");
      localStorage.setItem("user", JSON.stringify(response.data.user));
      localStorage.setItem("userPhone", phone);
      onLoginSuccess(response.data.user, response.data.is_admin);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Invalid OTP");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      data-testid="reporter-login-page"
      className={`min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden ${
        darkMode ? "bg-[#040609]" : "bg-[#070B12]"
      }`}
    >
      <div className="absolute top-0 left-0 w-72 h-72 bg-[#2D7AFF]/10 rounded-full -translate-x-1/2 -translate-y-1/2" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-[#2D7AFF]/5 rounded-full translate-x-1/3 translate-y-1/3" />

      {/* Logo */}
      <div className="mb-10 text-center relative z-10">
        <img src="/logo.svg" alt="Venture OS" className="h-16 w-16 mx-auto mb-3 rounded-xl drop-shadow-lg" data-testid="login-logo" />
        <p className={`text-sm tracking-wide ${darkMode ? "text-[#7A90A8]" : "text-[#5A7090]"}`}>
          Reporter & Admin Login
        </p>
      </div>

      {/* Phone Step */}
      {step === "phone" && (
        <div
          data-testid="phone-step"
          className={`w-full max-w-sm p-8 rounded-3xl shadow-lg relative z-10 border ${
            darkMode ? "bg-[#070B12] border-[#1C2840]" : "bg-[#070B12] border-[#1C2840]"
          }`}
        >
          <button
            data-testid="back-to-home"
            onClick={() => navigate("/")}
            className={`flex items-center gap-1 text-sm mb-4 ${darkMode ? "text-[#7A90A8] hover:text-white" : "text-[#5A7090] hover:text-[#E2EAF6]"} transition-colors`}
          >
            <ChevronLeft size={16} /> Back to News
          </button>

          <div className="text-center mb-6">
            <div className="w-14 h-14 rounded-2xl bg-[#131B2A] flex items-center justify-center mx-auto mb-3">
              <UserPlus size={24} className="text-[#2D7AFF]" />
            </div>
            <h2 className={`text-lg font-semibold ${darkMode ? "text-white" : "text-[#E2EAF6]"}`}>
              Login as Reporter
            </h2>
            <p className={`text-sm mt-1 ${darkMode ? "text-[#7A90A8]" : "text-[#5A7090]"}`}>
              Enter your mobile number to continue
            </p>
          </div>

          <div className="space-y-4">
            <div className="flex gap-2">
              <div className={`flex items-center justify-center px-4 rounded-xl font-medium text-sm ${
                darkMode ? "bg-[#0D1321] text-[#A0B4CC] border border-[#1C2840]" : "bg-[#0D1321] text-[#2D7AFF] border border-[#1C2840]"
              }`}>
                +91
              </div>
              <Input
                data-testid="phone-input"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, "").slice(0, 10))}
                placeholder="9876543210"
                maxLength={10}
                className={`text-lg tracking-wider h-12 rounded-xl ${darkMode ? "bg-[#0D1321] border-[#1C2840] text-white" : "border-[#1C2840]"}`}
              />
            </div>

            <Button
              data-testid="send-otp-btn"
              onClick={handleSendOtp}
              disabled={loading || phone.length !== 10}
              className="w-full bg-[#2D7AFF] hover:bg-[#1A5FCC] text-white h-12 rounded-xl text-base font-medium shadow-lg shadow-[#2D7AFF]/20 disabled:opacity-40"
            >
              {loading ? <Loader2 size={20} className="animate-spin" /> : (
                <><Phone size={18} className="mr-2" /> Send OTP</>
              )}
            </Button>
          </div>
        </div>
      )}

      {/* OTP Step */}
      {step === "otp" && (
        <div
          data-testid="otp-step"
          className={`w-full max-w-sm p-8 rounded-3xl shadow-lg relative z-10 border ${
            darkMode ? "bg-[#070B12] border-[#1C2840]" : "bg-[#070B12] border-[#1C2840]"
          }`}
        >
          <button
            data-testid="back-to-phone"
            onClick={() => { setStep("phone"); setOtp(""); }}
            className={`flex items-center gap-1 text-sm mb-4 ${darkMode ? "text-[#7A90A8] hover:text-white" : "text-[#5A7090] hover:text-[#E2EAF6]"} transition-colors`}
          >
            <ChevronLeft size={16} /> Change Number
          </button>

          <div className="text-center mb-6">
            <div className="w-14 h-14 rounded-2xl bg-[#131B2A] flex items-center justify-center mx-auto mb-3">
              <Shield size={24} className="text-[#2D7AFF]" />
            </div>
            <h2 className={`text-lg font-semibold ${darkMode ? "text-white" : "text-[#E2EAF6]"}`}>Verify OTP</h2>
            <p className={`text-sm mt-1 ${darkMode ? "text-[#7A90A8]" : "text-[#5A7090]"}`}>
              Code sent to +91 {phone}
            </p>
          </div>

          <div className="space-y-4">
            <Input
              data-testid="otp-input"
              type="tel"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
              placeholder="● ● ● ● ● ●"
              maxLength={6}
              className={`text-2xl text-center tracking-[0.5em] h-14 rounded-xl ${darkMode ? "bg-[#0D1321] border-[#1C2840] text-white" : "border-[#1C2840]"}`}
            />

            <Button
              data-testid="verify-otp-btn"
              onClick={handleVerifyOtp}
              disabled={loading || otp.length !== 6}
              className="w-full bg-[#2D7AFF] hover:bg-[#1A5FCC] text-white h-12 rounded-xl text-base font-medium shadow-lg shadow-[#2D7AFF]/20 disabled:opacity-40"
            >
              {loading ? <Loader2 size={20} className="animate-spin" /> : (
                <><Shield size={18} className="mr-2" /> Verify & Login</>
              )}
            </Button>

            <button
              data-testid="resend-otp-btn"
              onClick={handleResendOtp}
              disabled={resendCooldown > 0 || loading}
              className={`w-full text-sm font-medium py-2 transition-colors ${
                resendCooldown > 0 ? (darkMode ? "text-[#7A90A8]" : "text-[#7A90A8]") : "text-[#2D7AFF] hover:text-[#2D7AFF]"
              }`}
            >
              {resendCooldown > 0 ? `Resend OTP in ${resendCooldown}s` : "Resend OTP"}
            </button>
          </div>
        </div>
      )}

      <p className={`mt-8 text-xs relative z-10 ${darkMode ? "text-[#7A90A8]" : "text-[#7A90A8]"}`}>
        Secure login powered by SMS verification
      </p>
    </div>
  );
}

export { LoginPage };
