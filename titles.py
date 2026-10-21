"""Deterministic phrase extraction; no topic labels, models or dependencies.

Candidates retain source word order. Only grammatical scaffolding, optional
modifiers and verb forms are adjusted. Batch selection favours distinctive
phrases before considering alternatives to a similar title already selected.
"""
from collections import Counter
import re

WORDS = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
VERBS = dict(zip(
    "notice allow release reconnect return relax breathe imagine picture feel find welcome "
    "remember trust recognise recognize settle drift soften rest prepare open bring move "
    "listen observe explore enjoy accept embrace focus follow become let take carry leave "
    "begin enter walk step watch choose build discover acknowledge repeat pause reconnect".split(),
    "noticing allowing releasing reconnecting returning relaxing breathing imagining picturing feeling finding welcoming "
    "remembering trusting recognising recognizing settling drifting softening resting preparing opening bringing moving "
    "listening observing exploring enjoying accepting embracing focusing following becoming letting taking carrying leaving "
    "beginning entering walking stepping watching choosing building discovering acknowledging repeating pausing reconnecting".split()))
VERBS.update({"force": "forcing", "stretch": "stretching", "lower": "lowering", "raise": "raising"})
FUNCTION = set("a an the your you yourself my our their his her its to of in on at with and or "
               "as by for from is are be this that it how when if into through can will "
               "may might would could should have has do does".split())
WEAK = set("moment simply gently comfortably slowly little own next natural".split())
ENDINGS = FUNCTION - {"yourself", "you", "it", "her"}
SMALL = set("a an the and or but as at by for from in into of on to with".split())


def words(text):
    return WORDS.findall(text)


def content(text):
    # Small grammatical normalisation for similarity, retaining meaningful
    # opposites and body parts (e.g. hands/feet and slow/fast stay distinct).
    result = set()
    for word in words(text.lower()):
        if word not in FUNCTION and word not in WEAK:
            result.add(VERBS.get(word, word))
    return result


def title_case(text):
    return " ".join(word[:1].upper() + word[1:] if i == 0 or word.lower() not in SMALL
                    else word.lower() for i, word in enumerate(text.split()))


def grammatical_phrase(text):
    text = text.strip(" ,;:—–-\"“”")
    # Remove scaffolding repeatedly: 'Take a moment to begin by noticing...'.
    intro = (r"^(?:(?:please|simply|gently|now)\s+|(?:you\s+(?:can|may|might)|"
             r"begin\s+by|start\s+by|take\s+(?:a|this)\s+moment\s+to|"
             r"take\s+(?:a|this)\s+moment\s+for\s+yourself\s+to)\s+)")
    previous = None
    while text != previous:
        previous = text
        text = re.sub(intro, "", text, flags=re.I)
    # An opportunity to X is explanatory framing; X is the actual instruction.
    text = re.sub(r"^.+?\b(?:an?\s+)?opportunity\s+to\s+", "", text, flags=re.I)
    text = re.sub(r"^imagine\s+(?=\w+ing\b)", "", text, flags=re.I)
    text = re.sub(r"^if\s+", "When ", text, flags=re.I)
    text = re.sub(r"\ba little of the\b", "a little", text, flags=re.I)
    text = re.sub(r"\byour own\b", "your", text, flags=re.I)
    text = re.sub(r"\bbecome (slower|softer|calmer|quieter)\b",
                  lambda m: {"slower": "slow", "softer": "soft", "calmer": "calm", "quieter": "quiet"}[m[1].lower()],
                  text, flags=re.I)
    # Preserve negation rather than turning 'Do not force...' into 'Forcing...'.
    text = re.sub(r"^(?:do not|don't|don’t)\s+(\w+)",
                  lambda m: "Not " + VERBS.get(m[1].lower(), m[1]), text, flags=re.I)
    text = re.sub(r"^(\w+)", lambda m: VERBS.get(m[1].lower(), m[1]), text)
    return text


