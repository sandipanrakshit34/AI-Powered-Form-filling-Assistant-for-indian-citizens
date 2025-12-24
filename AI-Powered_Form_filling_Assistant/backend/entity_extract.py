# entity_extract.py (IMPROVED: stricter PAN, safer DOB parsing, aadhaar normalization)
import re
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def extract_entities_with_ai(text):
    """
    Try AI first (keeps your existing AI flow), but always validate/normalize
    the fields with deterministic regex fallback to avoid wrong outputs.
    """
    prompt = f"""
You are an expert at extracting data from Indian ID cards. Return ONLY JSON with keys:
name, dob, gender, aadhar, pan, address.
OCR TEXT:
{text}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = response.choices[0].message.content
        # Try parse JSON from model
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            # Validate & normalize parsed data
            return normalize_and_validate(parsed, text)
    except Exception as e:
        print("AI extraction failed:", e)

    # Fallback deterministic extraction
    return regex_fallback(text)

def normalize_and_validate(parsed, full_text):
    """
    Normalize fields from AI output and validate them. If AI gives something
    invalid (e.g., bad PAN), we replace with deterministic extraction.
    """
    out = {
        "name": parsed.get("name"),
        "dob": parsed.get("dob"),
        "gender": parsed.get("gender"),
        "aadhar": parsed.get("aadhar"),
        "pan": parsed.get("pan"),
        "address": parsed.get("address")
    }

    # Normalize Aadhaar (remove spaces)
    if out["aadhar"]:
        a = re.sub(r'\s+', '', str(out["aadhar"]))
        if re.fullmatch(r'\d{12}', a):
            out["aadhar"] = a
        else:
            out["aadhar"] = None

    # Validate PAN: strict pattern AAAAA9999A
    if out["pan"]:
        if not re.fullmatch(r'[A-Z]{5}\d{4}[A-Z]', str(out["pan"]).strip()):
            out["pan"] = None

    # Normalize DOB: try to standardize to DD/MM/YYYY
    if out["dob"]:
        out["dob"] = normalize_dob(out["dob"])

    # If AI missed something or gave invalid, use regex fallback values for reliability
    fallback = regex_fallback(full_text)
    for k in out:
        if not out[k] and fallback.get(k):
            out[k] = fallback[k]

    return out

def normalize_dob(dob_str):
    """Try a few DOB formats and return DD/MM/YYYY or None"""
    if not dob_str: 
        return None
    s = dob_str.strip()
    # common dd/mm/yyyy
    m = re.match(r'(\d{2})[\/\-](\d{2})[\/\-](\d{4})', s)
    if m:
        d, mth, y = m.groups()
        try:
            datetime(int(y), int(mth), int(d))
            return f"{d}/{mth}/{y}"
        except:
            return None
    # pattern like 0301/2004 (DDMM/YYYY)
    m2 = re.match(r'(\d{4})[\/\-](\d{4})', s)
    if m2:
        part, year = m2.groups()
        dd = part[:2]; mm = part[2:4]
        try:
            datetime(int(year), int(mm), int(dd))
            return f"{dd}/{mm}/{year}"
        except:
            # if invalid, try swap but still validate
            try:
                datetime(int(year), int(dd), int(mm))
                return f"{mm}/{dd}/{year}"
            except:
                return None
    # try ISO-like YYYY-MM-DD
    m3 = re.match(r'(\d{4})[\/\-](\d{2})[\/\-](\d{2})', s)
    if m3:
        y, mth, d = m3.groups()
        try:
            datetime(int(y), int(mth), int(d))
            return f"{d}/{mth}/{y}"
        except:
            return None
    return None

def regex_fallback(text):
    """Deterministic fallback: stricter rules, no guesswork."""
    data = {
        "name": None,
        "dob": None,
        "gender": None,
        "aadhar": None,
        "pan": None,
        "address": None
    }

    clean = " ".join(str(text).split())

    # Aadhaar: 12 digits (allow spaces)
    aadhar = re.search(r'\b(\d{4}\s?\d{4}\s?\d{4})\b', clean)
    if aadhar:
        data["aadhar"] = aadhar.group(1).replace(" ", "")

    # PAN: strict - accept only if pan regex found AND context contains PAN keywords
    pan_match = re.search(r'\b([A-Z]{5}\d{4}[A-Z])\b', clean)
    if pan_match:
        span = pan_match.span()
        ctx = clean[max(0, span[0]-50):span[1]+50]
        if re.search(r'\bPAN\b|\bIncome Tax\b|\bPermanent Account Number\b', ctx, re.I):
            data["pan"] = pan_match.group(1)
        else:
            # do NOT accept loose PAN-looking strings without context
            data["pan"] = None

    # DOB: standard patterns or DDMM/YYYY
    dob = re.search(r'\b(\d{2}[\/\-]\d{2}[\/\-]\d{4})\b', clean)
    if dob:
        candidate = dob.group(1)
        normalized = normalize_dob(candidate)
        data["dob"] = normalized
    else:
        m = re.search(r'\b(\d{4})[\/\-](\d{4})\b', clean)
        if m:
            part, year = m.groups()
            dd = part[:2]; mm = part[2:4]
            try:
                datetime(int(year), int(mm), int(dd))
                data["dob"] = f"{dd}/{mm}/{year}"
            except:
                data["dob"] = None

    # Gender
    if re.search(r'\bmale\b', clean, re.I):
        data["gender"] = "Male"
    elif re.search(r'\bfemale\b', clean, re.I):
        data["gender"] = "Female"

    # Name: look for uppercase multiword sequences (Aadhaar often uppercase)
    name_match = re.search(r'\b([A-Z][A-Z]+\s+[A-Z][A-Z]+(?:\s+[A-Z][A-Z]+)?)\b', clean)
    if name_match:
        data["name"] = name_match.group(1).title()

    # Address: try VTC/PO ... PIN Code pattern
    addr = re.search(r'(VTC[:\s_\-]*.*?PIN Code[:\s]*\d{6})', clean, re.I)
    if addr:
        data["address"] = addr.group(1)
    else:
        # fallback capture between PO and PIN Code
        addr2 = re.search(r'(PO[:\s]*.*?PIN Code[:\s]*\d{6})', clean, re.I)
        if addr2:
            data["address"] = addr2.group(1)

    return data
