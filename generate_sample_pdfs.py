#!/usr/bin/env python3
"""Generate 10 sample PDFs using PyMuPDF (already in venv). No extra deps needed."""
import sys
sys.path.insert(0, "/home/dell/hackathon/backend/.venv/lib/python3.12/site-packages")

import fitz
from pathlib import Path

OUT = Path("/home/dell/hackathon/uploads")
OUT.mkdir(exist_ok=True)

BOOKS = [
    ("ml_textbook.pdf", "Introduction to Machine Learning",
     ["Supervised Learning","Neural Networks","Deep Learning","Decision Trees",
      "Support Vector Machines","Clustering","Dimensionality Reduction",
      "Model Evaluation","Ensemble Methods","Reinforcement Learning",
      "Natural Language Processing","Computer Vision","Gradient Descent",
      "Backpropagation","Transfer Learning","Regularization","Transformers",
      "Generative Models","Ethics in AI","Future of ML"]),
    ("physics_fundamentals.pdf", "Physics Fundamentals",
     ["Classical Mechanics","Thermodynamics","Electromagnetism","Wave Mechanics",
      "Optics","Quantum Mechanics","Special Relativity","Fluid Dynamics",
      "Nuclear Physics","Particle Physics","Gravitational Theory",
      "Statistical Mechanics","Solid State Physics","Plasma Physics",
      "Astrophysics","Cosmology","String Theory","Quantum Field Theory",
      "Condensed Matter","Superconductivity"]),
    ("world_history.pdf", "World History: Ancient Times to Present",
     ["Prehistoric Civilizations","Ancient Egypt","Mesopotamia","Ancient Greece",
      "The Roman Empire","The Middle Ages","The Renaissance","Age of Exploration",
      "Industrial Revolution","World War I","World War II","Cold War",
      "Decolonization","Modern Era","Globalization","Ancient China",
      "Mughal Empire","Ottoman Empire","Byzantine Empire","The Americas"]),
    ("chemistry.pdf", "Chemistry: Atoms to Molecules",
     ["Atomic Theory","Periodic Table","Chemical Bonding","Stoichiometry",
      "Thermochemistry","Chemical Equilibrium","Acids and Bases",
      "Oxidation and Reduction","Electrochemistry","Organic Chemistry",
      "Biochemistry","Polymer Chemistry","Nuclear Chemistry",
      "Coordination Chemistry","Spectroscopy","Kinetics","Gas Laws",
      "Solutions","Colloids","Catalysis"]),
    ("calculus.pdf", "Calculus and Linear Algebra",
     ["Limits and Continuity","Differentiation","Integration",
      "Differential Equations","Multivariable Calculus","Vector Calculus",
      "Series and Sequences","Linear Transformations","Matrix Operations",
      "Eigenvalues","Vector Spaces","Inner Products","Orthogonality",
      "Numerical Methods","Fourier Analysis","Laplace Transforms",
      "Complex Analysis","Topology","Probability","Statistics"]),
    ("computer_science.pdf", "Computer Science Fundamentals",
     ["Algorithms","Data Structures","Operating Systems","Computer Networks",
      "Databases","Compilers","Computer Architecture","Cryptography",
      "Software Engineering","Distributed Systems","Cloud Computing",
      "Cybersecurity","Parallel Computing","Graph Theory","Automata Theory",
      "Programming Paradigms","Memory Management","File Systems",
      "Web Technologies","DevOps"]),
    ("biology.pdf", "Biology: Cell Theory to Evolution",
     ["Cell Biology","Genetics","Evolution","Ecology","Microbiology",
      "Biochemistry","Physiology","Anatomy","Neuroscience","Immunology",
      "Molecular Biology","Genomics","Developmental Biology","Botany",
      "Zoology","Marine Biology","Biotechnology","Epidemiology",
      "Conservation","Astrobiology"]),
    ("economics.pdf", "Economics and Finance",
     ["Microeconomics","Macroeconomics","Supply and Demand","Market Structures",
      "GDP and Growth","Inflation","Monetary Policy","Fiscal Policy",
      "International Trade","Financial Markets","Investment Theory",
      "Behavioral Economics","Game Theory","Public Finance",
      "Development Economics","Labor Economics","Environmental Economics",
      "Economic History","Cryptocurrencies","Global Financial Crisis"]),
    ("philosophy.pdf", "Philosophy: Ancient to Modern",
     ["Pre-Socratic Philosophy","Plato and Aristotle","Stoicism","Epicureanism",
      "Medieval Philosophy","Rationalism","Empiricism","Kant","Hegel",
      "Existentialism","Phenomenology","Analytic Philosophy","Ethics",
      "Political Philosophy","Epistemology","Metaphysics","Logic",
      "Philosophy of Mind","Philosophy of Science","Postmodernism"]),
    ("psychology.pdf", "Psychology: Cognitive and Behavioral",
     ["History of Psychology","Behavioral Psychology","Cognitive Psychology",
      "Developmental Psychology","Social Psychology","Personality Theory",
      "Abnormal Psychology","Clinical Psychology","Neuropsychology",
      "Sensation and Perception","Memory and Learning","Motivation",
      "Emotions","Language and Thought","Intelligence","Sleep",
      "Stress and Coping","Psychotherapy","Positive Psychology","Research Methods"]),
]

