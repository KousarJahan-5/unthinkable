import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted resume or job description text:
    - Normalize Unicode (NFKD)
    - Fix hyphenated linebreaks (e.g., 'engi-\nneer' -> 'engineer')
    - Replace tabs and special spaces with standard space
    - Collapse excessive blank lines and whitespace
    - Remove non-printable / control characters while preserving newlines
    """
    if not text:
        return ""

    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Replace carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Fix broken hyphenated line breaks
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # Replace weird bullet points and decorative symbols with standard bullet
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25CF\u25CB\u25A0\u25A1]', '\n- ', text)

    # Remove non-printable control characters (except newline, tab)
    text = re.sub(r'[^\x20-\x7E\n\t]', ' ', text)

    # Replace multiple spaces with a single space on each line
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]

    # Collapse consecutive blank lines (max 2)
    cleaned_lines = []
    blank_count = 0
    for line in lines:
        if not line:
            blank_count += 1
            if blank_count <= 1:
                cleaned_lines.append("")
        else:
            blank_count = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def extract_emails(text: str) -> list[str]:
    """Extract email addresses using RFC-compliant pattern."""
    if not text:
        return []
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    matches = re.findall(email_pattern, text)
    return list(dict.fromkeys([m.lower() for m in matches]))


def extract_phone_numbers(text: str) -> list[str]:
    """Extract phone numbers with various international and local formats."""
    if not text:
        return []
    # Matches patterns like +1 (555) 123-4567, 555-123-4567, +91 98765 43210, etc.
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    matches = re.findall(phone_pattern, text)
    # Clean matches
    clean_phones = []
    for p in matches:
        p_clean = re.sub(r'\s+', ' ', p.strip())
        if len(re.sub(r'\D', '', p_clean)) >= 10:
            clean_phones.append(p_clean)
    return list(dict.fromkeys(clean_phones))


def extract_urls(text: str) -> list[str]:
    """Extract LinkedIn, GitHub, or portfolio URLs."""
    if not text:
        return []
    url_pattern = r'(?:https?://)?(?:www\.)?(?:linkedin\.com/in/[a-zA-Z0-9_-]+|github\.com/[a-zA-Z0-9_-]+|[a-zA-Z0-9_-]+\.(?:dev|io|me|ai|com)/[a-zA-Z0-9_-]*)'
    matches = re.findall(url_pattern, text, re.IGNORECASE)
    return list(dict.fromkeys(matches))
