def generate_latex(resume_data):
    latex = []

    latex.append(r"\documentclass{article}")
    latex.append(r"\usepackage[a4paper,margin=1in]{geometry}")
    latex.append(r"\usepackage{hyperref}")
    latex.append(r"\begin{document}")

    # Header
    latex.append(f"\\begin{{center}}\\textbf{{\\Huge {resume_data['name']}}}\\\\")
    latex.append(f"{resume_data['title']}\\\\\\end{{center}}")

    # Contact
    contact = resume_data["contact"]
    latex.append("\\noindent")
    latex.append(f"Email: {contact['email']} \\quad Phone: {contact['phone']} \\quad LinkedIn: \\url{{{contact['linkedin']}}}\\\\[0.5cm]")

    # Summary
    latex.append(r"\section*{Summary}")
    latex.append(resume_data["summary"])

    # Skills
    latex.append(r"\section*{Skills}")
    latex.append(", ".join(resume_data["skills"]))

    # Education
    latex.append(r"\section*{Education}")
    for edu in resume_data["education"]:
        latex.append(f"\\textbf{{{edu['degree']}}}, {edu['institution']} ({edu['year']})\\\\[0.2cm]")

    # Experience
    latex.append(r"\section*{Experience}")
    for exp in resume_data["experience"]:
        latex.append(f"\\textbf{{{exp['role']}}} -- {exp['company']} ({exp['duration']})\\\\")
        latex.append(r"\begin{itemize}")
        for item in exp["responsibilities"]:
            latex.append(f"\\item {item}")
        latex.append(r"\end{itemize}")

    # Projects
    latex.append(r"\section*{Projects}")
    for proj in resume_data["projects"]:
        latex.append(f"\\textbf{{{proj['title']}}}: {proj['description']}\\\\[0.2cm]")

    latex.append(r"\end{document}")

    return "\n".join(latex)
