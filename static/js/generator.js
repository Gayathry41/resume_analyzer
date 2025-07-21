function insertSection() {
  insertLatex("\\section{Section Title}\n");
}

function insertItem() {
  insertLatex("\\item Your item here\n");
}

function insertEducation() {
  insertLatex("\\section{Education}\n\\begin{itemize}\n\\item B.Tech in XYZ, ABC University\n\\end{itemize}\n");
}

function insertExperience() {
  insertLatex("\\section{Experience}\n\\begin{itemize}\n\\item Software Developer at XYZ Corp\n\\end{itemize}\n");
}

function insertSkill() {
  insertLatex("\\section{Skills}\n\\begin{itemize}\n\\item Python, C++, LaTeX\n\\end{itemize}\n");
}

function insertLatex(text) {
  const editor = document.getElementById("editor");
  const sel = window.getSelection();
  const range = sel.getRangeAt(0);
  range.deleteContents();
  const node = document.createTextNode(text);
  range.insertNode(node);
  sel.collapseToEnd();
}

function generateLatex() {
  const content = document.getElementById("editor").innerText;
  document.getElementById("latex_code").value = content;
  document.getElementById("latexForm").submit();
}
