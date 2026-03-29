# RenderCV Reference

Source: https://docs.rendercv.com/user_guide/
GitHub: https://github.com/rendercv/rendercv

## YAML Structure

```yaml
cv:
  name: "Irmin Corona"
  headline: "Data Analyst & Web Developer"
  location: "Hong Kong"
  email: "email@example.com"
  phone: "+852-XXXX-XXXX"
  website: "https://climbthesearches.com"
  social_networks:
    - network: LinkedIn
      username: irmin-corona
    - network: GitHub
      username: ircorona

  sections:
    summary:
      - "5+ years experience in data analysis, fraud detection, and web development..."

    experience:
      - company: "Company Name"
        position: "Senior Data Analyst"
        start_date: "2022-01"
        end_date: "present"
        location: "Mexico City, Mexico"
        summary: "Led data analytics team..."
        highlights:
          - "Built Power BI dashboards reducing reporting time by 60%"
          - "Developed Python ETL pipelines processing 1M+ records daily"

    education:
      - institution: "University Name"
        area: "Computer Science"
        degree: "Bachelor's"
        start_date: "2015-08"
        end_date: "2019-06"
        location: "Mexico"
        highlights:
          - "Graduated with honors"

    skills:
      - label: "Data & BI"
        details: "Power BI, SQL, Python, Excel, Snowflake, dbt"
      - label: "Web Development"
        details: "PHP, JavaScript, WordPress, HTML/CSS, React"
      - label: "Tools & Cloud"
        details: "Git, Docker, Azure, AWS, Power Automate"
      - label: "Languages"
        details: "English (fluent), Spanish (native), Mandarin (basic)"

    projects:
      - name: "HK Job Market Dashboard"
        date: "2026"
        highlights:
          - "Built end-to-end pipeline scraping 7 sources, 2000+ jobs"
          - "Astro.js frontend with salary estimation engine"
        url: "https://climbthesearches.com/hk-jobs/"

design:
  theme: engineeringresumes  # or: classic, sb2nov, harvard, opal
  page:
    size: letterpaper
    top_margin: "1.2 cm"
    bottom_margin: "1.2 cm"
    left_margin: "1.2 cm"
    right_margin: "1.2 cm"
  colors:
    primary: "#004f90"
    text: "#333333"
```

## 9 Entry Types

| Type | Required Fields | Use For |
|------|----------------|---------|
| ExperienceEntry | company, position | Work experience |
| EducationEntry | institution, area | Education |
| NormalEntry | name | Projects, certifications |
| PublicationEntry | title, authors | Papers, publications |
| OneLineEntry | label, details | Skills (key: value format) |
| BulletEntry | bullet | Simple bullet lists |
| NumberedEntry | number | Numbered achievements |
| ReversedNumberedEntry | reversed_number | Reverse-numbered lists |
| TextEntry | (plain text) | Summary paragraphs |

## Date Formats

- Range: `start_date: "2022-01"` + `end_date: "present"`
- Single: `date: "2026-03"`
- Format: YYYY-MM or YYYY

## Text Formatting

- **Bold**: `**text**`
- *Italic*: `*text*`
- Links: `[text](url)`
- Code: `` `code` ``

## Available Themes

1. **engineeringresumes** — Clean, ATS-friendly, single-column
2. **classic** — Traditional, professional
3. **sb2nov** — Popular LaTeX resume style
4. **harvard** — Academic style
5. **moderncv** — Modern with sidebar
6. **opal** — Minimalist
7. **ember** — Contemporary
8. **ink** — Creative
9. **engineeringclassic** — Engineering-focused

## ATS Tips

- Use standard section names: Experience, Education, Skills
- Avoid tables, columns, graphics
- Use `engineeringresumes` or `classic` theme for best ATS parsing
- Include keywords from the job posting in highlights
- Quantify achievements: "Reduced X by Y% in Z months"

## Commands

```bash
pip install "rendercv[full]"        # Install
rendercv new "Irmin Corona"         # Generate starter YAML
rendercv render cv.yaml             # Render to PDF + PNG + MD + HTML
rendercv render cv.yaml --watch     # Auto-render on save
```
