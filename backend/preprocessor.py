"""
This file contains code for taking raw contract text and breaking it into individual clauses
"""

import nltk

nltk.download("punkt")
nltk.download("punkt_tab")

MINIMUM_CLAUSE_LENGTH = 35  # min number of chars in a clause


def clean_and_filter(raw_clauses):
    # strip whitespace from each clause and exclude very short sentences which are not clauses
    cleaned = []

    for clause in raw_clauses:
        clause = clause.strip()
        if len(clause) >= MINIMUM_CLAUSE_LENGTH:
            cleaned.append(clause)

    return cleaned


def line_is_a_numbered_section(line):
    # checks if a line starts with something like 1. or 3. or 16. etc
    parts = line.split()
    if len(parts) == 0:
        return False

    first_word = parts[0]

    # numeric style
    if first_word[:-1].isdigit() and first_word.endswith("."):
        return True

    # lettered style
    if len(first_word) == 2 and first_word[0].isalpha() and first_word.endswith("."):
        return True

    # paranthesis style
    if first_word.startswith("(") and first_word.endswith(")") and len(first_word) >= 3:
        return True

    return False


def split_by_numbered_sections(contract_text):
    lines = contract_text.splitlines()

    # count numbered section headers and remember where the first one starts
    numbered_line_count = 0
    first_section_index = None
    for i, line in enumerate(lines):
        if line_is_a_numbered_section(line.strip()):
            numbered_line_count += 1
            if first_section_index is None:
                first_section_index = i

    if numbered_line_count < 2:
        return None

    # drop any preamble (title, parties, recitals) before the first numbered section
    lines = lines[first_section_index:]

    # grouping lines into clauses, starting a new clause at each numbered line
    clauses = []
    current_clause_lines = []

    for line in lines:
        if line_is_a_numbered_section(line.strip()) and len(current_clause_lines) > 0:
            clauses.append(" ".join(current_clause_lines))
            current_clause_lines = [line]
        else:
            current_clause_lines.append(line)

    # adding last clause
    if len(current_clause_lines) > 0:
        clauses.append(" ".join(current_clause_lines))

    cleaned_clauses = clean_and_filter(clauses)
    return cleaned_clauses


def split_by_paragraphs(contract_text):
    # paragraphs are separated by blank lines
    paragraphs = contract_text.split("\n\n")

    # If there are less than 3 paras, the whole contract is just one big block of text
    if len(paragraphs) < 3:
        return None

    return clean_and_filter(paragraphs)


def split_by_sentences(contract_text):
    # if contract has no numbering and no paragraph break, nltk is used to split into sentences
    sentences = nltk.sent_tokenize(contract_text)

    sentences_per_clause = 3  # 3 sentences grouped together into one clause
    grouped_clauses = []
    current_group = []

    for sentence in sentences:
        current_group.append(sentence)
        if len(current_group) == sentences_per_clause:
            grouped_clauses.append(" ".join(current_group))
            current_group = []

    if len(current_group) > 0:
        grouped_clauses.append(" ".join(current_group))  # adding any leftover sentences

    return clean_and_filter(grouped_clauses)


def get_clauses(contract_text):
    # trying numbered sections
    clauses = split_by_numbered_sections(contract_text)
    if clauses is not None:
        return clauses

    # trying splitting by paras
    clauses = split_by_paragraphs(contract_text)
    if clauses is not None:
        return clauses

    # if above doesn't work, split by sentences
    clauses = split_by_sentences(contract_text)
    return clauses
