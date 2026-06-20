#!/usr/bin/env python3
"""
Download OR generate 10 large PDFs (200+ pages each) for demo.
First tries working Gutenberg/Archive URLs; falls back to generating
synthetic academic PDFs with fpdf2 (auto-installed if missing).
"""
import urllib.request
import subprocess
import sys
import os
from pathlib import Path

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Working PDF URLs (verified format from Project Gutenberg cache)
PDFS = [
    # These IDs go through Gutenberg's epub-to-PDF pipeline
    ("alice_in_wonderland.pdf",    "https://www.gutenberg.org/cache/epub/11/pg11.pdf"),
    ("adventures_tom_sawyer.pdf",  "https://www.gutenberg.org/cache/epub/74/pg74.pdf"),
    ("adventures_huck_finn.pdf",   "https://www.gutenberg.org/cache/epub/76/pg76.pdf"),
    ("sherlock_holmes.pdf",        "https://www.gutenberg.org/cache/epub/1661/pg1661.pdf"),
    ("dracula.pdf",                "https://www.gutenberg.org/cache/epub/345/pg345.pdf"),
    ("frankenstein.pdf",           "https://www.gutenberg.org/cache/epub/84/pg84.pdf"),
    ("pride_prejudice.pdf",        "https://www.gutenberg.org/cache/epub/1342/pg1342.pdf"),
    ("great_expectations.pdf",     "https://www.gutenberg.org/cache/epub/1400/pg1400.pdf"),
    ("moby_dick.pdf",              "https://www.gutenberg.org/cache/epub/2701/pg2701.pdf"),
    ("war_and_peace.pdf",          "https://www.gutenberg.org/cache/epub/2600/pg2600.pdf"),
]

# ── Synthetic PDF generator (fallback) ───────────────────────
SUBJECTS = [
    ("machine_learning_textbook.pdf", "Introduction to Machine Learning",
     ["Supervised Learning", "Unsupervised Learning", "Neural Networks",
      "Deep Learning", "Reinforcement Learning", "Model Evaluation",
      "Feature Engineering", "Decision Trees", "Support Vector Machines",
      "Natural Language Processing", "Computer Vision", "Gradient Descent",
      "Backpropagation", "Convolutional Networks", "Recurrent Networks",
      "Attention Mechanisms", "Transfer Learning", "Regularization",
      "Hyperparameter Tuning", "Ensemble Methods"]),
    ("physics_fundamentals.pdf", "Physics Fundamentals",
     ["Classical Mechanics", "Thermodynamics", "Electromagnetism",
      "Wave Mechanics", "Optics", "Quantum Mechanics", "Special Relativity",
      "Fluid Dynamics", "Nuclear Physics", "Particle Physics",
      "Gravitational Theory", "Statistical Mechanics", "Solid State Physics",
      "Plasma Physics", "Astrophysics", "Cosmology", "String Theory",
      "Quantum Field Theory", "Condensed Matter", "Superconductivity"]),
    ("world_history.pdf", "World History: From Ancient Times to Present",
     ["Prehistoric Civilizations", "Ancient Egypt", "Mesopotamia",
      "Ancient Greece", "The Roman Empire", "The Middle Ages",
      "The Renaissance", "Age of Exploration", "The Industrial Revolution",
      "World War I", "World War II", "Cold War", "Decolonization",
      "The Modern Era", "Globalization", "Ancient China", "Mughal Empire",
      "Ottoman Empire", "Byzantine Empire", "The Americas"]),
    ("chemistry_basics.pdf", "Chemistry: From Atoms to Molecules",
     ["Atomic Theory", "Periodic Table", "Chemical Bonding",
      "Stoichiometry", "Thermochemistry", "Chemical Equilibrium",
      "Acids and Bases", "Oxidation and Reduction", "Electrochemistry",
      "Organic Chemistry", "Biochemistry", "Polymer Chemistry",
      "Nuclear Chemistry", "Coordination Chemistry", "Spectroscopy",
      "Kinetics", "Gas Laws", "Solutions", "Colloids", "Catalysis"]),
    ("calculus_linear_algebra.pdf", "Mathematics: Calculus and Linear Algebra",
     ["Limits and Continuity", "Differentiation", "Integration",
      "Differential Equations", "Multivariable Calculus", "Vector Calculus",
      "Series and Sequences", "Linear Transformations", "Matrix Operations",
      "Eigenvalues and Eigenvectors", "Vector Spaces", "Inner Products",
      "Orthogonality", "Numerical Methods", "Fourier Analysis",
      "Laplace Transforms", "Complex Analysis", "Topology", "Probability",
      "Statistics"]),
]


VENV_PIP = str(Path(__file__).parent / "backend" / ".venv" / "bin" / "pip")

