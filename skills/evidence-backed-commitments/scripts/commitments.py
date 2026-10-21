"""Deterministic everyday-commitment parser.

Turns one consented utterance into zero or more typed commitment candidates. No model is
involved: every field is derived from explicit text, and every assumption (for example a
default hour for "Friday") is recorded on the candidate so the UI can disclose it.
"""

import hashlib
import re
from datetime import datetime, timedelta

PROMISE = re.compile(
    r"\b(i(?:'ll| will| shall| promise(?: to)?| promised(?: to)?| need to| have to| must| gotta|'ve got to| got to)"
    r"|i(?:'m| am) (?:going to|gonna)|let me|remind me to|don't let me forget to|make sure i)\b"
)
REQUEST = re.compile(r"^(?:\w+,\s*)?(?:can you|could you|would you|will you|please|don't forget to)\s+")
NEGATION = re.compile(r"\b(i will not|i won't|i cannot|i can't|i don't|i do not|i shan't|never)\b")
HEDGE = re.compile(r"\b(if|maybe|might|probably|perhaps|try to|hopefully)\b")
INJECTION = re.compile(r"\b(ignore .*instructions|mark .*verified|set .*status|system prompt)\b")
COMPLETION = re.compile(
    r"^(?:ok(?:ay)?,? |so |well,? )?(?:i (?:just |already |finally )?"
    r"(called|phoned|rang|texted|messaged|emailed|paid|sent|finished|submitted|booked|ordered|bought|picked up"
    r"|took out|cleaned|did|completed|walked|fed|watered|renewed|returned|dropped off|attended|went to)"
    r"|(?:done|finished) with)\b"
)

PEOPLE = (
    "wife|husband|partner|mom|mum|mother|dad|father|sister|brother|son|daughter|kids|children|boss|manager"
    "|team|friend|neighbou?r|grandma|grandpa|grandmother|grandfather|aunt|uncle|cousin|nephew|niece|landlord"
    "|doctor|dentist|teacher|client|colleague|roommate|girlfriend|boyfriend|fianc[eé]e?|in-laws"
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
NUMBERS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "ten": 10,
    "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "half an": 0.5,
}


def recurrence(text):
    """DAILY / WEEKLY(weekday) series from explicit words only."""
    for i, name in enumerate(WEEKDAYS):
        if re.search(rf"\bevery {name}s?\b|\b(?:on )?{name}s\b", text):
            return {"freq": "WEEKLY", "weekday": i}
    if re.search(r"\bevery (?:day|morning|evening|night)\b|\bdaily\b|\beach day\b", text):
        return {"freq": "DAILY"}
    if re.search(r"\bevery week\b|\bweekly\b", text):
        return {"freq": "WEEKLY", "weekday": None}
    return None


def _num(token):
    try:
        return float(token)
    except ValueError:
        return NUMBERS.get(token)


