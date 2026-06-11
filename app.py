import streamlit as st
from google import genai
import sys

# Fetch API key from Streamlit Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not API_KEY:
    st.error("🔑 **API Key Missing!**")
    st.info("To fix this locally: Paste your key into `.streamlit/secrets.toml` like this:\n`GEMINI_API_KEY = 'your-key-here'`")
    st.stop()

MARKDOWN_ARTIFACTS = ["```latex", "```", "```python", "```text"]

PROMPT_TEMPLATE = """You are an elite LaTeX resume optimizer specializing in Java Backend and BFSI engineering. 
Your sole task is to align the candidate's resume to the provided Job Description (JD) while maintaining strict technical truthfulness.

CRITICAL OUTPUT RULE: 
Return ONLY the raw, valid LaTeX code. 
Do NOT wrap your response in markdown code blocks (e.g., do NOT use ```latex or ```). 
Do NOT include any introduction, explanation, or markdown formatting outside of LaTeX commands.

==== CORE WORKFLOW ====
1. Extract relevant technical keywords and target metrics from the JD.
2. Identify true conceptual overlaps with the candidate's authentic background.
3. Tailor the Professional Summary and Technical Skills sections to highlight JD-demanded skills.
4. Rewrite and weave JD keywords naturally into the experience bullets *without changing the core engineering impact*.
5. Keep ALL LaTeX structure, custom macros, document styling, and layout definitions completely intact.

==== CANDIDATE SKILL MATRIX (TRUTH ANCHORS) ====
* HIGH EXPERTISE: Java (8/11/17), Spring Boot, Spring MVC, Spring Security, Hibernate, JPA, Microservices Architecture, RESTful API Development, Multithreading, Performance Tuning.
* ENTERPRISE BFSI DOMAIN: FinnOne Lending Core Modules, Loan Processing Workflows, Credit/Regulatory Reporting (CRS), Maker-Checker Systems, Multi-level Configurable Approvals.
* DATA & ARCHITECTURE: Oracle SQL & PL/SQL, Query Optimization (Execution Plans, Composite Indexes, Hibernate Batch Fetching Size, N+1 Query Resolution), Apache Kafka (Asynchronous Workflows, DLQ), Redis Caching.
* DEVOPS, PLATFORMS & MIGRATION: Application Migration (Oracle WebLogic to Red Hat JBoss/WildFly), Apache Tomcat, CI/CD Jenkins Pipelines, SonarQube Code Quality, Git, Maven.
* STRICTLY FORBIDDEN: Do NOT include Cloud Platforms (AWS, Azure, GCP), "AI/ML", or "Data Science" unless the candidate has explicitly built a simulator/project for it. Do NOT claim "Advanced Distributed Systems Architecture" beyond the Kafka/Redis project scope.
* TONE RULE: Eliminate fluff. Strictly ban subjective filler terms like "Passionate", "Results-driven", "Motivated", or "Talented". Let the metrics do the talking.

==== OPTIMIZATION INSTRUCTIONS ====

1. Enhance Summary:
   - Anchor with the mandatory title: "Java Backend Developer with 3.5+ years of experience..." (Keep this duration exact).
   - Dynamically highlight core matching keywords (e.g., Microservices, PL/SQL, Kafka, or Low-latency) based on what the JD prioritizes.

2. Enhance Skills Section:
   - Prioritize and re-order the layout of categories (Programming & Backend, Messaging & Caching, Database, Tools, Servers) so that the skills explicitly requested in the JD appear first in each bullet list.
   - Do not invent entirely new skills outside the Candidate Skill Matrix.

3. Enhance Experience (Nucleus Software):
   - Weave JD technical keywords into existing bullet points naturally.
   - PROTECT THE METRICS. Ensure these key highlights remain preserved or appropriately emphasized:
     * Reducing loan processing time by 40% using Java/Spring Boot/Oracle PL/SQL.
     * Application migration from WebLogic to JBoss saving 25% in licensing costs.
     * Optimization of application performance by 30% via execution plan refactoring and resolving N+1 queries.
     * Leading end-to-end delivery of FinnOne modules for 3+ global banking clients.
     * Zero critical post-release defects across 4+ production releases.
     * Improving SonarQube code quality scores by 15% through mentorship.
   - CRITICAL: Modify ONLY plain text keywords to prevent breaking the layout. Do NOT add, remove, or alter LaTeX environment definitions, section structural setups, or `\item` markers.

4. Preserve Integrity:
   - Ensure all `\newcommand` definitions, special character escapes (like `\%`, `&`), and format wrappers are output completely unchanged.

JOB DESCRIPTION:
{jd}

RESUME LATEX:
{resume}

OUTPUT ONLY THE MODIFIED RAW LATEX:"""

