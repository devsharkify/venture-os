import { useState, useContext, useRef } from "react";
import axios from "axios";
import { API, AppContext } from "../App";
import { Upload, Image, Video, Loader2, X, Check } from "lucide-react";
import { Button } from "./ui/button";

export const FileUpload = ({ type = "image", onUpload, currentUrl = "" }) => {
  const { darkMode } = useContext(AppContext);
  const [uploading, setUploading] = useState(false);
  const [uploadedUrl, setUploadedUrl] = useState(currentUrl);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const isImage = type === "image";
  const acceptTypes = isImage 
    ? "image/jpeg,image/png,image/gif,image/webp" 
    : "video/mp4,video/webm,video/quicktime";
  const maxSize = isImage ? 5 : 100; // MB
  const Icon = isImage ? Image : Video;

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate size
    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > maxSize) {
      setError(`File too large. Max ${maxSize}MB`);
      return;
    }

    setError("");
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const endpoint = isImage ? "/upload/image" : "/upload/video";
      const response = await axios.post(`${API}${endpoint}`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      // ImageKit returns full URL directly
      const fullUrl = response.data.url;
      
      setUploadedUrl(fullUrl);
      onUpload(fullUrl);
    } catch (err) {
      console.error("Upload failed:", err);
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = () => {
    setUploadedUrl("");
    onUpload("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-2">
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptTypes}
        onChange={handleFileSelect}
        className="hidden"
        id={`file-upload-${type}`}
      />

      {!uploadedUrl ? (
        <label
          htmlFor={`file-upload-${type}`}
          className={`
            flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg cursor-pointer
            transition-colors
            ${darkMode 
              ? "border-[#1C2840] hover:border-[#2D7AFF] bg-[#131B2A]/50" 
              : "border-[#1C2840] hover:border-[#2D7AFF] bg-[#0A0E18]"
            }
            ${uploading ? "pointer-events-none opacity-60" : ""}
          `}
        >
          {uploading ? (
            <Loader2 size={32} className="animate-spin text-[#2D7AFF] mb-2" />
          ) : (
            <Icon size={32} className={darkMode ? "text-[#7A90A8] mb-2" : "text-[#5A7090] mb-2"} />
          )}
          <span className={`text-sm font-medium ${darkMode ? "text-[#A0B4CC]" : "text-[#7A90A8]"}`}>
            {uploading
              ? "Uploading..."
              : `Click to upload ${isImage ? "image" : "video"}`
            }
          </span>
          <span className={`text-xs mt-1 ${darkMode ? "text-[#5A7090]" : "text-[#7A90A8]"}`}>
            Max {maxSize}MB
          </span>
        </label>
      ) : (
        <div className={`relative rounded-lg overflow-hidden ${darkMode ? "bg-[#131B2A]" : "bg-[#131B2A]"}`}>
          {isImage ? (
            <img 
              src={uploadedUrl} 
              alt="Uploaded" 
              className="w-full h-32 object-cover"
            />
          ) : (
            <video 
              src={uploadedUrl} 
              className="w-full h-32 object-cover"
              controls
            />
          )}
          <div className="absolute top-2 right-2 flex gap-1">
            <Button
              size="icon"
              variant="secondary"
              className="h-7 w-7 bg-[#00D9C8] text-white hover:bg-green-600"
            >
              <Check size={14} />
            </Button>
            <Button
              size="icon"
              variant="secondary"
              onClick={handleRemove}
              className="h-7 w-7 bg-red-500 text-white hover:bg-red-600"
            >
              <X size={14} />
            </Button>
          </div>
        </div>
      )}

      {error && (
        <p className="text-xs text-red-500">{error}</p>
      )}
    </div>
  );
};
