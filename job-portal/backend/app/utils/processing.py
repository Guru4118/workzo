from dateutil import parser
import re
from geopy.geocoders import Nominatim

def parse_posted_date(raw_date_str):
    try:
        dt = parser.parse(raw_date_str, fuzzy=True, dayfirst=False)
        return dt.date().isoformat()
    except Exception:
        return None



def clean_salary(raw):
    if not raw: return None
    # remove commas, currency symbols, approximate tags
    s = raw.replace(",", "")
    # find ranges or single numbers
    m = re.findall(r"\d{2,7}", s)
    if not m: return None
    nums = list(map(int, m))
    if len(nums) >= 2:
        return {"min": min(nums), "max": max(nums)}
    return {"min": nums[0], "max": nums[0]}



geolocator = Nominatim(user_agent="job_portal")

def normalize_location(loc_str):
    try:
        loc = geolocator.geocode(loc_str, language="en", timeout=10)
        if not loc: return {"raw": loc_str}
        return {"raw": loc_str, "lat": loc.latitude, "lon": loc.longitude, "display_name": loc.address}
    except Exception:
        return {"raw": loc_str}


def tag_source(job):
    title = job.get("title","").lower()
    company = job.get("company","").lower()
    tags = set()
    if "senior" in title or "lead" in title: tags.add("seniority:senior")
    if "intern" in title: tags.add("seniority:intern")
    if "python" in title or "django" in title: tags.add("skill:python")
    if job.get("source"): tags.add(f"source:{job['source']}")
    return list(tags)
