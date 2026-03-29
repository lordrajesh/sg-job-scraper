# Resume Workflow

Automated resume tailoring pipeline: job posting → tailored resume → outreach.

## Folder Structure

```
resume/
├── master/           # Master resume (YAML source + PDF)
│   └── irmin_corona_cv.yaml   ← upload here when ready
├── tailored/         # Job-specific versions (auto-generated)
│   └── {company}_{role}_{date}/
│       ├── resume.yaml
│       ├── resume.pdf
│       └── job_posting.txt
├── templates/        # RenderCV themes + reference docs
│   └── rendercv_reference.md
└── outreach/         # Email tracking + Hunter.io contacts
    └── tracker.csv
```

## Workflow (planned)

1. Find a matching job in the HK Jobs dashboard
2. Feed the job posting URL or description
3. System auto-tailors resume YAML (keywords, skills emphasis, experience framing)
4. RenderCV renders to PDF
5. Hunter.io finds the recruiter contact
6. Send personalized outreach email

## Tool: RenderCV

- Write resume as YAML → render to PDF with professional typography
- Install: `pip install "rendercv[full]"` (requires Python 3.12+)
- Create: `rendercv new "Irmin Corona"`
- Render: `rendercv render irmin_corona_cv.yaml`
- Themes: classic, moderncv, engineeringresumes, sb2nov, harvard, opal, ember
