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
  const { language, darkMode } = useContext(AppContext);
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
      toast.error(language === "en" ? "Name and phone are required" : "పేరు మరియు ఫోన్ అవసరం");
      return;
    }
    
    if (formData.phone.length !== 10) {
      toast.error(language === "en" ? "Enter valid 10-digit phone number" : "చెల్లుబాటు అయ్యే 10 అంకెల ఫోన్ నంబర్ నమోదు చేయండి");
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API}/reporter/register`, formData);
      toast.success(language === "en" ? "Registration submitted! Wait for approval." : "రిజిస్ట్రేషన్ సమర్పించబడింది! ఆమోదం కోసం వేచి ఉండండి.");
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
    <div data-testid="reporter-register-page" className={`min-h-screen py-8 px-4 ${darkMode ? "bg-slate-900" : "bg-slate-50"}`}>
      <div className="max-w-lg mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Camera size={40} className="text-white" />
          </div>
          <h1 className={`text-2xl font-bold mb-2 ${darkMode ? "text-white" : "text-slate-900"} ${language === "te" ? "font-telugu" : ""}`}>
            {language === "en" ? "Become a Reporter" : "రిపోర్టర్ అవ్వండి"}
          </h1>
          <p className={`text-sm ${darkMode ? "text-slate-400" : "text-slate-600"} ${language === "te" ? "font-telugu" : ""}`}>
            {language === "en" 
              ? "Join Mint Street as a citizen reporter and share local news"
              : "Mint Street లో సిటిజన్ రిపోర్టర్‌గా చేరి స్థానిక వార్తలను పంచుకోండి"}
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
            <p className="font-medium text-slate-900">
              {language === "en" ? "Already registered!" : "ఇప్పటికే నమోదు అయింది!"}
            </p>
            <p className="text-sm text-slate-700 mt-1">
              {existingReporter.status === "approved" 
                ? (language === "en" ? `Welcome back, ${existingReporter.name}! You're approved.` : `తిరిగి స్వాగతం, ${existingReporter.name}! మీరు ఆమోదించబడ్డారు.`)
                : existingReporter.status === "pending"
                  ? (language === "en" ? "Your registration is pending approval." : "మీ రిజిస్ట్రేషన్ ఆమోదం కోసం పెండింగ్‌లో ఉంది.")
                  : (language === "en" ? "Your registration was rejected." : "మీ రిజిస్ట్రేషన్ తిరస్కరించబడింది.")}
            </p>
            <Button
              data-testid="go-to-dashboard-btn"
              onClick={goToDashboard}
              className="mt-3 bg-orange-500 hover:bg-orange-600"
            >
              {language === "en" ? "Go to Dashboard" : "డాష్‌బోర్డ్‌కు వెళ్ళండి"}
              <ArrowRight size={16} className="ml-1" />
            </Button>
          </div>
        )}

        {/* Registration Form */}
        {!existingReporter && (
          <form onSubmit={handleSubmit} className={`p-6 rounded-lg border ${darkMode ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"}`}>
            <div className="space-y-4">
              {/* Name */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-slate-200" : ""}>
                  <User size={14} className="inline mr-1" />
                  {language === "en" ? "Full Name *" : "పూర్తి పేరు *"}
                </Label>
                <Input
                  data-testid="reporter-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder={language === "en" ? "Enter your full name" : "మీ పూర్తి పేరు నమోదు చేయండి"}
                  className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                />
              </div>

              {/* Phone */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-slate-200" : ""}>
                  <Phone size={14} className="inline mr-1" />
                  {language === "en" ? "Phone Number *" : "ఫోన్ నంబర్ *"}
                </Label>
                <div className="relative">
                  <Input
                    data-testid="reporter-phone-input"
                    value={formData.phone}
                    onChange={handlePhoneChange}
                    placeholder="9876543210"
                    maxLength={10}
                    className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                  />
                  {checkingPhone && (
                    <Loader2 size={16} className="absolute right-3 top-3 animate-spin text-orange-500" />
                  )}
                </div>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-slate-200" : ""}>
                  <Mail size={14} className="inline mr-1" />
                  {language === "en" ? "Email (Optional)" : "ఇమెయిల్ (ఐచ్ఛికం)"}
                </Label>
                <Input
                  data-testid="reporter-email-input"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="reporter@example.com"
                  className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                />
              </div>

              {/* Location */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-slate-200" : ""}>
                  <MapPin size={14} className="inline mr-1" />
                  {language === "en" ? "Location" : "ప్రదేశం"}
                </Label>
                <Input
                  data-testid="reporter-location-input"
                  value={formData.location}
                  onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                  placeholder={language === "en" ? "City, State" : "నగరం, రాష్ట్రం"}
                  className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                />
              </div>

              {/* Photo URL */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-slate-200" : ""}>
                  <Camera size={14} className="inline mr-1" />
                  {language === "en" ? "Photo URL" : "ఫోటో URL"}
                </Label>
                <Input
                  data-testid="reporter-photo-input"
                  value={formData.photo}
                  onChange={(e) => setFormData(prev => ({ ...prev, photo: e.target.value }))}
                  placeholder="https://example.com/photo.jpg"
                  className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                />
              </div>

              {/* Bio */}
              <div className="space-y-2">
                <Label className={darkMode ? "text-slate-200" : ""}>
                  <FileText size={14} className="inline mr-1" />
                  {language === "en" ? "About You" : "మీ గురించి"}
                </Label>
                <Textarea
                  data-testid="reporter-bio-input"
                  value={formData.bio}
                  onChange={(e) => setFormData(prev => ({ ...prev, bio: e.target.value }))}
                  placeholder={language === "en" ? "Tell us about yourself..." : "మీ గురించి చెప్పండి..."}
                  rows={3}
                  className={darkMode ? "bg-slate-700 border-slate-600 text-white" : ""}
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                data-testid="register-submit-btn"
                disabled={loading || !formData.name || !formData.phone}
                className="w-full bg-orange-500 hover:bg-orange-600 text-white py-6"
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="animate-spin mr-2" />
                    {language === "en" ? "Submitting..." : "సమర్పిస్తోంది..."}
                  </>
                ) : (
                  <>
                    <CheckCircle size={18} className="mr-2" />
                    {language === "en" ? "Submit Registration" : "రిజిస్ట్రేషన్ సమర్పించండి"}
                  </>
                )}
              </Button>
            </div>
          </form>
        )}

        {/* Info */}
        <div className={`mt-6 p-4 rounded-lg ${darkMode ? "bg-slate-800" : "bg-orange-50"}`}>
          <h3 className={`font-semibold mb-2 ${darkMode ? "text-white" : "text-slate-900"} ${language === "te" ? "font-telugu" : ""}`}>
            {language === "en" ? "What happens next?" : "తర్వాత ఏమి జరుగుతుంది?"}
          </h3>
          <ul className={`text-sm space-y-2 ${darkMode ? "text-slate-300" : "text-slate-600"} ${language === "te" ? "font-telugu" : ""}`}>
            <li>• {language === "en" ? "Admin will review your application" : "అడ్మిన్ మీ అప్లికేషన్‌ను సమీక్షిస్తారు"}</li>
            <li>• {language === "en" ? "Once approved, you can submit news" : "ఆమోదించిన తర్వాత, మీరు వార్తలను సమర్పించవచ్చు"}</li>
            <li>• {language === "en" ? "Get your digital ID card" : "మీ డిజిటల్ ID కార్డ్ పొందండి"}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export { ReporterRegister };
