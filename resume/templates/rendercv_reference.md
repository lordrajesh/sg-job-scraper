# RenderCV Reference

Source: https://docs.rendercv.com/user_guide/
GitHub: https://github.com/rendercv/rendercv

## YAML Structure

```yaml
cv:
  name: "Rajesh Rajagopalan"
  headline: "Senior Data Analyst | Fraud & Risk | Data Science | Agentic AI"
  location: "Singapore"
  email: "rajesh.rajagopalan.18@gmail.com"
  phone: "+65-92317063"
  website: "https://linkedin.com/in/rajesh-rajagopalan-72b696b9"
  social_networks:
    - network: LinkedIn
      username: rajesh-rajagopalan-72b696b9

  sections:
    summary:
      - "Senior Data Analyst with 10+ years specializing in fraud detection, risk operations, and data-driven strategy across global payments and e-commerce ecosystems. Currently at Stripe's Risk Operations team. Previously led fraud prevention initiatives at Microsoft protecting $20B+ annually. Expert in SQL, Python, Power BI, and Azure ML. MS in Business Analytics from NUS."

    experience:
      - company: "Stripe"
        position: "Senior Data Analyst — Risk & Fraud Pattern Ops"
        start_date: "2025-01"
        end_date: "present"
        location: "Singapore"
        summary: "Analyze complex fraud and abuse patterns across Stripe's global payments ecosystem."
        highlights:
          - "Develop data-driven frameworks to detect emerging fraud vectors and support investigation, triage, and policy response"
          - "Build and maintain dashboards tracking fraud trends and measuring intervention effectiveness"
          - "Collaborate with Credit, Strategy, Product, Engineering, and Operations partners"

      - company: "Microsoft"
        position: "Senior Data Scientist — Risk Strategy & Fraud Prevention"
        start_date: "2021-01"
        end_date: "2025-01"
        location: "Singapore"
        summary: "Led enterprise-scale ML and fraud platforms across Azure, E-commerce, M365, and Copilot."
        highlights:
          - "Contributed to approximately $2.4B saved annually from payment fraud across e-commerce platforms"
          - "Implemented ML frameworks resulting in $20B saved from payment fraud annually"
          - "Drove integration of Gen AI technologies using Azure Foundry, Copilot, and OpenAI"

      - company: "Tata Consultancy Services"
        position: "Risk Systems Engineer"
        start_date: "2013-01"
        end_date: "2016-01"
        location: "Chennai, India"
        summary: "Designed and developed Risk Assessment products for AIG and AXA."
        highlights:
          - "Built predictive models to assess insured property losses — achieved 40% reduction in client cost and time"
          - "Supervised BI division helping clients identify business trends in Risk Assessment"
          - "Built Claims and Benefits platform achieving 30% cost reduction"

    education:
      - institution: "National University of Singapore"
        area: "Business Analytics"
        degree: "Master's"
        start_date: "2017-01"
        end_date: "2017-12"
        location: "Singapore"
        highlights:
          - "Specialization: Quantitative Risk Management, Marketing & Consumer Analytics"
          - "GPA: 4.6/5"

      - institution: "Anna University"
        area: "Electronics and Communication Engineering"
        degree: "Bachelor's"
        start_date: "2013-01"
        end_date: "2013-06"
        location: "Chennai, India"
        highlights:
          - "First Class, GPA: 8.1/10"
          - "Vice President, Enactus; Group Ambassador of India, Enactus WC 2012"

    skills:
      - label: "Data & BI"
        details: "SQL, Power BI, Tableau, Python, Azure Synapse, Cosmos DB"
      - label: "Machine Learning"
        details: "Scikit-Learn, XGBoost, PyTorch, TensorFlow, Azure ML, MLFlow"
      - label: "Programming & Tools"
        details: "Python, PySpark, C#, Git, Docker, Azure, Azure Foundry"
      - label: "Certifications"
        details: "Microsoft Azure Fundamentals, Microsoft Azure AI Fundamentals, ITIL Foundation"
      - label: "Languages"
        details: "English, Spanish, Hindi, Tamil"

    projects:
      - name: "Singapore Job Market Intelligence"
        date: "2026"
        highlights:
          - "Built end-to-end pipeline scraping 7 sources (LinkedIn, Indeed, JobsDB, Lever, Greenhouse), 1000+ jobs"
          - "Multi-signal salary estimation engine (seniority, company tier, role category, visa eligibility)"
          - "Astro.js + Tailwind CSS frontend with Chart.js analytics"
          - "3-layer job deduplication system (URL canonicalization, exact matching, fuzzy 70%+ similarity)"
        url: "#"

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
pip install "rendercv[full]"              # Install
rendercv new "Rajesh Rajagopalan"       # Generate starter YAML
rendercv render cv.yaml                  # Render to PDF + PNG + MD + HTML
rendercv render cv.yaml --watch          # Auto-render on save
```
