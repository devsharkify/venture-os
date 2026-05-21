import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, AppContext } from "../App";
import { toast } from "sonner";
import {
  User, Phone, Mail, MapPin, FileText, Camera,
  Loader2, CheckCircle, ArrowRight
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";

export default function ReporterRegister() {
  const { darkMode } = useContext(AppContext);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [checkingPhone, setCheckingPhone] = useState(false);
  const [existingReporter, setExistingReporter] = useState(null);

  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    photo: "",
    location: "",
    bio: ""
  });

  const checkPhone = async (phone) => {
    if (phone.length < 10) {
      setExistingReporter(null);
      return;
    }

    try {
      setCheckingPhone(true);
      const response = await axios.get(`${API}/reporter/check/${phone}`);
      if (response.data.registered) {
        setExistingReporter(response.data);
      } else {
        setExistingReporter(null);
      }
    } catch (error) {
      console.error("Error checking phone:", error);
    } finally {
      setCheckingPhone(false);
    }
  };

  const handlePhoneChange = (e) => {
    const phone = e.target.value.replace(/\D/g, "").slice(0, 10);
    setFormData(prev => ({ ...prev, phone }));
    checkPhone(phone);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.name || !formData.phone) {
      toast.error("Name and phone are required");
      return;
    }

    if (formData.phone.length !== 10) {
      toast.error("Enter valid 10-digit phone number");
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API}/reporter/register`, formData);
      toast.success("Registration submitted! Wait for approval.");
      navigate(`/reporter/dashboard/${response.data.id}`);
    } catch (error) {
      console.error("Registration failed:", error);
      toast.error(error.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const goToDashboard = () => {
    if (existingReporter?.id) {
      navigate(`/reporter/dashboard/${existingReporter.id}`);
    }
  };

  return (
    <div data-testid="reporter-register-page" className={`min-h-screen py-8 px-4 ${darkMode ? "bg-[#070B12]" : "bg-[#0A0E18]"}`}>
      <div className="max-w-lg mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-[#2D7AFF] rounded-full flex items-center justify-center mx-auto mb-4">
            <Camera size={40} className="text-white" />
          </div>
          <h1 className={`text-2xl font-bold mb-2 ${darkMode ? "text-white" : "text-[#E2EAF6]"}`}>
            Become a Reporter
          </h1>
          <p className={`text-sm ${darkMode ? "text-[#7A90A8]" : "text-[#7A90A8]"}`}>
            Join Venture OS as a citizen reporter and share local news
          </p>
        </div>

        {/* Existing Reporter Alert */}
        {existingReporter && (
          <div className={`p-4 rounded-lg mb-6 ${
            existingReporter.status === "approved"
              ? "bg-green-100 border border-green-300"
              : existingReporter.status === "pending"
                ? "bg-yellow-100 border border-yellow-300"
                : "bg-red-100 border border-red-300"
          }`}>
            <p className="font-medium text-[#E2EAF6]">
              Already registered!
            </p>
            <p className="text-sm text-[#A0B4CC] mt-1">
              {existingReporter.status === "approved"
                ? `Welcome back, ${existingReporter.name}! You're approved.`
                : existingReporter.status === "pending"
                  ? "Your registration is pending approval."
                  : "Your registration was rejected."}
            </p>
            <Button
              data-testid="go-to-dashboard-btn"
              onClick={goToDashboard}
              className="mt-3 bg-[#2D7AFF] hover:bg-[#1A5FCC]"
            >
              Go to Dashboard
              <ArrowRight size={16} className="ml-1" />
            </Button>
          </div>
        )}

        {/* Registration Form */}
        {!existingReporter && (
          <form onSubmit={handleSubmit} className={`p-6 rounded-lg border ${darkMode ? "bg-[#0D1321] border-[#1C2840]" : "bg-[#070B12] border-[#1C2840]"}`}>
            <div className="space-y-4">
              {/* Name */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-[#D0DDF0]" : ""}>
                  <User size={14} className="inline mr-1" />
                  Full Name *
                </Label>
                <Input
                  data-testid="reporter-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter your full name"
                  className={darkMode ? "bg-[#131B2A] border-[#1C2840] text-white" : ""}
                />
              </div>

              {/* Phone */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-[#D0DDF0]" : ""}>
                  <Phone size={14} className="inline mr-1" />
                  Phone Number *
                </Label>
                <div className="relative">
                  <Input
                    data-testid="reporter-phone-input"
                    value={formData.phone}
                    onChange={handlePhoneChange}
                    placeholder="9876543210"
                    maxLength={10}
                    className={darkMode ? "bg-[#131B2A] border-[#1C2840] text-white" : ""}
                  />
                  {checkingPhone && (
                    <Loader2 size={16} className="absolute right-3 top-3 animate-spin text-[#2D7AFF]" />
                  )}
                </div>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-[#D0DDF0]" : ""}>
                  <Mail size={14} className="inline mr-1" />
                  Email (Optional)
                </Label>
                <Input
                  data-testid="reporter-email-input"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="reporter@example.com"
                  className={darkMode ? "bg-[#131B2A] border-[#1C2840] text-white" : ""}
                />
              </div>

              {/* Location */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-[#D0DDF0]" : ""}>
                  <MapPin size={14} className="inline mr-1" />
                  Location
                </Label>
                <Input
                  data-testid="reporter-location-input"
                  value={formData.location}
                  onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                  placeholder="City, State"
                  className={darkMode ? "bg-[#131B2A] border-[#1C2840] text-white" : ""}
                />
              </div>

              {/* Photo URL */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-[#D0DDF0]" : ""}>
                  <Camera size={14} className="inline mr-1" />
                  Photo URL
                </Label>
                <Input
                  data-testid="reporter-photo-input"
                  value={formData.photo}
                  onChange={(e) => setFormData(prev => ({ ...prev, photo: e.target.value }))}
                  placeholder="https://example.com/photo.jpg"
                  className={darkMode ? "bg-[#131B2A] border-[#1C2840] text-white" : ""}
                />
              </div>

              {/* Bio */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-[#D0DDF0]" : ""}>
                  <FileText size={14} className="inline mr-1" />
                  About You
                </Label>
                <Textarea
                  data-testid="reporter-bio-input"
                  value={formData.bio}
                  onChange={(e) => setFormData(prev => ({ ...prev, bio: e.target.value }))}
                  placeholder="Tell us about yourself..."
                  rows={3}
                  className={darkMode ? "bg-[#131B2A] border-[#1C2840] text-white" : ""}
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                data-testid="register-submit-btn"
                disabled={loading || !formData.name || !formData.phone}
                className="w-full bg-[#2D7AFF] hover:bg-[#1A5FCC] text-white py-6"
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="animate-spin mr-2" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircle size={18} className="mr-2" />
                    Submit Registration
                  </>
                )}
              </Button>
            </div>
          </form>
        )}

        {/* Info */}
        <div className={`mt-6 p-4 rounded-lg ${darkMode ? "bg-[#0D1321]" : "bg-[#0D1321]"}`}>
          <h3 className={`font-semibold mb-2 ${darkMode ? "text-white" : "text-[#E2EAF6]"}`}>
            What happens next?
          </h3>
          <ul className={`text-sm space-y-2 ${darkMode ? "text-[#A0B4CC]" : "text-[#7A90A8]"}`}>
            <li>&bull; Admin will review your application</li>
            <li>&bull; Once approved, you can submit news</li>
            <li>&bull; Get your digital ID card</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export { ReporterRegister };