def parse_deadline(text, now_local):
    """Return (due_local | None, trigger | None, assumption | None)."""
    trigger = None
    if re.search(r"\b(when i (?:get|come|am|'m) (?:back )?home|on my way home|before i get home|when i'm back"
                 r"|after work|on the way back)\b", text):
        trigger = "ARRIVAL_HOME"
    if re.search(r"\bbefore (?:i )?(?:watch(?:ing)?|turn(?:ing)? on|switch(?:ing)? on) "
                 r"(?:the )?(?:tv|television|netflix|prime|a movie|the game)|before tv\b", text):
        trigger = "BEFORE_ENTERTAINMENT"
    assumption = None
    rel = re.search(r"\bin (a|an|half an|one|two|three|four|five|ten|fifteen|twenty|thirty|forty|fifty|\d+(?:\.\d+)?)"
                    r" (minute|min|hour|hr|day)s?\b", text)
    if rel:
        n = _num(rel[1]) or 1
        unit = {"minute": "minutes", "min": "minutes", "hour": "hours", "hr": "hours", "day": "days"}[rel[2]]
        if rel[1] == "half an":
            n, unit = 30, "minutes"
        return now_local + timedelta(**{unit: n}), trigger, None

    day = now_local.date()
    day_given = False
    if re.search(r"\b(tomorrow|tmrw)\b", text):
        day, day_given = day + timedelta(days=1), True
    else:
        for i, name in enumerate(WEEKDAYS):
            m = re.search(rf"\b(next )?{name}\b", text)
            if m:
                ahead = (i - now_local.weekday()) % 7 or 7
                if m[1]:
                    ahead += 7 if ahead < 7 else 0
                day, day_given = day + timedelta(days=ahead), True
                break
    if re.search(r"\b(end of (?:the )?week|this weekend)\b", text) and not day_given:
        target = 4 if "end of" in text else 5
        day, day_given = day + timedelta(days=(target - now_local.weekday()) % 7), True

    hour = minute = None
    m = re.search(r"\b(?:at|by|before|around|until|till|for)?\s*(\d{1,2})(?::(\d\d))?\s*(a\.?m\.?|p\.?m\.?)", text)
    if m:
        hour = int(m[1]) % 12 + (12 if m[3].startswith("p") else 0)
        minute = int(m[2] or 0)
    else:
        m = re.search(r"\b(?:at|by|before|until|till)\s+([01]?\d|2[0-3]):([0-5]\d)\b", text)
        if m:
            hour, minute = int(m[1]), int(m[2])
        elif re.search(r"\b(?:at|by|before) noon\b|\bmidday\b", text):
            hour, minute = 12, 0
        elif re.search(r"\bmidnight\b", text):
            hour, minute = 23, 59
        else:
            m = re.search(r"\b(?:at|by|before) (\d{1,2})(?: o'clock)?\b(?!\s*(?:minute|min|hour|hr|day|rep|squat))",
                          text)
            if m and 1 <= int(m[1]) <= 12:
                h = int(m[1])
                evening = re.search(r"\b(tonight|evening|afternoon)\b", text)
                hour, minute = (h % 12 + 12 if evening or h < 7 else h), 0
                assumption = f"Interpreted '{m[0].strip()}' as {hour:02d}:00 local time."
    if hour is None:
        for pattern, h, label in [
            (r"\b(end of (?:the )?day|eod|by close of business|cob)\b", 18, "end of day"),
            (r"\btonight\b", 21, "tonight"),
            (r"\bevery night\b", 21, "every night"),
            (r"\bthis evening\b|\bin the evening\b|\bevery evening\b", 19, "this evening"),
            (r"\bthis afternoon\b|\bin the afternoon\b", 15, "this afternoon"),
            (r"\bthis morning\b|\bin the morning\b|\btomorrow morning\b|\bevery morning\b", 9, "the morning"),
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
    if due <= now_local and not day_given:
        due += timedelta(days=1)
        assumption = (assumption + " " if assumption else "") + "Time already passed today; set for tomorrow."
    return due, trigger, assumption


def _counterparty(original, text):
    m = re.search(rf"\b(?:my|our|the) ({PEOPLE})\b", text)
    if m:
        return m[1].capitalize()
    m = re.search(r"\b(?:call|phone|ring|text|message|email|tell|meet|visit|pick up|drop off|pay)\s+"
                  r"([A-Z][a-z]+)\b", original)
    if m and m[1].lower() not in {"the", "my", "a", "it", "him", "her", "them", "up", "i"}:
        return m[1]
    return None


def classify(text):
    """Return (commitment_type, verification_modality, item_class, reps)."""
    reps = None
    m = re.search(r"\b(\d+|ten|fifteen|twenty|thirty)\s+(squats?|push-?ups?|sit-?ups?|lunges?|jumping jacks?|burpees?)",
                  text)
    if m:
        reps = int(_num(m[1]))
        modality = "FIRE_TV_LIVE_POSE_CAMERA" if m[2].startswith("squat") else "AUTHORIZED_MANUAL_CONFIRMATION"
        return "PHYSICAL_ACTION", modality, None, reps
    if re.search(r"\b(run|jog|walk|workout|work out|gym|yoga|swim|cycle|exercise|stretch)\b", text) and not re.search(
        r"\bwalk (?:the )?dog\b", text
    ):
        return "PHYSICAL_ACTION", "AUTHORIZED_MANUAL_CONFIRMATION", None, None
    if re.search(r"\b(call|phone|ring up|video call|facetime|give .* a call)\b", text):
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
    t = re.sub(
        r"\b(?:maybe|probably|perhaps|hopefully|try to|definitely|really)\b"
        r"|\b(?:today|tonight|tomorrow(?: morning| evening| night)?|this (?:morning|afternoon|evening|weekend)"
        r"|in the (?:morning|afternoon|evening)|morning|end of (?:the )?(?:day|week)|eod"
        r"|every (?:day|morning|evening|night|week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?"
        r"|daily|weekly|each day"
        r"|(?:when i (?:get|come) (?:back )?home|on my way home|after work|before i get home)"
        r"|(?:at|by|before|around|until|till) (?:\d{1,2}(?::\d\d)?\s*(?:am|pm|a\.m\.|p\.m\.|o'clock)?|noon|midnight)"
        r"|in (?:a|an|half an|one|two|three|four|five|ten|fifteen|twenty|thirty|\d+) (?:minutes?|mins?|hours?|days?)"
        r"|(?:on |by |next )?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b",
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
    for original in split_sentences(utterance):
        text = original.lower().replace("’", "'")
        asked = request and REQUEST.search(text)
        if INJECTION.search(text) or not (PROMISE.search(text) or asked):
            continue
        if asked and not PROMISE.search(text):
            original = REQUEST.sub("i'll ", original.lower(), count=1)
            text = original
        if NEGATION.search(text) and "don't let me forget" not in text:
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
    stop = {"the", "a", "an", "my", "to", "and", "i", "it", "for", "with", "of", "on", "up", "just", "already"}
    stems = {"called": "call", "phoned": "call", "rang": "call", "paid": "pay", "sent": "send", "texted": "text",
             "emailed": "email", "bought": "buy", "booked": "book", "ordered": "order", "took": "take",
             "finished": "finish", "submitted": "submit", "cleaned": "clean", "walked": "walk", "fed": "feed",
             "watered": "water", "renewed": "renew", "returned": "return", "picked": "pick", "did": "do",
             "went": "go", "attended": "attend", "mum": "mom", "mother": "mom"}
    return {stems.get(w, w) for w in re.findall(r"[a-z']+", text.lower()) if w not in stop}