def phrase_candidates(text):
    """Return scored, whole-word phrases from every sentence/clause."""
    text = re.sub(r"\[pause\]", ". ", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    candidates = {}
    clauses = re.split(r"[.!?;:\n]+|\s*[—–]\s*|,\s*", text)
    for position, clause in enumerate(clauses):
        clause = clause.strip()
        if not clause:
            continue
        # A subordinate lead-in is not the instruction. The next clause is
        # independently considered, including instructions late in a paragraph.
        if re.match(r"^as you\b", clause, re.I):
            continue
        clause = re.sub(r"^(?:and|then)\s+", "", clause, flags=re.I)
        phrase = grammatical_phrase(clause)
        # Offer complete subclauses and a compact version before length fitting.
        short = re.split(r"\s+(?:if|whenever|without|as you|you['’]ve|that you)\b", phrase, maxsplit=1, flags=re.I)[0]
        compact = re.sub(r"\b(?:gentle|comfortably|simply)\b\s*", "", short, flags=re.I).strip()
        variants = [(phrase, 0), (short, 2 if short != phrase else 0),
                    (compact, 2.4 if compact != phrase else 0)]
        for variant, bonus in variants:
            # Coordination often provides a second useful phrase; prefer keeping
            # the complete first object over cutting halfway into the next one.
            first = re.split(r"\s+and\s+", variant, maxsplit=1, flags=re.I)[0]
            for part, part_bonus in ((variant, bonus), (first, bonus - 0.3)):
                tokens = words(part)
                if not tokens:
                    continue
                fitted = []
                for token in tokens[:8]:
                    if len(" ".join(fitted + [token])) > 50:
                        break
                    fitted.append(token)
                while fitted and fitted[-1].lower() in ENDINGS:
                    fitted.pop()
                if not fitted:
                    continue
                candidate = title_case(" ".join(fitted))
                keys = content(candidate)
                action = fitted[0].lower() in VERBS.values() or fitted[0].lower() == "not"
                conditional = fitted[0].lower() == "when"
                score = (5 * action + 5 * conditional + min(len(keys), 4) * 0.7 +
                         (2 if 4 <= len(fitted) <= 8 else 0) + part_bonus - position * 0.03)
                # Avoid generic setup/reassurance winning over a later instruction.
                if re.match(r"^(?:Take|Taking|There|It|You|This|A Moment)\b", candidate):
                    score -= 5
                if re.match(r"^\w+\s+(?:it|this|that)\b", candidate, re.I):
                    score -= 2  # A title should identify its object without the previous sentence.
                if re.search(r"\b(?:no need|do not|don't|don’t)\b", part, re.I) and not action:
                    score -= 2
                if len(fitted) < len(tokens):
                    score -= 1.5
                candidates[candidate] = max(score, candidates.get(candidate, float("-inf")))
    if not candidates:
        return [("Untitled Spoken Passage", 0)]
    return sorted(candidates.items(), key=lambda item: (-item[1], item[0]))


def similar(left, right):
    a, b = content(left), content(right)
    return bool(a and b and len(a & b) / len(a | b) >= 0.75)


def suggest_titles(paragraphs):
    """Use distinct source phrases without automatically suffixing collisions.

    If no source-grounded distinction exists, keep the collision visible so the
    existing editable-preview validation requires human wording, not a guess.
    """
    candidates = [phrase_candidates(text) for text in paragraphs]
    frequency = Counter(word for text in paragraphs for word in content(text))
    selected, first_titles = [], {}
    for text, options in zip(paragraphs, candidates):
        normalised = " ".join(words(re.sub(r"\[pause\]", "", text.lower(), flags=re.I)))
        def rank(option):
            title, score = option
            keys = content(title)
            specificity = sum(1 / frequency.get(word, 1) for word in keys) / max(len(keys), 1)
            collision = any(similar(title, previous) for previous in selected)
            return score + specificity * 2 - collision * 8
        title = max(options, key=rank)[0]
        title = first_titles.setdefault(normalised, title)
        selected.append(title)
    return selected


def suggest_title(text):
    return suggest_titles([text])[0]
