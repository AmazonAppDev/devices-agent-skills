"""Deterministic everyday-commitment parser.

Turns one consented utterance into zero or more typed commitment candidates. No model is
involved: every field is derived from explicit text, and every assumption (for example a
default hour for "Friday") is recorded on the candidate so the UI can disclose it.
"""

import calendar
import hashlib
import re
from datetime import date, datetime, timedelta

PROMISE = re.compile(
    r"\b(i(?:'ll| will| shall| promise(?: to)?| promised(?: to)?| need to| have to| must| gotta|'ve got to| got to)"
    r"|i(?:'m| am) (?:going to|gonna)|let me|remind me to|don't let me forget to|make sure i"
    r"|i won't forget to|i will not forget to|i'll not forget to)\b"
    r"|^(?:\w+,\s*)?(?:gotta|got to|need to|have to|must|remember to)\b"
)
REQUEST = re.compile(r"^(?:\w+,\s*)?(?:can you|could you|would you|will you|please|don't forget to)\s+")
NEGATION = re.compile(
    r"\b(i will not|i won't|i'll not|i shall not|i cannot|i can't|i don't|i do not|i shan't|never"
    r"|i did not|i didn't|i haven't|i have not|i hasn't|not yet)\b"
)
NOT_FORGET = re.compile(r"\b(?:won't|will not|don't let me|never) forget\b|\bnot forget\b")
HEDGE = re.compile(r"\b(if|maybe|might|probably|perhaps|try to|hopefully)\b")
INJECTION = re.compile(
    r"\bignore (?:all |your |the |previous |prior )*(?:instructions|rules|policy)\b"
    r"|\bmark (?:it|this|that|everything|all|the contract|them) (?:as )?(?:done|verified|complete)\b"
    r"|\bset (?:the )?status\b|\bsystem prompt\b"
)
PAST_VERBS = (
    r"called|phoned|rang|texted|messaged|emailed|paid|sent|finished|submitted|booked|ordered|bought|picked up"
    r"|took out|cleaned|did|completed|walked|fed|watered|renewed|returned|dropped off|attended|went to"
    r"|recharged|collected|brought|cooked|fixed|washed"
)
COMPLETION = re.compile(
    rf"^(?:ok(?:ay)?,? |so |well,? |yes,? )?(?:(?:i |i've |i have )?(?:just |already |finally )?({PAST_VERBS})"
    r"|(?:i'm |i am )?(?:done|finished) with)\b"
)

PEOPLE = (
    "wife|husband|partner|mom|mum|mother|dad|father|sister|brother|son|daughter|kids|children|boss|manager"
    "|team|friend|neighbou?r|grandma|grandpa|grandmother|grandfather|aunt|uncle|cousin|nephew|niece|landlord"
    "|doctor|dentist|teacher|client|colleague|roommate|girlfriend|boyfriend|fianc[eé]e?|in-laws"
    "|amma|appa|nani|nana|dadi|dada|bhaiya|didi|mummy|papa"
)
ITEM_CLASSES = [
    (r"grocer|milk|bread|egg|vegetable|fruit|rice|flour|snack", "grocery_bag"),
    (r"drink|beer|soda|juice|water bottle|wine|coke", "drinks_bag"),
    (r"medicine|prescription|pharmacy|tablet|pills", "pharmacy_bag"),
    (r"flower|bouquet", "flowers"),
    (r"cake|dessert|pizza|food|dinner|takeaway|takeout", "food_container"),
    (r"parcel|package|box", "parcel"),
]
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
MONTHS.update({name.lower(): i for i, name in enumerate(calendar.month_abbr) if name})
MONTHS["sept"] = 9
MONTH_RE = "|".join(sorted(MONTHS, key=len, reverse=True))
NUMBERS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50,
}
NUM_WORDS = "|".join(sorted(NUMBERS, key=len, reverse=True))
MAX_RELATIVE = {"minutes": 60 * 24 * 366, "hours": 24 * 366, "days": 366, "weeks": 53}
PM_CONTEXT = re.compile(r"\b(tonight|evening|afternoon|night)\b")
AM_CONTEXT = re.compile(r"\b(morning|breakfast)\b")
GENERIC = {"call", "pay", "send", "take", "do", "finish", "buy", "book", "order", "clean", "go", "attend",
           "water", "feed", "walk", "return", "renew", "submit", "text", "email", "pick", "bill", "out", "get",
           "make", "have", "be", "will", "ll", "i've", "done", "complete", "completed", "today", "now"}


