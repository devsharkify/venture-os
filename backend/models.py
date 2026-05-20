from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime, timezone
import re
import uuid


# ===================== NEWS MODELS =====================

class NewsArticle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    summary: str
    category: str
    category_label: Optional[str] = ""
    image: Optional[str] = ""
    video_url: Optional[str] = ""
    content_type: str = "text"
    link: Optional[str] = ""
    is_pinned: bool = False
    priority: int = 5
    is_active: bool = True
    source: Optional[str] = ""
    seo_description: Optional[str] = ""
    seo_keywords: Optional[List[str]] = []
    seo_author: Optional[str] = ""
    og_title: Optional[str] = ""
    og_description: Optional[str] = ""
    og_image: Optional[str] = ""
    article_published_time: Optional[str] = ""
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NewsCreate(BaseModel):
    title: str
    summary: str
    category: str
    image: Optional[str] = ""
    video_url: Optional[str] = ""
    content_type: str = "text"
    link: Optional[str] = ""
    is_pinned: bool = False
    priority: int = 5
    source: Optional[str] = ""
    published_at: Optional[str] = None

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    video_url: Optional[str] = None
    content_type: Optional[str] = None
    link: Optional[str] = None
    is_pinned: Optional[bool] = None
    priority: Optional[int] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None
    published_at: Optional[str] = None

class ScrapeRequest(BaseModel):
    url: str
    category: str
    rephrase: bool = True

class ScrapeResponse(BaseModel):
    title: str
    summary: str
    image: str
    source: str


# ===================== STATUS MODELS =====================

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str


# ===================== LIVE TV MODELS =====================

class LiveChannel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    youtube_url: str
    youtube_id: str = ""
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class LiveChannelCreate(BaseModel):
    name: str
    youtube_url: str

class YouTubeShort(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    youtube_url: str
    youtube_id: str = ""
    thumbnail: str = ""
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class YouTubeShortCreate(BaseModel):
    title: str
    youtube_url: str


# ===================== REPORTER MODELS =====================

class Reporter(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reporter_id: str = ""
    name: str
    phone: str
    email: Optional[str] = ""
    photo: Optional[str] = ""
    location: Optional[str] = ""
    bio: Optional[str] = ""
    status: str = "pending"  # pending | approved | rejected
    rejection_reason: Optional[str] = ""
    approved_at: Optional[str] = ""
    news_submitted: int = 0
    news_approved: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = ""

class ReporterRegister(BaseModel):
    name: str
    phone: str
    email: Optional[str] = ""
    photo: Optional[str] = ""
    location: Optional[str] = ""
    bio: Optional[str] = ""

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = (v or "").strip()
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("Phone must be exactly 10 digits")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = (v or "").strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v

class ReporterNews(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reporter_id: str
    reporter_name: str = ""
    title: str
    summary: str
    category: str
    image: Optional[str] = ""
    video_url: Optional[str] = ""
    reporter_video_url: Optional[str] = ""
    news_type: str = "text"  # text | video_url | reporter_video
    location: Optional[str] = ""
    status: str = "pending"  # pending | approved | rejected
    rejection_reason: Optional[str] = ""
    approved_at: Optional[str] = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = ""

class ReporterNewsSubmit(BaseModel):
    title: str
    summary: str
    category: str
    image: Optional[str] = ""
    video_url: Optional[str] = ""
    reporter_video_url: Optional[str] = ""
    news_type: str = "text"
    location: Optional[str] = ""


# ===================== STARTUP APPLICATION MODELS =====================

class StartupApplication(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    mobile: str
    email: str
    idea: str  # tech business idea description
    pitch_pdf_url: Optional[str] = ""
    pitch_video_url: Optional[str] = ""
    age: Optional[int] = None
    colony: Optional[str] = ""
    area: Optional[str] = ""
    city: Optional[str] = "Hyderabad"
    is_woman_founder: bool = False
    status: str = "submitted"  # submitted | shortlisted | interviewed | selected | rejected
    rejection_reason: Optional[str] = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = ""

class StartupApplicationCreate(BaseModel):
    name: str
    mobile: str
    email: str
    idea: str
    pitch_pdf_url: Optional[str] = ""
    pitch_video_url: Optional[str] = ""
    age: Optional[int] = None
    colony: Optional[str] = ""
    area: Optional[str] = ""
    city: Optional[str] = "Hyderabad"
    is_woman_founder: bool = False

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        v = (v or "").strip()
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("Mobile must be exactly 10 digits")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = (v or "").strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v

    @field_validator("idea")
    @classmethod
    def validate_idea(cls, v: str) -> str:
        v = (v or "").strip()
        if len(v) < 30:
            raise ValueError("Please describe your idea in at least 30 characters")
        return v


# ===================== AUTH MODELS =====================

class SendOTPRequest(BaseModel):
    mobile: str

class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str

class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    phone: str
    name: Optional[str] = ""
    email: Optional[str] = ""
    is_admin: bool = False
    is_reporter: bool = False
    reporter_id: Optional[str] = ""
    photo_url: Optional[str] = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ===================== ANALYTICS MODELS =====================

class ArticleView(BaseModel):
    article_id: str
    user_phone: Optional[str] = ""
    duration: int = 0
    source: str = "app"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