def clean_markdown(text: str) -> str:
    for artifact in MARKDOWN_ARTIFACTS:
        text = text.replace(artifact, "")
    text = text.replace("**", "")
    return text.strip()

def optimize_resume(jd: str, resume: str, model_id: str) -> str:
    client = genai.Client(api_key=API_KEY)
    prompt = PROMPT_TEMPLATE.format(jd=jd, resume=resume)
    response = client.models.generate_content(model=model_id, contents=prompt)
    return clean_markdown(response.text)

# --- STREAMLIT UI ---
st.set_page_config(page_title="LaTeX Resume Optimizer", page_icon="📄")
st.title("📄 LaTeX Resume Optimizer")

st.markdown("ATS resume optimizer with JD matching using Google AI Studio selected models.")

MODEL_OPTIONS = {
    "gemini-3-flash-preview": "1. Gemini 3 Flash (20 RPD | The Best, won't break LaTeX)",
    "gemini-2.5-flash": "2. Gemini 2.5 Flash (20 RPD | Highly Capable alternative)",
    "gemini-3.1-flash-lite-preview": "3. Gemini 3.1 Flash Lite (500 RPD | Best for bulk testing)",
    "gemma-3-27b": "4. Gemma 3 27B (14,400 RPD | Massive Backup)"
}

selected_model = st.selectbox(
    "Choose your AI Model:",
    options=list(MODEL_OPTIONS.keys()),
    format_func=lambda x: MODEL_OPTIONS[x],
    index=0
)

jd_input = st.text_area("Paste Job Description (JD) here:", height=300)

if st.button("Generate Optimized Resume", type="primary"):
    if not jd_input:
        st.warning("⚠️ Please provide a Job Description.")
    else:
        with st.spinner("Optimizing your resume with Gemini..."):
            try:
                with open("resume.tex", "r", encoding="utf-8") as f:
                    resume_content = f.read()
            except FileNotFoundError:
                st.error("❌ 'resume.tex' was not found in the repository! Make sure it is pushed to GitHub.")
                st.stop()
            try:
                optimized_tex = optimize_resume(jd_input, resume_content, selected_model)
                st.success(f"✅ Optimization complete using {selected_model}!")
                
                with st.spinner("Compiling LaTeX to PDF..."):
                    import tempfile
                    import subprocess
                    import os
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        tex_path = os.path.join(temp_dir, "optimized.tex")
                        pdf_path = os.path.join(temp_dir, "optimized.pdf")
                        
                        with open(tex_path, "w", encoding="utf-8") as f:
                            f.write(optimized_tex)
                        
                        compile_process = subprocess.run(
                            ["pdflatex", "-interaction=nonstopmode", "optimized.tex"],
                            cwd=temp_dir,
                            capture_output=True,
                            text=True
                        )
                        
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as f:
                                pdf_data = f.read()
                                
                            st.success("🎉 PDF Compiled Successfully!")
                            st.download_button(
                                label="⬇️ Download Optimized PDF",
                                data=pdf_data,
                                file_name="optimized.pdf",
                                mime="application/pdf"
                            )                            
                        else:
                            st.error("❌ Failed to compile LaTeX to PDF. The model likely generated invalid LaTeX structure.")
                            with st.expander("View LaTeX Errors"):
                                st.text(compile_process.stdout)
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    st.error("🛑 Rate Limit Exceeded for this Model!")
                    st.warning("💡 **Tip:** You have hit the daily free quota for this specific AI model. Please scroll up and select a different model (e.g. Gemini 3.1 Flash Lite or Gemma) from the dropdown menu to continue!")
                else:
                    st.error(f"An error occurred: {error_msg}")


