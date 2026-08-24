import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

PDF_SAMPLES = [
    {
        "filename": "Alex_Chen_Senior_AI_FullStack.pdf",
        "title": "Alex Chen - Senior Full-Stack AI Engineer",
        "sections": [
            ("Alex Chen", "San Francisco, CA | alex.chen@techmail.dev | +1 (415) 555-0192 | linkedin.com/in/alexchen-ai"),
            ("Professional Summary", "Staff / Senior Full-Stack AI Engineer with 6+ years of experience designing and deploying enterprise GenAI systems, high-throughput FastAPI microservices, and React TypeScript web platforms. Led architecture for RAG systems serving 2M+ monthly queries."),
            ("Technical Skills", "<b>Languages:</b> Python, TypeScript, JavaScript, SQL, C++<br/><b>Frontend:</b> React, Next.js, Tailwind CSS, Redux Toolkit, HTML5/CSS3<br/><b>Backend & APIs:</b> FastAPI, Django, Node.js, RESTful APIs, gRPC, Celery<br/><b>AI & LLMs:</b> Large Language Models (LLM), RAG, LangChain, LlamaIndex, OpenAI, Hugging Face, PyTorch, Vector Databases<br/><b>Databases:</b> PostgreSQL, Redis, MongoDB, SQLite<br/><b>Cloud & DevOps:</b> AWS (EC2, S3, RDS), Docker, Kubernetes, CI/CD, GitHub Actions"),
            ("Professional Experience", "<b>Senior Full-Stack AI Engineer | NeuralScale AI (2021 - Present)</b><br/>- Architected and shipped an enterprise GenAI platform using FastAPI, Python, and React TypeScript, reducing latency by 45%.<br/>- Implemented hybrid vector search RAG pipeline utilizing PostgreSQL and OpenAI embeddings.<br/>- Containerized microservices using Docker and orchestrated deployments on AWS ECS and Kubernetes.<br/><br/><b>Full-Stack Developer | Apex Software Labs (2018 - 2021)</b><br/>- Developed responsive web applications in React and FastAPI backed by PostgreSQL.<br/>- Designed REST APIs handling 5,000+ requests per second with Redis caching."),
            ("Education", "<b>Master of Science (M.S.) in Computer Science</b> - Stanford University (2018)<br/><b>Bachelor of Science (B.S.) in Computer Science</b> - UC Berkeley (2016)"),
            ("Notable Projects", "<b>PromptFlow-Agent:</b> Open-source framework for structured LLM evaluation and schema validation (Python, FastAPI, React, PyTorch).<br/><b>Multi-Tenant RAG Engine:</b> Scalable enterprise search engine with hybrid BM25 and vector embeddings (Python, PostgreSQL, Docker, AWS)."),
            ("Certifications", "AWS Certified Solutions Architect - Associate")
        ]
    },
    {
        "filename": "Sarah_Jenkins_Backend_Python.pdf",
        "title": "Sarah Jenkins - Backend Python Developer",
        "sections": [
            ("Sarah Jenkins", "Austin, TX | sarah.jenkins@workmail.io | +1 (512) 555-0144 | github.com/sjenkins-code"),
            ("Professional Summary", "Senior Python Backend Developer with 5 years of experience building resilient microservices, optimizing PostgreSQL databases, and maintaining CI/CD pipelines in AWS."),
            ("Skills", "<b>Languages:</b> Python, SQL, Bash<br/><b>Frameworks:</b> FastAPI, Django, Flask, SQLAlchemy<br/><b>Databases:</b> PostgreSQL, MySQL, Redis<br/><b>DevOps:</b> Docker, AWS (S3, EC2), CI/CD, Git, GitHub Actions<br/><b>Testing:</b> Pytest, TDD, Unit Testing"),
            ("Experience", "<b>Backend Engineer | CloudMatrix Systems (2020 - Present)</b><br/>- Developed high-throughput REST APIs using Python, FastAPI, and PostgreSQL.<br/>- Optimized database indexing and queries, cutting query execution times by 35%.<br/>- Built automated CI/CD workflows using GitHub Actions and Docker containers.<br/><br/><b>Software Developer | DataStream Corp (2019 - 2020)</b><br/>- Built Django web applications with relational database backends.<br/>- Wrote extensive unit tests using pytest."),
            ("Education", "<b>Bachelor of Science (B.S.) in Software Engineering</b> - University of Texas at Austin (2019)"),
            ("Projects", "<b>Async-DB-Broker:</b> Lightweight connection pooler for PostgreSQL in Python.<br/><b>Micro-Cache:</b> Distributed in-memory caching wrapper using Redis.")
        ]
    },
    {
        "filename": "David_Kim_Junior_Frontend.pdf",
        "title": "David Kim - Junior Frontend Developer",
        "sections": [
            ("David Kim", "Seattle, WA | david.kim@webdev.net | +1 (206) 555-0188 | github.com/davidkim-ui"),
            ("Profile", "Junior Frontend Developer with 1.5 years of experience building clean, responsive user interfaces using React, JavaScript, HTML, and CSS. Passionate about UI/UX and web performance."),
            ("Technical Skills", "<b>Frontend:</b> React, JavaScript, HTML5, CSS3, Tailwind CSS<br/><b>Tools:</b> Git, GitHub, VS Code, Figma, Webpack<br/><b>Familiarity:</b> Node.js, Express, REST APIs"),
            ("Experience", "<b>Junior Web Developer | PixelCraft Media (2023 - Present)</b><br/>- Created responsive landing pages and dashboard components using React and Tailwind CSS.<br/>- Collaborated with UI/UX designers to translate Figma prototypes into pixel-perfect components.<br/>- Maintained code repositories using Git and GitHub."),
            ("Education", "<b>Bachelor of Arts (B.A.) in Digital Arts and Media</b> - University of Washington (2023)"),
            ("Projects", "<b>React-Task-Dashboard:</b> Kanban task board with drag-and-drop support (React, Tailwind).<br/><b>Weather-Widget-App:</b> Dynamic weather lookup using OpenWeather API.")
        ]
    },
    {
        "filename": "Emma_Watson_Data_Analyst.pdf",
        "title": "Emma Watson - Data Analyst",
        "sections": [
            ("Emma Watson", "Chicago, IL | emma.watson@analyticsdata.org | +1 (312) 555-0177"),
            ("Summary", "Data Analyst with 3 years of experience generating business intelligence dashboards, SQL queries, and statistical reports in Excel and Tableau."),
            ("Skills", "<b>Data Analysis:</b> SQL, Excel, Tableau, Power BI, Google Sheets<br/><b>Statistics:</b> Data Cleaning, Business Intelligence, Reporting, A/B Testing<br/><b>Basic Python:</b> Pandas, Data visualization"),
            ("Experience", "<b>Data Analyst | Midwest Retail Group (2021 - Present)</b><br/>- Formulated complex SQL queries to extract customer transaction records from MySQL.<br/>- Built interactive Tableau executive dashboards tracking quarterly sales and KPI metrics.<br/>- Cleaned and prepared monthly reporting datasets for marketing stakeholders."),
            ("Education", "<b>Bachelor of Science (B.S.) in Business Analytics</b> - University of Illinois (2021)"),
            ("Projects", "<b>Retail Sales KPI Tracker:</b> Tableau dashboard visualizing seasonal sales trends.")
        ]
    }
]


def generate_sample_pdfs(output_dirs):
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )
    
    section_head_style = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2563eb"),
        spaceBefore=8,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4
    )

    for out_dir in output_dirs:
        os.makedirs(out_dir, exist_ok=True)
        for item in PDF_SAMPLES:
            file_path = os.path.join(out_dir, item["filename"])
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36
            )
            story = []

            for heading, content in item["sections"]:
                if heading == item["sections"][0][0]:
                    story.append(Paragraph(heading, title_style))
                    story.append(Paragraph(content, body_style))
                    story.append(Spacer(1, 4))
                else:
                    story.append(Paragraph(heading.upper(), section_head_style))
                    story.append(Paragraph(content, body_style))
                    story.append(Spacer(1, 4))

            doc.build(story)
            print(f"Generated PDF: {file_path}")


if __name__ == "__main__":
    dirs = ["backend/data/sample_resumes", "sample_data"]
    generate_sample_pdfs(dirs)
