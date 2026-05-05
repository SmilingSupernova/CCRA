"""
extract entities: spaCy NER, filtered down to things that matter in a contract
extract keyphrases: YAKE keyphrases, with legal boilerplate filtered out
"""

import spacy
import yake

nlp = spacy.load("en_core_web_sm")

# spaCy entity labels we keep, mapped to the friendly name we show in the UI
ENTITY_TYPES = {
    "ORG": "Organization",
    "PERSON": "Person",
    "DATE": "Date",
    "MONEY": "Money",
    "GPE": "Location",
    "LAW": "Law",
}

# Words and phrases spaCy keeps mistagging as entities. Compared lowercase, after we strip a leading "the/a/an" and a trailing "'s".
BLOCKLIST = {
    # contract roles
    "licensor", "licensee", "provider", "distributor", "supplier",
    "client", "customer", "vendor", "party", "parties", "territory",
    "contractor", "buyer", "seller", "company", "software", "services",
    # common contract phrases
    "agreement", "this agreement", "effective date", "agreement date",
    "expiration date", "renewal term", "term", "initial term",
    "license grant", "governing law", "audit rights",
    "change of control", "source code escrow",
    "exhibit a", "exhibit b", "schedule a", "work order",
    "confidential information",
}

# Boilerplate words that YAKE picks up but that aren't useful as keyphrases
STOPWORDS = {
    "party", "parties", "agreement", "contract", "shall", "hereby",
    "herein", "thereof", "hereof", "pursuant", "accordance", "terms",
    "conditions", "provision", "provisions", "section", "article",
}

yake_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.7, top=5)

# Returns a list of {"text", "type"} dicts for the entities found in a clause.
def extract_entities(clause_text):
    # a lot of clauses starts with something like "5. Termination. ..."
    # if spaCy sees that, it picks up the heading word ("Termination") as an
    # entity which is not what we want. so we cut that part off first before sending the text to spaCy.

    body = clause_text.lstrip()
    first_dot = body.find(". ")
    if 0 < first_dot <= 3:
        prefix = body[:first_dot]

        # only treat it as a heading if the prefix is something like "5" or "a"
        if prefix.isdigit() or (len(prefix) == 1 and prefix.isalpha()):
            second_dot = body.find(". ", first_dot + 2)
            if second_dot != -1:
                heading = body[first_dot + 2:second_dot]
                # heading should starts with capital letter and not be too long
                if heading and heading[0].isupper() and len(heading) <= 50:
                    body = body[second_dot + 2:]

    # running spaCy on cleaned body
    doc = nlp(body)

    entities = []
    seen = set()  # tracks what are already added so we dont duplicate

    for ent in doc.ents:
        if ent.label_ not in ENTITY_TYPES:
            continue

        name = ent.text.strip()

        if "(" in name or ")" in name:
            name = name.replace("(", "").replace(")", "")
            name = " ".join(name.split())  # collapse the double spaces left behind
        if not name:
            continue

        if name.isupper():
            continue

        # we need a normalized version of the name
        key = name.lower()
        if key.endswith("."):
            key = key[:-1]
        if key.startswith("the "):
            key = key[4:]
        elif key.startswith("a "):
            key = key[2:]
        elif key.startswith("an "):
            key = key[3:]
        if key.endswith("'s") or key.endswith("s'"):
            key = key[:-2]

        for tail in (" of this agreement", " of the agreement",
                     " under this agreement", " under the agreement"):
            if key.endswith(tail):
                key = key[: -len(tail)]
                break
        key = key.strip()

        # drop if its empty, blocklisted, or already seen in this clause
        if not key or key in BLOCKLIST or key in seen:
            continue

        # spaCy might get confused on phrases like "State of Delaware"
        # it tags them as ORG when they are a location, rather than throwing them away, label them to location.
        friendly_type = ENTITY_TYPES[ent.label_]
        if ent.label_ == "ORG" and (
            key.startswith("state of ")
            or key.startswith("commonwealth of ")
            or key.startswith("district of ")
        ):
            friendly_type = "Location"

        seen.add(key)
        # keep the original name but use the cleaned-up type
        entities.append({"text": name, "type": friendly_type})

    return entities


def extract_keyphrases(clause_text):
    # Returns a list of important phrases pulled from the clause.

    if len(clause_text.split()) < 5:
        return []

    # YAKE gives back tuples of (phrase, score).
    raw = yake_extractor.extract_keywords(clause_text)

    keyphrases = []
    for phrase, _score in raw:
        phrase = phrase.strip()
        words = phrase.lower().split()

        # if every word in the phrase is boilerplate then the phrase has no real meaning, so we drops it. but if even one word is useful, keep it
        if all(w in STOPWORDS for w in words):
            continue
        keyphrases.append(phrase)

    return keyphrases
