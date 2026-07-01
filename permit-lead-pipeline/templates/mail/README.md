# Mail / outreach templates (placeholders)

These are **placeholder templates** the outreach + mailer modules render per lead.
They use `{{merge_field}}` syntax. Edit the copy freely — no code change needed.

Direct **physical mail is the compliant automated channel** (exempt from TCPA),
which is why the mailer targets postcards/letters via a print-and-mail partner
(see `src/permitlead/mailer.py`). Email/SMS drafts remain **contractor-sent**.

## Merge fields
| field | example |
|---|---|
| `{{owner}}` | Delgado |
| `{{owner_full}}` | R. Delgado |
| `{{address}}` | 45 Onota St |
| `{{town}}` | Pittsfield |
| `{{trade}}` | solar |
| `{{hook}}` | since the roof will be freshly done, it's the ideal time to add solar |
| `{{contractor_name}}` | Berkshire Photovoltaic Services |
| `{{contractor_phone}}` | (413) 664-0152 |

## Files
- `postcard_front.txt` — headline side
- `postcard_back.txt` — message + CTA side (address block added by the mail API)
- `letter.txt` — #10 letter body
- `email.txt` — contractor-sent email (subject on first line)
- `sms.txt` — contractor-sent SMS (≤320 chars)
