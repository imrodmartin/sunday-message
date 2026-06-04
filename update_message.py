#!/usr/bin/env python3
"""
update_message.py
Reads the latest "Title and scripture" / "Scripture and Title" email from Gmail
and updates index.html.
Requires env vars: GMAIL_USER, GMAIL_APP_PASSWORD
"""
import imaplib
import email
from email.utils import parsedate_to_datetime
import re
import os

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]


def fetch_email_body():
    with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        mail.select('"[Gmail]/All Mail"')
        _, msg_ids = mail.search(
            None,
            'OR SUBJECT "Scripture and Title" SUBJECT "Title and scripture"'
        )
        if not msg_ids[0]:
            raise ValueError("No emails found with subject 'Scripture and Title' or 'Title and scripture'")

        ids = msg_ids[0].split()

        # Fetch INTERNALDATE for all matches and pick the newest
        best_id = None
        best_date = None
        for msg_id in ids:
            _, date_data = mail.fetch(msg_id, "(INTERNALDATE)")
            date_str = date_data[0].decode()
            match = re.search(r'INTERNALDATE "([^"]+)"', date_str)
            if match:
                msg_date = parsedate_to_datetime(match.group(1))
                if best_date is None or msg_date > best_date:
                    best_date = msg_date
                    best_id = msg_id

        if best_id is None:
            raise ValueError("Could not determine email dates")

        print(f"Fetching email id={best_id} date={best_date}")
        _, msg_data = mail.fetch(best_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode("utf-8", errors="ignore")
        return msg.get_payload(decode=True).decode("utf-8", errors="ignore")


def parse_title(body):
    print("--- EMAIL BODY ---")
    print(body[:500])
    print("--- END BODY ---")

    # Try: quoted title with closing quote (straight or curly), possibly spanning lines
    match = re.search(r'[""]([^""]+)[""]', body, re.DOTALL)
    if match:
        # Grab only the first line of the match (in case it spans multiple lines)
        title = match.group(1).split('\n')[0].strip()
        if title:
            return title

    # Fallback: opening quote with no closing — grab to end of that line
    match = re.search(r'[""]([^\n""]+)', body)
    if match:
        return match.group(1).strip()

    # Fallback: unquoted body like "Scripture, Title" or "Title, Scripture".
    # Take the first non-empty line, strip the scripture reference out, and
    # what remains (minus surrounding commas/quotes/whitespace) is the title.
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        title = re.sub(
            r'\b(?:\d\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\s+\d+:\d+(?:[–\-]\d+)?\b',
            '', line, count=1,
        ).strip()
        title = title.strip(' ,\t"“”\'')
        if title:
            return title
        break

    raise ValueError("No quoted title found in email body")


def parse_scripture(body):
    # Match patterns like "John 11:25", "1 Corinthians 13:4-7", "Song of Solomon 2:1"
    match = re.search(
        r'\b(?:\d\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\s+\d+:\d+(?:[–\-]\d+)?\b',
        body
    )
    if not match:
        raise ValueError("No scripture reference found in email body")
    return match.group(0).strip()


def update_html(title, scripture, html_path="index.html"):
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r"<!-- TITLE_START -->.*?<!-- TITLE_END -->",
        f"<!-- TITLE_START -->{title}<!-- TITLE_END -->",
        content, flags=re.DOTALL,
    )
    content = re.sub(
        r"<!-- SCRIPTURE_START -->.*?<!-- SCRIPTURE_END -->",
        f"<!-- SCRIPTURE_START -->{scripture}<!-- SCRIPTURE_END -->",
        content, flags=re.DOTALL,
    )
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {title!r} | {scripture!r}")


if __name__ == "__main__":
    body = fetch_email_body()
    title = parse_title(body)
    scripture = parse_scripture(body)
    update_html(title, scripture)