def recurrence(text):
    """DAILY / WEEKLY(weekday) / MONTHLY(day) series from explicit words only."""
    m = re.search(r"\b(?:on )?(?:the )?(\d{1,2})(?:st|nd|rd|th)? of (?:every|each) month\b", text)
    if m and 1 <= int(m[1]) <= 31:
        return {"freq": "MONTHLY", "day": int(m[1])}
    for i, name in enumerate(WEEKDAYS):
        if re.search(rf"\b(?:every|each) {name}s?\b|\b(?:on )?{name}s\b", text):
            return {"freq": "WEEKLY", "weekday": i}
    if re.search(r"\b(?:every|each) (?:day|morning|evening|night)\b|\bdaily\b", text):
        return {"freq": "DAILY"}
    if re.search(r"\b(?:every|each) week\b|\bweekly\b", text):
        return {"freq": "WEEKLY", "weekday": None}
    if re.search(r"\b(?:every|each) month\b|\bmonthly\b", text):
        return {"freq": "MONTHLY", "day": None}
    return None


def _num(token):
    try:
        return float(token)
    except ValueError:
        return NUMBERS.get(token)


def _safe_date(year, month, day):
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _dated(text, today):
    """Calendar dates: '5th', 'the 20th', '20th October', 'Oct 30', 'October 30th'. Returns (date|None)."""
    m = re.search(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({MONTH_RE})\b", text) or None
    if m:
        day, month = int(m[1]), MONTHS[m[2]]
    else:
        m = re.search(rf"\b({MONTH_RE})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?\b", text)
        if m:
            day, month = int(m[2]), MONTHS[m[1]]
        else:
            m = re.search(r"\b(?:on|by|before|till|until|the)\s+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)\b", text)
            if not m:
                return None
            day = int(m[1])
            if not 1 <= day <= 31:
                return None
            for offset in range(0, 3):
                month_index = today.month - 1 + offset
                candidate = _safe_date(today.year + month_index // 12, month_index % 12 + 1, day)
                if candidate and candidate >= today:
                    return candidate
            return None
    candidate = _safe_date(today.year, month, day)
    if candidate and candidate < today:
        candidate = _safe_date(today.year + 1, month, day)
    return candidate


def _soonest(now_local, day, h, minute):
    """For an hour without am/pm, choose the soonest future reading (h or h+12) on the given day."""
    base = datetime.combine(day, datetime.min.time(), now_local.tzinfo)
    options = [h % 12, h % 12 + 12] if 1 <= h <= 12 else [h]
    for hour in sorted(options):
        candidate = base.replace(hour=hour, minute=minute)
        if candidate > now_local:
            return hour
    return min(options)


def parse_deadline(text, now_local):
    """Return (due_local | None, trigger | None, assumption | None)."""
    trigger = None
    if re.search(r"\b(when i (?:get|come|am|'m) (?:back )?home|on my way home|before i get home|when i'm back"
                 r"|on the way back)\b", text):
        trigger = "ARRIVAL_HOME"
    if re.search(r"\bbefore (?:i )?(?:watch(?:ing)?|turn(?:ing)? on|switch(?:ing)? on) "
                 r"(?:the )?(?:tv|television|netflix|prime|a movie|the game)|before tv\b", text):
        trigger = "BEFORE_ENTERTAINMENT"
    if re.search(r"\b(?:in|within) (?:an? )?hour and a half\b|\bin (?:one and a half|1\.5) hours?\b", text):
        return now_local + timedelta(minutes=90), trigger, None
    if re.search(r"\bin half an hour\b", text):
        return now_local + timedelta(minutes=30), trigger, None
    rel = re.search(rf"\bin ({NUM_WORDS}|\d+(?:\.\d+)?) (minute|min|hour|hr|day|week)s?\b", text)
    if rel:
        n = _num(rel[1])
        unit = {"minute": "minutes", "min": "minutes", "hour": "hours", "hr": "hours", "day": "days",
                "week": "weeks"}[rel[2]]
        if n and 0 < n <= MAX_RELATIVE[unit]:
            return now_local + timedelta(**{unit: n}), trigger, None
        return None, trigger, "Relative time out of range; no deadline set."

    assumption = None
    today = now_local.date()
    day = today
    day_given = False
    weekday_given = False
    if re.search(r"\bday after tomorrow\b|\bparso\b", text):
        day, day_given = today + timedelta(days=2), True
    elif re.search(r"\b(tomorrow|tmrw|kal)\b", text):
        day, day_given = today + timedelta(days=1), True
    else:
        dated = _dated(text, today)
        if dated:
            day, day_given = dated, True
        else:
            for i, name in enumerate(WEEKDAYS):
                m = re.search(rf"\b(next )?{name}s?\b", text)
                if m:
                    ahead = (i - now_local.weekday()) % 7 or 7
                    if m[1] and ahead < 7:
                        ahead += 7
                    day, day_given, weekday_given = today + timedelta(days=ahead), True, True
                    break
    if not day_given:
        if re.search(r"\bnext week\b", text):
            day, day_given = today + timedelta(days=(7 - now_local.weekday()) or 7), True
        elif re.search(r"\bnext month\b", text):
            first = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
            day, day_given = first, True
        elif re.search(r"\b(end of (?:the )?week|this weekend)\b", text):
            target = 4 if "end of" in text else 5
            day, day_given, weekday_given = today + timedelta(days=(target - now_local.weekday()) % 7), True, True

    hour = minute = None
    pm_ctx = bool(PM_CONTEXT.search(text))
    am_ctx = bool(AM_CONTEXT.search(text)) and not pm_ctx
    m = re.search(r"(?<![\d:.])(\d{1,2})(?:[:.]([0-5]\d))?\s*(a\.?m\.?|p\.?m\.?)(?![a-z])", text)
    if m and 1 <= int(m[1]) <= 12:
        hour = int(m[1]) % 12 + (12 if m[3].startswith("p") else 0)
        minute = int(m[2] or 0)
    else:
        m = re.search(r"\b(?:at|by|before|until|till|around|for)\s+([01]?\d|2[0-3])[:.]([0-5]\d)\b", text)
        hp = re.search(rf"\b(half|quarter) (past|to) ({NUM_WORDS}|\d{{1,2}})\b", text)
        if m:
            h, minute = int(m[1]), int(m[2])
            if h > 12 or h == 0:
                hour = h
            elif pm_ctx:
                hour = h % 12 + 12
            elif am_ctx:
                hour = h % 12
            else:
                hour = _soonest(now_local, day, h, minute)
                assumption = f"No am/pm spoken; '{m[0].strip()}' read as the next {hour:02d}:{minute:02d}."
        elif hp:
            h = int(_num(hp[3]) or 0)
            if 1 <= h <= 12:
                minute = 30 if hp[1] == "half" else (15 if hp[2] == "past" else 45)
                h = h if hp[2] == "past" else (h - 1 or 12)
                hour = h % 12 + 12 if pm_ctx else h % 12 if am_ctx else _soonest(now_local, day, h, minute)
        elif re.search(r"\b(?:at|by|before) noon\b|\bmidday\b", text):
            hour, minute = 12, 0
        elif re.search(r"\bmidnight\b", text):
            hour, minute = 23, 59
        else:
            m = re.search(r"\b(?:at|by|before|around) (\d{1,2})(?: o'clock)?\b(?!\s*(?:minute|min|hour|hr|day|rep|squat"
                          r"|st|nd|rd|th|of))", text)
            if m and 1 <= int(m[1]) <= 12:
                h = int(m[1])
                hour = h % 12 + 12 if pm_ctx else h % 12 if am_ctx else _soonest(now_local, day, h, 0)
                minute = 0
                assumption = f"No am/pm spoken; '{m[0].strip()}' read as {hour:02d}:00 local time."
    if hour is None:
        for pattern, h, label in [
            (r"\b(end of (?:the )?day|eod|by close of business|cob)\b", 18, "end of day"),
            (r"\bafter breakfast\b", 9, "after breakfast"),
            (r"\bafter lunch\b", 14, "after lunch"),
            (r"\bafter dinner\b", 21, "after dinner"),
            (r"\bbefore (?:bed|bedtime|sleeping)\b|\bat bedtime\b", 22, "before bed"),
            (r"\btonight\b", 21, "tonight"),
            (r"\bevery night\b|\bat night\b", 21, "at night"),
            (r"\bevening\b", 19, "evening"),
            (r"\bafternoon\b", 15, "afternoon"),
            (r"\bmorning\b", 9, "morning"),
        ]:
            if re.search(pattern, text):
                hour, minute = h, 0
                assumption = f"No exact time spoken; '{label}' interpreted as {h:02d}:00 local time."
                break
    if hour is None and day_given:
        hour, minute = 18, 0
        assumption = "Day given without a time; deadline set to 18:00 local time on that day."
    if hour is None:
        return None, trigger, None
    due = datetime.combine(day, datetime.min.time(), now_local.tzinfo).replace(hour=hour, minute=minute)
    if due <= now_local:
        if not day_given:
            due += timedelta(days=1)
            assumption = (assumption + " " if assumption else "") + "Time already passed today; set for tomorrow."
        elif weekday_given:
            due += timedelta(days=7)
            assumption = (assumption + " " if assumption else "") + "That time has passed; set for next week."
    return due, trigger, assumption


def _counterparty(original, text):
    m = re.search(rf"\b(?:my|our|the) ({PEOPLE})\b", text)
    if m:
        return m[1].capitalize()
    m = re.search(rf"\b(?:call|phone|ring|text|message|email|tell|meet|visit|pick up|drop off|pay)\s+({PEOPLE})\b",
                  text)
    if m:
        return m[1].capitalize()
    m = re.search(r"\b(?:call|phone|ring|text|message|email|tell|meet|visit|pick up|drop off|pay)\s+"
                  r"([A-Z][a-z]+)\b", original)
    if m and m[1].lower() not in {"the", "my", "a", "it", "him", "her", "them", "up", "i"}:
        return m[1]
    return None


def classify(text):
    """Return (commitment_type, verification_modality, item_class, reps)."""
    m = re.search(rf"\b(\d+|{NUM_WORDS})\s+(squats?|push-?ups?|sit-?ups?|lunges?|jumping jacks?|burpees?)", text)
    if m and _num(m[1]):
        reps = int(_num(m[1]))
        modality = "FIRE_TV_LIVE_POSE_CAMERA" if m[2].startswith("squat") else "AUTHORIZED_MANUAL_CONFIRMATION"
        return "PHYSICAL_ACTION", modality, None, reps
    if re.search(r"\b(run|jog|walk|workout|work out|gym|yoga|swim|cycle|exercise|stretch)\b", text) and not re.search(
        r"\bwalk (?:the )?dog\b", text
    ):
        return "PHYSICAL_ACTION", "AUTHORIZED_MANUAL_CONFIRMATION", None, None
    if not re.search(r"\b(recharge|charger|bill)\b", text) and re.search(
        r"\b(call|ring up|video call|facetime)\b|\bgive .* a call\b|\bphone (?:my |the )?[a-z]+\b", text
    ):
        return "SCHEDULED_SOCIAL_COMMITMENT", "BEE_CONVERSATION_AUDIT", None, None
    if re.search(r"\b(attend|join|go to|be at|cover|show up)\b.*\b(meeting|appointment|class|game|recital|interview"
                 r"|party|session|ceremony|review|standup|call)\b", text):
        return "SCHEDULED_SOCIAL_COMMITMENT", "BEE_CONVERSATION_AUDIT", None, None
    if re.search(r"\b(bring|buy|get|grab|pick up|collect|carry)\b", text):
        for pattern, item in ITEM_CLASSES:
            if re.search(pattern, text):
                home = re.search(r"\bhome\b|when i (?:get|come)|on my way", text)
                return ("INBOUND_ITEM", "RING_THRESHOLD_OBJECT_SCAN" if home else "AUTHORIZED_MANUAL_CONFIRMATION",
                        item, None)
    return "TRIGGERED_TASK", "AUTHORIZED_MANUAL_CONFIRMATION", None, None


def _title(sentence):
    t = sentence.replace("’", "'")
    t = re.sub(r"^.*?" + PROMISE.pattern, "", t, count=1, flags=re.I).strip(" ,.")
    t = re.sub(r"^(?:also|just|definitely|then)\s+", "", t, flags=re.I)
    t = re.sub(
        rf"\b(?:for |on |by |before |till |until )?(?:the )?(?:(?:{MONTH_RE})\.? \d{{1,2}}(?:st|nd|rd|th)?"
        rf"|\d{{1,2}}(?:st|nd|rd|th)? (?:of )?(?:{MONTH_RE}))\b",
        "",
        t,
        flags=re.I,
    )
    t = re.sub(
        r"\b(?:maybe|probably|perhaps|hopefully|try to|definitely|really)\b"
        r"|\b(?:day after tomorrow|today|tonight|tomorrow(?: morning| evening| night)?|kal"
        r"|this (?:morning|afternoon|evening|weekend)|in the (?:morning|afternoon|evening)|at night|morning|evening"
        r"|end of (?:the )?(?:day|week)|eod|next (?:week|month)"
        r"|(?:every|each) (?:day|morning|evening|night|week|month|monday|tuesday|wednesday|thursday|friday|saturday"
        r"|sunday)s?|daily|weekly|monthly"
        r"|(?:on )?(?:the )?\d{1,2}(?:st|nd|rd|th)? of (?:every|each) month"
        r"|(?:when i (?:get|come) (?:back )?home|on my way home|before i get home)"
        r"|(?:after|before) (?:breakfast|lunch|dinner|bed|bedtime)"
        r"|(?:at|by|before|around|until|till) (?:\d{1,2}(?:[:.]\d\d)?\s*(?:am|pm|a\.m\.|p\.m\.|o'clock)?|noon|midnight)"
        r"|(?:at )?(?:half|quarter) (?:past|to) \w+"
        r"|in (?:a|an|half an|one|two|three|four|five|ten|fifteen|twenty|thirty|\d+) (?:minutes?|mins?|hours?|days?|weeks?)"
        r"(?: and a half)?"
        r"|(?:on |by |before |till |until )?(?:the )?\d{1,2}(?:st|nd|rd|th)(?: of)?(?: \w+)?"
        r"|(?:on |by |next )?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?)\b",
        "",
        t,
        flags=re.I,
    )
    t = re.sub(r"\s+", " ", t).strip(" ,.")
    return (t[:1].upper() + t[1:])[:90] if t else "Spoken commitment"


def split_sentences(utterance):
    return [p.strip() for p in re.split(r"(?<=[.!?;])\s+|\s+(?:and also|also,)\s+", utterance) if p.strip()]


def parse(utterance, now_local, request=False):
    """Candidate commitments for one utterance (empty when nothing is promised).

    With ``request=True`` (another household member speaking) a polite request such as
    "can you pick up milk" also yields a candidate; the caller keeps it NEEDS_CONFIRMATION.
    """
    out = []
    for original in split_sentences(utterance[:4000]):
        text = original.lower().replace("’", "'")
        asked = request and REQUEST.search(text)
        if INJECTION.search(text) or not (PROMISE.search(text) or asked):
            continue
        if asked and not PROMISE.search(text):
            original = REQUEST.sub("i'll ", original.lower(), count=1)
            text = original
        if NEGATION.search(NOT_FORGET.sub("", text)):
            out.append({"negated": True, "sentence": original})
            continue
        ctype, modality, item, reps = classify(text)
        due, trigger, assumption = parse_deadline(text, now_local)
        series = recurrence(text)
        if series and due is None and not trigger:
            due = now_local.replace(hour=21, minute=0, second=0, microsecond=0)
            if due <= now_local:
                due += timedelta(days=1)
            assumption = "Recurring promise without a time; each occurrence is due at 21:00 local time."
        title = _title(original)
        person = _counterparty(original, text)
        key = "gen_" + hashlib.sha256(re.sub(r"\W+", " ", title.lower()).strip().encode()).hexdigest()[:12]
        out.append(dict(
            key=key, sentence=original, title=title, counterparty=person or "Self",
            type=ctype, modality=modality, item_class=item, reps=reps, due_local=due,
            trigger=trigger, assumption=assumption, hedged=bool(HEDGE.search(text)), recurrence=series,
        ))
    return out


def completion_claim(utterance):
    """Return normalized completion text when the speaker says something is already done."""
    text = utterance.lower().replace("’", "'").strip()
    return text if COMPLETION.search(text) and not NEGATION.search(text) else None


def tokens(text):
    stop = {"the", "a", "an", "my", "to", "and", "i", "it", "for", "with", "of", "on", "up", "just", "already",
            "i've", "have", "finally"}
    stems = {"called": "call", "phoned": "call", "rang": "call", "paid": "pay", "sent": "send", "texted": "text",
             "emailed": "email", "bought": "buy", "booked": "book", "ordered": "order", "took": "take",
             "finished": "finish", "submitted": "submit", "cleaned": "clean", "walked": "walk", "fed": "feed",
             "watered": "water", "renewed": "renew", "returned": "return", "picked": "pick", "did": "do",
             "went": "go", "attended": "attend", "mum": "mom", "mother": "mom", "amma": "mom", "mummy": "mom",
             "recharged": "recharge", "collected": "collect", "brought": "bring", "cooked": "cook", "fixed": "fix",
             "washed": "wash", "bills": "bill"}
    return {stems.get(w, w) for w in re.findall(r"[a-z']+", text.lower()) if w not in stop}


def specific(words):
    """Tokens that identify *what* or *who* (not generic verbs) — required to match a completion claim."""
    return {w for w in words if w not in GENERIC and len(w) > 2}


def next_occurrence(series, due_local):
    """Next local due datetime of a recurring series after ``due_local`` (local-day arithmetic, DST-safe)."""
    if series["freq"] == "DAILY":
        return due_local + timedelta(days=1)
    if series["freq"] == "WEEKLY":
        return due_local + timedelta(days=7)
    month_index = due_local.month  # next month, 0-based offset handled below
    year = due_local.year + month_index // 12
    month = month_index % 12 + 1
    day = min(series.get("day") or due_local.day, calendar.monthrange(year, month)[1])
    return due_local.replace(year=year, month=month, day=day)
