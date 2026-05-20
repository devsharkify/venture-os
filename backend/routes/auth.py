from fastapi import APIRouter, HTTPException
import httpx
import random
from datetime import datetime, timezone, timedelta
from database import db, logger
from models import SendOTPRequest, VerifyOTPRequest
import os

router = APIRouter(prefix="/api")

AUTHKEY_API_KEY = os.environ.get("AUTHKEY_API_KEY", "")
AUTHKEY_SID = os.environ.get("AUTHKEY_SID", "35306")
ADMIN_PHONE = "7386917770"
OTP_EXPIRY_MINUTES = 5

otp_storage = {}


def clean_phone(phone: str) -> str:
    phone = phone.replace("+91", "").replace("+", "").replace(" ", "").replace("-", "").strip()
    return phone[-10:] if len(phone) >= 10 else phone


@router.post("/auth/send-otp")
async def send_otp(request: SendOTPRequest):
    mobile = clean_phone(request.mobile)
    if len(mobile) != 10 or not mobile.isdigit():
        raise HTTPException(status_code=400, detail="Invalid mobile number. Must be 10 digits.")

    otp = str(random.randint(100000, 999999))
    otp_storage[mobile] = {
        "otp": otp,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
        "attempts": 0
    }

    # Send OTP via Authkey.io for ALL users including admin
    if AUTHKEY_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    "https://api.authkey.io/request",
                    params={
                        "authkey": AUTHKEY_API_KEY,
                        "mobile": mobile,
                        "country_code": "91",
                        "sid": AUTHKEY_SID,
                        "otp": otp,
                        "company": "Mint Street"
                    }
                )
                result = resp.json() if resp.text else {}
                if resp.status_code == 200 and "Submitted" in str(result.get("Message", "")):
                    logger.info(f"AuthKey OTP sent to {mobile}: LogID={result.get('LogID')}")
                else:
                    logger.error(f"AuthKey failed for {mobile}: {result}")
                    raise HTTPException(status_code=500, detail="Failed to send OTP. Please try again.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"AuthKey error for {mobile}: {e}")
            raise HTTPException(status_code=500, detail="SMS service error. Please try again.")
    else:
        logger.warning("AUTHKEY_API_KEY not set — OTP not sent via SMS")

    return {"message": "OTP sent successfully", "expires_in": OTP_EXPIRY_MINUTES * 60}


@router.post("/auth/resend-otp")
async def resend_otp(request: SendOTPRequest):
    mobile = clean_phone(request.mobile)
    if len(mobile) != 10 or not mobile.isdigit():
        raise HTTPException(status_code=400, detail="Invalid mobile number. Must be 10 digits.")

    otp = str(random.randint(100000, 999999))
    otp_storage[mobile] = {
        "otp": otp,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
        "attempts": 0
    }

    if AUTHKEY_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    "https://api.authkey.io/request",
                    params={
                        "authkey": AUTHKEY_API_KEY,
                        "mobile": mobile,
                        "country_code": "91",
                        "sid": AUTHKEY_SID,
                        "otp": otp,
                        "company": "Mint Street"
                    }
                )
                result = resp.json() if resp.text else {}
                if resp.status_code == 200 and "Submitted" in str(result.get("Message", "")):
                    logger.info(f"AuthKey OTP resent to {mobile}: LogID={result.get('LogID')}")
                else:
                    logger.error(f"AuthKey resend failed for {mobile}: {result}")
                    raise HTTPException(status_code=500, detail="Failed to resend OTP. Please try again.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"AuthKey resend error for {mobile}: {e}")
            raise HTTPException(status_code=500, detail="SMS service error. Please try again.")

    return {"message": "OTP resent successfully", "expires_in": OTP_EXPIRY_MINUTES * 60}


@router.post("/auth/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    mobile = clean_phone(request.mobile)
    otp = request.otp.strip()
    stored = otp_storage.get(mobile)

    if not stored:
        raise HTTPException(status_code=400, detail="No OTP sent to this number. Please request a new OTP.")

    # Check expiry
    if datetime.now(timezone.utc) > stored["expires_at"]:
        del otp_storage[mobile]
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one.")

    # Check max attempts
    if stored["attempts"] >= 3:
        del otp_storage[mobile]
        raise HTTPException(status_code=400, detail="Too many failed attempts. Please request a new OTP.")

    # Verify
    if stored["otp"] != otp:
        stored["attempts"] += 1
        remaining = 3 - stored["attempts"]
        raise HTTPException(status_code=400, detail=f"Invalid OTP. {remaining} attempt(s) remaining.")

    # Success — clear OTP
    del otp_storage[mobile]

    is_admin = mobile == ADMIN_PHONE
    user = await db.users.find_one({"phone": mobile}, {"_id": 0})
    if not user:
        user = {
            "phone": mobile, "name": "", "email": "", "preferred_language": "en",
            "is_admin": is_admin, "is_reporter": False, "reporter_id": "",
            "photo_url": "", "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user)
        user.pop("_id", None)

    reporter = await db.reporters.find_one({"phone": mobile, "is_approved": True}, {"_id": 0, "reporter_id": 1})
    if reporter:
        user["is_reporter"] = True
        user["reporter_id"] = reporter.get("reporter_id", "")

    return {"message": "OTP verified successfully", "user": user, "is_admin": is_admin}


@router.get("/auth/user/{phone}")
async def get_user(phone: str):
    user = await db.users.find_one({"phone": phone}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/auth/user/{phone}")
async def update_user(phone: str, name: str = "", preferred_language: str = "en"):
    update = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if name:
        update["name"] = name
    if preferred_language:
        update["preferred_language"] = preferred_language
    await db.users.update_one({"phone": phone}, {"$set": update})
    user = await db.users.find_one({"phone": phone}, {"_id": 0})
    return user or {"message": "User not found"}
