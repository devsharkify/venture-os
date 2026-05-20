import { useState, useRef, useContext, useCallback } from "react";
import { AppContext } from "../App";
import { API } from "../App";
import axios from "axios";
import { Video, Square, Upload, Loader2, RotateCcw, Camera } from "lucide-react";
import { Button } from "./ui/button";
import { toast } from "sonner";

export const VideoRecorder = ({ onUpload }) => {
  const { darkMode } = useContext(AppContext);
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);

  const [status, setStatus] = useState("idle"); // idle, previewing, recording, recorded, uploading
  const [recordedUrl, setRecordedUrl] = useState(null);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [duration, setDuration] = useState(0);
  const timerRef = useRef(null);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } }, 
        audio: true 
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.muted = true;
      }
      setStatus("previewing");
    } catch (err) {
      toast.error("Camera access denied. Please allow camera permission.");
    }
  }, []);

  const startRecording = useCallback(() => {
    chunksRef.current = [];
    const mr = new MediaRecorder(streamRef.current, { mimeType: "video/webm" });
    mr.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
    mr.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "video/webm" });
      setRecordedBlob(blob);
      setRecordedUrl(URL.createObjectURL(blob));
      setStatus("recorded");
      // Stop camera
      streamRef.current?.getTracks().forEach(t => t.stop());
    };
    mediaRecorderRef.current = mr;
    mr.start(1000);
    setStatus("recording");
    setDuration(0);
    timerRef.current = setInterval(() => setDuration(d => d + 1), 1000);
  }, []);

  const stopRecording = useCallback(() => {
    clearInterval(timerRef.current);
    mediaRecorderRef.current?.stop();
  }, []);

  const resetRecording = useCallback(() => {
    setRecordedUrl(null);
    setRecordedBlob(null);
    setDuration(0);
    setStatus("idle");
  }, []);

  const uploadRecording = useCallback(async () => {
    if (!recordedBlob) return;
    setStatus("uploading");
    try {
      const formData = new FormData();
      formData.append("file", recordedBlob, `recording_${Date.now()}.webm`);
      const response = await axios.post(`${API}/upload/video`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      const url = response.data.url;
      toast.success("Video uploaded!");
      onUpload(url);
      setStatus("idle");
    } catch {
      toast.error("Upload failed");
      setStatus("recorded");
    }
  }, [recordedBlob, onUpload]);

  const formatTime = (s) => `${Math.floor(s / 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;

  return (
    <div data-testid="video-recorder" className={`rounded-xl border overflow-hidden ${darkMode ? "bg-slate-800 border-slate-700" : "bg-slate-50 border-slate-200"}`}>
      {/* Video Preview / Playback */}
      <div className="relative aspect-video bg-black">
        {status === "idle" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <Camera size={40} className="text-slate-500 mb-3" />
            <Button onClick={startCamera} className="bg-orange-500 hover:bg-orange-600" data-testid="start-camera-btn">
              <Camera size={16} className="mr-2" /> Open Camera
            </Button>
          </div>
        )}
        {(status === "previewing" || status === "recording") && (
          <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />
        )}
        {(status === "recorded" || status === "uploading") && recordedUrl && (
          <video src={recordedUrl} controls className="w-full h-full object-cover" />
        )}
        {/* Recording indicator */}
        {status === "recording" && (
          <div className="absolute top-3 left-3 flex items-center gap-2 px-3 py-1.5 bg-red-600 rounded-full text-white text-sm font-medium">
            <div className="w-2.5 h-2.5 bg-white rounded-full animate-pulse" />
            REC {formatTime(duration)}
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="p-3 flex items-center justify-center gap-3">
        {status === "previewing" && (
          <Button onClick={startRecording} className="bg-red-600 hover:bg-red-700" data-testid="record-btn">
            <Video size={16} className="mr-2" /> Start Recording
          </Button>
        )}
        {status === "recording" && (
          <Button onClick={stopRecording} variant="destructive" data-testid="stop-btn">
            <Square size={16} className="mr-2" /> Stop ({formatTime(duration)})
          </Button>
        )}
        {status === "recorded" && (
          <>
            <Button onClick={resetRecording} variant="outline" data-testid="retake-btn">
              <RotateCcw size={16} className="mr-2" /> Retake
            </Button>
            <Button onClick={uploadRecording} className="bg-orange-500 hover:bg-orange-600" data-testid="upload-recording-btn">
              <Upload size={16} className="mr-2" /> Upload Video
            </Button>
          </>
        )}
        {status === "uploading" && (
          <Button disabled className="bg-orange-500">
            <Loader2 size={16} className="animate-spin mr-2" /> Uploading...
          </Button>
        )}
      </div>
    </div>
  );
};
