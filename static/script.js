function createBlock(html, type) {
    const div = document.createElement("div");
    div.className = "block";
    div.setAttribute("data-type", type);
    div.innerHTML = html;
    document.getElementById("editor").appendChild(div);
}

function addTitle() { createBlock('<input placeholder="Enter centered title" class="title">', "title"); }
function addSubtitle() { createBlock('<input placeholder="Enter centered subtitle (smaller text)">', "subtitle"); }
function addLinks() { createBlock('<input placeholder="Email/link/phone (use | to separate multiple)">', "links"); }
function addSection() { createBlock('<input placeholder="Section title">', "section"); }
function addHR() { createBlock('<em>--- horizontal rule ---</em>', "hr"); }
function addSubheading() {
    createBlock(`<input placeholder="Left Text"><input placeholder="Right Text">`, "subheading");
}
function addSubheadingRight() {
    createBlock(`<input placeholder="Right Text"><input placeholder="Left Text">`, "subheading-right");
}
function addBullets(col) {
    createBlock('<textarea placeholder="Enter bullets, one per line"></textarea>', col === "one" ? "bullets1" : "bullets2");
}
function addParagraph() {
    createBlock('<textarea rows="4" placeholder="Enter paragraph text..."></textarea>', "paragraph");
}

// Form submission to compile LaTeX
document.querySelector("form").onsubmit = function () {
    const blocks = document.querySelectorAll(".block");
    let tex = "";

    blocks.forEach(block => {
        const type = block.getAttribute("data-type");
        const inputs = block.querySelectorAll("input, textarea");

        switch (type) {
            case "title":
                tex += `\\begin{center}\\LARGE \\textbf{${inputs[0].value}}\\end{center}\n\n`; break;
            case "subtitle":
                tex += `\\begin{center}\\normalsize ${inputs[0].value}\\end{center}\n\n`; break;
            case "links":
                const links = inputs[0].value.split("|").map(s => s.trim());
                tex += "\\begin{center}" + links.join(" $|$ ") + "\\end{center}\n\n"; break;
            case "section":
                tex += `\\section*{${inputs[0].value}}\n\n`; break;
            case "hr":
                tex += "\\hrule\n\n"; break;
            case "subheading":
                tex += `\\textbf{${inputs[0].value}} \\hfill ${inputs[1].value}\n\n`; break;
            case "subheading-right":
                tex += `${inputs[1].value} \\hfill \\textit{${inputs[0].value}} \n\n`; break;
            case "bullets1":
                tex += "\\begin{itemize}[leftmargin=*]\n" + inputs[0].value.trim().split("\n").map(i => `\\item ${i}`).join("\n") + "\n\\end{itemize}\n\n"; break;
            case "bullets2":
                tex += "\\begin{multicols}{2}\n\\begin{itemize}[leftmargin=*]\n" + inputs[0].value.trim().split("\n").map(i => `\\item ${i}`).join("\n") + "\n\\end{itemize}\n\\end{multicols}\n\n"; break;
            case "paragraph":
                tex += inputs[0].value + "\n\n"; break;
        }
    });

    document.getElementById("latex_content").value = tex;
};

// Drag and Drop Feature
fetch("/static/data.json")
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById("data-container");
    container.innerHTML = "";

    function makeDraggable(text) {
      if (!text || typeof text !== "string") return;
      const div = document.createElement("div");
      div.className = "draggable";
      div.textContent = text;
      div.draggable = true;
      div.ondragstart = e => {
        e.dataTransfer.setData("text/plain", text);
      };
      container.appendChild(div);
    }

    function extractValues(obj) {
      if (typeof obj === "string" || typeof obj === "number") {
        makeDraggable(String(obj));
      } else if (Array.isArray(obj)) {
        obj.forEach(extractValues);
      } else if (typeof obj === "object" && obj !== null) {
        Object.values(obj).forEach(extractValues);
      }
    }

    extractValues(data);
  });

// Fetch skills from skills_output.json
fetch("/static/skills_output.json")
  .then(res => res.json())
  .then(data => {
    const skillsContainer = document.getElementById("skills-container");
    skillsContainer.innerHTML = "";

    function makeSkillDraggable(text) {
      if (!text || typeof text !== "string") return;
      const div = document.createElement("div");
      div.className = "draggable";
      div.textContent = text;
      div.draggable = true;
      div.ondragstart = e => {
        e.dataTransfer.setData("text/plain", text);
      };
      skillsContainer.appendChild(div);
    }

    // Flatten and extract skills
    function extractSkills(obj) {
      if (Array.isArray(obj)) {
        obj.forEach(extractSkills);
      } else if (typeof obj === "object" && obj !== null) {
        Object.values(obj).forEach(extractSkills);
      } else if (typeof obj === "string") {
        makeSkillDraggable(obj);
      }
    }

    extractSkills(data);
  });

// Allow inputs and textareas to accept drops
document.addEventListener("dragover", e => {
    if (e.target.matches("input, textarea")) {
        e.preventDefault();
    }
});
document.addEventListener("drop", e => {
    if (e.target.matches("input, textarea")) {
        e.preventDefault();
        const text = e.dataTransfer.getData("text/plain");
        if (e.target.value) e.target.value += " " + text;
        else e.target.value = text;
    }
});
