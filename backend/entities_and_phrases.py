"""
extract entities: spaCy NER, filtered down to things that matter in a contract
extract keyphrases: YAKE keyphrases, with legal boilerplate filtered out
"""

import re

import spacy
import yake

from preprocessor import line_is_a_numbered_section

nlp = spacy.load("en_core_web_sm")

# spaCy entity labels we keep, mapped to the name shown in the UI
ENTITY_TYPES = {
    "ORG": "Organization",
    "PERSON": "Person",
    "DATE": "Date",
    "MONEY": "Money",
    "GPE": "Location",
    "LAW": "Law",
}

# Words and phrases spaCy keeps mistagging as entities
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

    # generic defined-term jargon
    "licensed software", "licensed territory", "license term", "license",
    "third party", "proprietary information", "intellectual property",
    "products", "product", "deliverables", "work product",
    "specifications", "documentation",
}

# product name suffixes that indicate a mislabeled product
PRODUCT_SUFFIXES = {
    "software", "system", "platform", "service", "services",
    "product", "application",
}

# Date entities that are just cadence adjectives
DATE_BLOCKLIST = {
    "annual", "monthly", "weekly", "daily", "quarterly", "yearly",
    "biennial", "semi-annual", "semi-annually",
}

# address fragment tokens spaCy often mistags as a Person
ADDRESS_WORDS = {
    "suite", "phd", "ph.d", "dr", "drive", "street", "avenue", "blvd",
    "boulevard", "road", "rd", "floor", "fl", "apt", "unit", "ave", "st",
}
ADDRESS_PREFIXES = ("suite ", "apt ", "unit ", "floor ", "fl ")

INDUSTRY_SUFFIXES = (" industry", " sector", " market", " marketplace")

SUBSECTION_PREFIX_RE = re.compile(r"^\d+\.\d+\.?")

# Boilerplate words
STOPWORDS = {
    "party", "parties", "agreement", "contract", "shall", "hereby",
    "herein", "thereof", "hereof", "pursuant", "accordance", "terms",
    "conditions", "provision", "provisions", "section", "article",
}

yake_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.7, top=5)

# common written out numbers that spaCy sometimes flags as entities
NUMBER_WORDS = {
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand",
    "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five",
    "twenty-six", "twenty-seven", "twenty-eight", "twenty-nine",
    "thirty-one", "thirty-six", "forty-five", "sixty-five", "ninety-nine",
}

# prefixes that signal a cross-reference rather than a real entity
XREF_PREFIXES = ("section ", "schedule ", "exhibit ", "article ", "paragraph ")


# Checks contract's preamble and pulls out the parties and defined terms
def parse_preamble(contract_text):
    known_parties = set()
    defined_terms = set()

    # find where the first numbered section starts so we only preamble is scanndd.
    lines = contract_text.splitlines()
    cutoff_char = None
    running = 0
    for line in lines:
        if line_is_a_numbered_section(line.strip()):
            cutoff_char = running
            break
        running += len(line) + 1  # +1 for the newline we split on

    if cutoff_char is None or cutoff_char == 0:
        preamble = contract_text[:1500]
    else:
        preamble = contract_text[:cutoff_char]

    quote_pairs = [('("', '")'), ("('", "')"), ('(“', '”)')]

    for opener, closer in quote_pairs:
        pos = 0
        while True:
            start = preamble.find(opener, pos)
            if start == -1:
                break
            end = preamble.find(closer, start + len(opener))
            if end == -1:
                break

            term = preamble[start + len(opener):end].strip()
            if term:
                defined_terms.add(term.lower())

            # walk backwards from the opening paren to grab the company name
            before = preamble[:start].rstrip()
            words = before.split()
            party_words = []
            for w in reversed(words):
                clean = w.rstrip(",;:.")
                if not clean:
                    break
                if clean[0].isupper() or clean.lower() in {"and", "of", "&"}:
                    party_words.insert(0, clean)
                else:
                    break

            # trim leading connector words like "and" or "of"
            while party_words and party_words[0].lower() in {"and", "of", "&"}:
                party_words.pop(0)

            if party_words:
                known_parties.add(" ".join(party_words).lower())

            pos = end + len(closer)

    return known_parties, defined_terms


# Returns a list of {"text", "type"} dicts for the entities found in a clause.
# known_parties and defined_terms come from parse_preamble and are used to
# correct spaCy's mistakes on contract-specific names.
def extract_entities(clause_text, known_parties=None, defined_terms=None):
    known_parties = known_parties or set()
    defined_terms = defined_terms or set()

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

    # also strip sub-section numbers glued to the first word (e.g. "2.5.Licensee")
    body = SUBSECTION_PREFIX_RE.sub("", body.lstrip(), count=1)

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

        # drop garbage fragments: too short or no vowels (e.g. "fon", "xy")
        if len(key) < 3 or not any(ch in "aeiou" for ch in key):
            continue

        # drop mislabeled product names like "K9 Store Software"
        last_word = key.rsplit(" ", 1)[-1] if " " in key else key
        if last_word in PRODUCT_SUFFIXES and " " in key:
            continue

        # drop DATE entities that are really cadence adjectives ("annual")
        if ent.label_ == "DATE" and key in DATE_BLOCKLIST:
            continue

        # drop address fragments mistagged as Person ("Suite", "W. Wacker")
        if key in ADDRESS_WORDS:
            continue
        if any(key.startswith(p) for p in ADDRESS_PREFIXES):
            continue
        key_words = key.split()
        if len(key_words) == 2 and len(key_words[0]) == 2 and key_words[0].endswith("."):
            if key_words[0][0].isalpha():
                continue

        # drop general industry references like "the cannabis industry"
        if any(key.endswith(suf) for suf in INDUSTRY_SUFFIXES):
            continue

        # drop written-out numbers like "eighteen" or "twenty-four"
        if " " not in key and key in NUMBER_WORDS:
            continue

        # drop cross-references like "section 4" or "exhibit b"
        is_xref = False
        for prefix in XREF_PREFIXES:
            if key.startswith(prefix):
                rest = key[len(prefix):].split()
                if rest:
                    tok = rest[0].rstrip(".,;:)")
                    if tok.isdigit() or (len(tok) == 1 and tok.isalpha()):
                        is_xref = True
                        break
        if is_xref:
            continue

        # if this entity matches a known party (or is part of one), it's
        # definitely an organization no matter what spaCy guessed
        forced_org = False
        for party in known_parties:
            if key == party or (key and key in party.split()):
                forced_org = True
                break
        if not forced_org:
            for party in known_parties:
                if key in party:
                    forced_org = True
                    break

        # otherwise, defined terms like "Platform" or "Effective Date" are
        # contract jargon, not real-world entities
        if not forced_org and key in defined_terms:
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

        if forced_org:
            friendly_type = "Organization"

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

        if all(w in STOPWORDS for w in words):
            continue
        keyphrases.append(phrase)

    return keyphrases