PARA = (
    "This section provides a comprehensive examination of the topic, drawing on "
    "foundational theories and current empirical research. Students are encouraged "
    "to engage critically with the material presented here. The concepts introduced "
    "build upon prerequisite knowledge and serve as a bridge to more advanced topics. "
    "Key definitions, theorems, and illustrative examples are provided throughout. "
    "Practice problems reinforce comprehension and applied understanding. "
    "References to seminal works in the field are included for further study. "
    "The interdisciplinary nature of this subject is highlighted where relevant. "
    "Modern applications and recent developments are discussed to situate classical "
    "ideas within a contemporary framework. Critical thinking and analytical skills "
    "are developed through structured inquiry and problem-solving exercises. "
)

def make_pdf(filename, title, chapters):
    dest = OUT / filename
    if dest.exists():
        print(f"  ✓  {filename} exists, skipping.")
        return

    doc = fitz.open()

    def add_page(text_blocks):
        page = doc.new_page(width=595, height=842)  # A4
        y = 60
        for (txt, size, bold) in text_blocks:
            font = "helv" if not bold else "hebo"
            page.insert_text((50, y), txt, fontname=font, fontsize=size, color=(0.1,0.1,0.3) if bold else (0.1,0.1,0.1))
            y += size * 1.6
            if y > 780:
                break
        # Footer
        page.insert_text((50, 820), f"Page {doc.page_count}", fontname="helv", fontsize=8, color=(0.5,0.5,0.5))

    # Title page
    add_page([
        (title, 22, True),
        ("A Comprehensive Academic Reference", 13, False),
        ("For Educational Purposes — RAG Scholar Demo", 11, False),
    ])

    # TOC
    toc_blocks = [("Table of Contents", 16, True)]
    for i, ch in enumerate(chapters, 1):
        toc_blocks.append((f"  Chapter {i}: {ch}", 10, False))
    add_page(toc_blocks)

    # Chapters — 10 pages each = 200+ pages total
    for i, chapter in enumerate(chapters, 1):
        # Chapter header page
        add_page([(f"Chapter {i}: {chapter}", 18, True), ("Overview and Key Concepts", 12, False)])

        for pg in range(9):  # 9 content pages per chapter
            blocks = [(f"{i}.{pg+1} — {chapter}", 13, True)]
            # Fill the page with content paragraphs
            for _ in range(6):
                blocks.append((PARA[:180], 9, False))
                blocks.append((PARA[180:360], 9, False))
            add_page(blocks)

    doc.save(str(dest))
    size_mb = dest.stat().st_size / 1024 / 1024
    print(f"  ✅ {filename} — {doc.page_count} pages, {size_mb:.1f} MB")
    doc.close()

if __name__ == "__main__":
    print("━" * 52)
    print("  Generating 10 sample academic PDFs (200+ pages)")
    print("━" * 52)
    for fname, title, chapters in BOOKS:
        make_pdf(fname, title, chapters)
    total = len(list(OUT.glob("*.pdf")))
    print(f"\n  Done! {total} PDFs in {OUT}")
    print("  Upload them via http://localhost:8000 or run bulk_ingest.py")
