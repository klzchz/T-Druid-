# Email report template

A small, dependency-free script to email yourself a report with attachments. Meant to sit at the end of a pipeline (a job scanner, a metrics puller, anything mechanical that produces text you want to see without opening a terminal).

## Setup
Gmail example (works with any SMTP provider, adjust host/port):
1. Turn on 2FA on the sending account.
2. Create an [app password](https://myaccount.google.com/apppasswords) — never use your real login password here.
3. Export: `SMTP_USER`, `SMTP_PASS` (the app password), optionally `SMTP_HOST`/`SMTP_PORT`/`SMTP_FROM_NAME`.

## Example
```bash
../job-scanner/scan-jobs.py | send-report.py "This week's job matches" you@example.com ~/resume.pdf
```