def ensure_fpdf2():
    try:
        import fpdf  # noqa
        return
    except ImportError:
        pass
    print("  Installing fpdf2 into venv…")
    pip = VENV_PIP if Path(VENV_PIP).exists() else sys.executable.replace("python3", "pip3")
    subprocess.check_call([pip, "install", "-q", "fpdf2"])
    # Now importable via venv python
    import importlib, fpdf  # noqa


def generate_pdf(filename: str, title: str, chapters: list, pages_per_chapter: int = 11):
    """Generate a synthetic academic PDF with ~220 pages."""
    from fpdf import FPDF

    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, title, align="C", new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(20, 20, 20)

    # Title page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(30, 30, 80)
    pdf.ln(60)
    pdf.multi_cell(0, 14, title, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 10, "A Comprehensive Academic Reference\nFor Educational Purposes", align="C")
    pdf.ln(20)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 10, "Generated for RAG Scholar Demo", align="C")

    # Table of Contents
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for i, ch in enumerate(chapters, 1):
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 8, f"Chapter {i}: {ch}", new_x="LMARGIN", new_y="NEXT")

    # Chapters
    para = (
        "This chapter provides a thorough examination of the subject matter, "
        "drawing on foundational theories and empirical research. Students are "
        "encouraged to engage critically with the material presented here. "
        "The concepts introduced build upon prerequisite knowledge and serve "
        "as a bridge to more advanced topics in later chapters. Key definitions, "
        "theorems, and illustrative examples are provided throughout. "
        "Practice problems at the end of each section reinforce comprehension. "
        "References to seminal works in the field are included for further study. "
        "The interdisciplinary nature of this topic is highlighted where relevant. "
        "Modern applications and recent developments are discussed to situate "
        "classical ideas within a contemporary framework. "
    )

    for i, chapter in enumerate(chapters, 1):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(20, 20, 100)
        pdf.cell(0, 14, f"Chapter {i}: {chapter}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        for sec in range(1, 5):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(40, 40, 120)
            pdf.cell(0, 10, f"{i}.{sec} {'Overview' if sec==1 else 'Key Concepts' if sec==2 else 'Applications' if sec==3 else 'Summary'}",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(30, 30, 30)
            # Repeat paragraph enough times to fill pages
            for _ in range(pages_per_chapter):
                pdf.multi_cell(0, 7, para + f" [Section {i}.{sec} — {chapter}]")
                pdf.ln(3)

    dest = UPLOAD_DIR / filename
    pdf.output(str(dest))
    size_mb = dest.stat().st_size / 1024 / 1024
    pages = pdf.page  # approximate
    print(f"  ✅ Generated {filename} ({size_mb:.1f} MB, ~{pages} pages)")


def download_pdf(name: str, url: str) -> bool:
    dest = UPLOAD_DIR / name
    if dest.exists() and dest.stat().st_size > 50_000:
        print(f"  ✓  {name} already exists, skipping.")
        return True
    print(f"  ⬇  Downloading {name}…", end="", flush=True)
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; RAGScholar/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        if len(data) < 10_000 or not data.startswith(b"%PDF"):
            print(f" ❌ not a valid PDF ({len(data)} bytes)")
            return False
        dest.write_bytes(data)
        print(f" ✅ ({len(data)/1024/1024:.1f} MB)")
        return True
    except Exception as e:
        print(f" ❌ {e}")
        return False


if __name__ == "__main__":
    print("━" * 55)
    print("  RAG Scholar — PDF Corpus Setup")
    print("━" * 55)
    print()

    # Step 1: try downloading from Gutenberg
    downloaded = 0
    failed_names = []
    for name, url in PDFS:
        ok = download_pdf(name, url)
        if ok:
            downloaded += 1
        else:
            failed_names.append(name)

    # Step 2: generate synthetic PDFs for failures OR if we need more
    need_synthetic = max(0, 10 - downloaded)
    if need_synthetic > 0:
        print(f"\n  Generating {need_synthetic} synthetic academic PDFs…")
        ensure_fpdf2()
        for fname, title, chapters in SUBJECTS[:need_synthetic]:
            dest = UPLOAD_DIR / fname
            if dest.exists() and dest.stat().st_size > 50_000:
                print(f"  ✓  {fname} already exists, skipping.")
                continue
            print(f"  ✏  Generating {fname}…", end="", flush=True)
            print()
            generate_pdf(fname, title, chapters)

    total = sum(1 for p in UPLOAD_DIR.glob("*.pdf") if p.stat().st_size > 50_000)
    print(f"\n  📚 Total PDFs ready: {total}")
    print(f"  📂 Location: {UPLOAD_DIR}")
    print()
    print("  Next: ingest them via the web UI at http://localhost:8000")
    print("  Or run: python3 bulk_ingest.py")
