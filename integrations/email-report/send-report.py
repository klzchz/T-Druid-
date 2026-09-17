#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generic template: send yourself (or a small list of people) a periodic
plain-text report by email, optionally with file attachments (a resume, a
generated PDF, whatever). Meant to be the last step of a pipeline — e.g. a
job scanner or a daily-metrics script pipes its findings in here.

Configure via env vars (a .env file, never committed):
    SMTP_HOST   default smtp.gmail.com
    SMTP_PORT   default 587
    SMTP_USER   the sending address
    SMTP_PASS   an app password, not your normal login password
    SMTP_FROM_NAME  display name for the From: header

Usage:
    echo "report body here" | send-report.py "Subject line" you@example.com [attachment1 attachment2 ...]
"""
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr


def env(name, default=""):
    return os.environ.get(name, default)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    subject, to = sys.argv[1], sys.argv[2]
    attachments = sys.argv[3:]
    body = sys.stdin.read()

    user, password = env("SMTP_USER"), env("SMTP_PASS")
    if not (user and password):
        sys.exit("SMTP_USER / SMTP_PASS not set — nothing sent")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((env("SMTP_FROM_NAME", "Automated report"), user))
    msg["To"] = to
    msg.set_content(body)

    for path in attachments:
        if not os.path.exists(path):
            print(f"skipping missing attachment: {path}", file=sys.stderr)
            continue
        with open(path, "rb") as f:
            data = f.read()
        ext = os.path.splitext(path)[1].lstrip(".").lower() or "octet-stream"
        maintype = "application"
        msg.add_attachment(data, maintype=maintype, subtype=ext, filename=os.path.basename(path))

    with smtplib.SMTP(env("SMTP_HOST", "smtp.gmail.com"), int(env("SMTP_PORT", "587")), timeout=30) as s:
        s.starttls(context=ssl.create_default_context())
        s.login(user, password)
        s.send_message(msg)
    print(f"sent to {to}")


if __name__ == "__main__":
    main()
