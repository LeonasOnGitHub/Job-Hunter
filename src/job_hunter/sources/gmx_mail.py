
import hashlib
import imaplib
import logging
import os
import re

from datetime import datetime, timedelta
from email import message_from_bytes
from email.header import decode_header
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)

from job_hunter.models import Job

logger = logging.getLogger(__name__)

IMAP_SERVER = "imap.gmx.net"
IMAP_PORT = 993

SOURCE_DOMAINS = {
    "stepstone": ("stepstone.",),
    "indeed": ("indeed.",),
    "linkedin": ("linkedin.com",),
    "kununu": ("kununu.",),
    "goodjobs": ("goodjobs.eu",),
}

JOB_URL_MARKERS = (
    "stellenangebot",
    "stellenangebote",
    "stellenanzeige",
    "viewjob",
    "/jobs/",
    "/job/",
    "/position/",
    "/career/",
    "jobdetails",
)

IGNORED_LINK_TEXT = {
    "unsubscribe",
    "abmelden",
    "datenschutz",
    "impressum",
    "mehr erfahren",
    "jetzt bewerben",
    "alle jobs ansehen",
    "job alerts verwalten",
    "einstellungen",
}


class MailHTMLParser(HTMLParser):
    """Extract readable text and links from HTML emails."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text_parts = []
        self.links = []
        self.current_href = None
        self.current_anchor_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a":
            self.current_href = attrs.get("href")
            self.current_anchor_text = []

        if tag in {"br", "p", "div", "tr", "li", "td"}:
            self.text_parts.append("\n")

    def handle_data(self, data):
        self.text_parts.append(data)

        if self.current_href:
            self.current_anchor_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current_href:
            self.links.append(
                (
                    self.current_href,
                    " ".join(self.current_anchor_text).strip(),
                )
            )
            self.current_href = None
            self.current_anchor_text = []

        if tag in {"p", "div", "tr", "li"}:
            self.text_parts.append("\n")

    @property
    def text(self):
        return re.sub(
            r"\n{3,}",
            "\n\n",
            " ".join(self.text_parts),
        ).strip()


def _decode_header(value: str | None) -> str:
    if not value:
        return ""

    parts = decode_header(value)
    result = []

    for content, encoding in parts:
        if isinstance(content, bytes):
            result.append(
                content.decode(encoding or "utf-8", errors="replace")
            )
        else:
            result.append(content)

    return "".join(result)


def _extract_body(message) -> tuple[str, list[tuple[str, str]]]:
    plain_text = ""
    html_text = ""
    links = []

    for part in message.walk():
        if part.get_content_disposition() == "attachment":
            continue

        content_type = part.get_content_type()

        if content_type not in {"text/plain", "text/html"}:
            continue

        try:
            content = part.get_content()
        except Exception:
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            content = payload.decode(
                part.get_content_charset() or "utf-8",
                errors="replace",
            )

        if content_type == "text/plain":
            plain_text += "\n" + content

        elif content_type == "text/html":
            parser = MailHTMLParser()
            parser.feed(content)
            html_text += "\n" + parser.text
            links.extend(parser.links)

    body = plain_text.strip() or html_text.strip()

    if not links:
        for url in re.findall(r"https?://[^\s<>\"']+", body):
            links.append((url.rstrip(".,);"), ""))

    return body, links


def _detect_source(sender: str, subject: str, body: str) -> str | None:
    text = f"{sender} {subject} {body[:2000]}".lower()

    for source, domains in SOURCE_DOMAINS.items():
        if any(domain in text for domain in domains):
            return source

    return None


def _clean_url(url: str) -> str:
    parts = urlsplit(url.strip())

    tracking_parameters = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "utm_term",
        "trk",
        "trackingid",
    }

    query = [
        (key, value)
        for key, value in parse_qsl(parts.query)
        if key.lower() not in tracking_parameters
    ]

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query),
            "",
        )
    )


def _is_job_link(url: str, anchor_text: str) -> bool:
    parts = urlsplit(url)

    if parts.scheme not in {"http", "https"}:
        return False

    if not parts.netloc:
        return False

    text = anchor_text.lower().strip()

    if text in IGNORED_LINK_TEXT:
        return False

    if any(marker in url.lower() for marker in JOB_URL_MARKERS):
        return True

    return False


def _email_date(message) -> datetime | None:
    try:
        return parsedate_to_datetime(message["Date"])
    except (TypeError, ValueError):
        return None


def _make_job(
    source: str,
    title: str,
    url: str,
    body: str,
    published_at: datetime | None,
) -> Job:
    clean_url = _clean_url(url)

    job_id = hashlib.sha256(
        clean_url.encode("utf-8")
    ).hexdigest()[:20]

    return Job(
        id=job_id,
        title=title or "Titel nicht erkannt",
        company="Nicht angegeben",
        location="Nicht angegeben",
        url=clean_url,
        description=body[:8000],
        source=source,
        published_at=published_at,
    )


def fetch_gmx_alert_jobs() -> list[Job]:
    """
    Fetch unread job-alert emails from GMX via IMAP.

    Emails are marked as read after successful extraction.
    The returned jobs use the common Job data model.
    """

    username = os.getenv("GMX_EMAIL")
    password = os.getenv("GMX_PASSWORD")

    if not username:
        raise RuntimeError("GMX_EMAIL is not configured.")

    if not password:
        raise RuntimeError("GMX_PASSWORD is not configured.")

    jobs = []
    mail = None

    try:
        mail = imaplib.IMAP4_SSL(
            IMAP_SERVER,
            IMAP_PORT,
            timeout=30,
        )

        mail.login(username, password)

        status, _ = mail.select("INBOX")

        if status != "OK":
            raise RuntimeError("Could not open GMX inbox.")

        status, data = mail.uid("search", None, "UNSEEN")

        if status != "OK":
            raise RuntimeError("Could not search GMX inbox.")

        message_uids = data[0].split() if data and data[0] else []

        logger.info(
            "Found %s unread emails in GMX inbox.",
            len(message_uids),
        )

        for uid in message_uids:
            status, messages = mail.uid(
                "fetch",
                uid,
                "(RFC822)",
            )

            if status != "OK" or not messages:
                logger.warning("Could not fetch email UID %s.", uid)
                continue

            raw_email = next(
                (
                    item[1]
                    for item in messages
                    if isinstance(item, tuple)
                ),
                None,
            )

            if not raw_email:
                continue

            message = message_from_bytes(raw_email)

            sender = _decode_header(message.get("From"))
            subject = _decode_header(message.get("Subject"))
            body, links = _extract_body(message)

            source = _detect_source(sender, subject, body)

            if source is None:
                logger.info(
                    "Ignoring email from unknown job source: %s",
                    sender,
                )
                continue

            published_at = _email_date(message)
            extracted = []

            for url, anchor_text in links:
                if not _is_job_link(url, anchor_text):
                    continue

                title = anchor_text.strip() or subject.strip()

                if len(title) < 5:
                    continue

                extracted.append(
                    _make_job(
                        source=source,
                        title=title,
                        url=url,
                        body=body,
                        published_at=published_at,
                    )
                )

            # Remove duplicate links within the same email.
            unique_jobs = {
                job.id: job
                for job in extracted
            }

            jobs.extend(unique_jobs.values())

            logger.info(
                "%s: extracted %s jobs from email '%s'.",
                source,
                len(unique_jobs),
                subject,
            )

            # Mark the processed email as read.
            # This prevents it from being imported again.
            mail.uid(
                "store",
                uid,
                "+FLAGS",
                "(\\Seen)",
            )

        return list({
            job.id: job
            for job in jobs
        }.values())

    except imaplib.IMAP4.error as exc:
        raise RuntimeError(
            f"GMX IMAP authentication or access failed: {exc}"
        ) from exc

    finally:
        if mail is not None:
            try:
                mail.logout()
            except Exception:
                pass
