const { 
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, BorderStyle, ImageRun, Table, TableRow,
  TableCell, WidthType, ShadingType, Spacing, PageOrientation
} = require("docx");
const fs = require("fs");
const path = require("path");

const dataPath = process.argv[2];
const outputPath = process.argv[3];
const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));

const {
  name, email, phone, location, linkedin, github,
  summary, skills, experience, projects, education,
  certifications, photo_path
} = data;

// Colors
const BLUE = "1a56db";
const DARK = "1e293b";
const GRAY = "64748b";
const LIGHT = "f1f5f9";
const WHITE = "ffffff";

// Helper: horizontal rule
function hRule() {
  return new Paragraph({
    border: { bottom: { color: "CBD5E1", size: 6, style: BorderStyle.SINGLE } },
    spacing: { before: 60, after: 60 }
  });
}

// Helper: section heading
function sectionHeading(text) {
  return new Paragraph({
    children: [new TextRun({ text: text.toUpperCase(), bold: true, color: BLUE, size: 22 })],
    spacing: { before: 240, after: 80 },
    border: { bottom: { color: BLUE, size: 8, style: BorderStyle.SINGLE } }
  });
}

// Helper: bullet
function bullet(text) {
  return new Paragraph({
    children: [new TextRun({ text: "• " + text, size: 20, color: DARK })],
    spacing: { before: 40, after: 40 },
    indent: { left: 360 }
  });
}

// Helper: empty line
function spacer(sz = 80) {
  return new Paragraph({ spacing: { before: sz, after: 0 } });
}

// Build children array
const children = [];

// ── HEADER ──────────────────────────────────────
// Photo + Name side by side using table
const headerCells = [];

// Photo cell (if provided)
if (photo_path && fs.existsSync(photo_path)) {
  const photoData = fs.readFileSync(photo_path);
  const ext = path.extname(photo_path).replace(".", "").toLowerCase();
  const typeMap = { jpg: "jpg", jpeg: "jpg", png: "png", gif: "gif" };
  headerCells.push(new TableCell({
    children: [new Paragraph({
      children: [new ImageRun({ data: photoData, type: typeMap[ext] || "png", transformation: { width: 85, height: 105 } })],
      alignment: AlignmentType.CENTER
    })],
    width: { size: 1400, type: WidthType.DXA },
    borders: { top: {style:BorderStyle.NONE}, bottom:{style:BorderStyle.NONE}, left:{style:BorderStyle.NONE}, right:{style:BorderStyle.NONE} }
  }));
}

// Name + contact cell
const nameCell = new TableCell({
  children: [
    new Paragraph({
      children: [new TextRun({ text: name || "Your Name", bold: true, size: 52, color: DARK })],
      spacing: { after: 60 }
    }),
    new Paragraph({
      children: [
        new TextRun({ text: email || "", size: 18, color: GRAY }),
        new TextRun({ text: "  |  ", size: 18, color: GRAY }),
        new TextRun({ text: phone || "", size: 18, color: GRAY }),
        new TextRun({ text: "  |  ", size: 18, color: GRAY }),
        new TextRun({ text: location || "", size: 18, color: GRAY })
      ],
      spacing: { after: 40 }
    }),
    new Paragraph({
      children: [
        linkedin ? new TextRun({ text: "LinkedIn: " + linkedin + "   ", size: 18, color: BLUE }) : new TextRun(""),
        github ? new TextRun({ text: "GitHub: " + github, size: 18, color: BLUE }) : new TextRun("")
      ]
    })
  ],
  width: { size: 7640, type: WidthType.DXA },
  borders: { top:{style:BorderStyle.NONE}, bottom:{style:BorderStyle.NONE}, left:{style:BorderStyle.NONE}, right:{style:BorderStyle.NONE} },
  verticalAlign: "center"
});

if (photo_path && fs.existsSync(photo_path)) headerCells.push(nameCell);
else headerCells.unshift(nameCell);

children.push(new Table({
  rows: [new TableRow({ children: headerCells })],
  width: { size: 9040, type: WidthType.DXA }
}));

children.push(hRule());

// ── SUMMARY ─────────────────────────────────────
if (summary) {
  children.push(sectionHeading("Professional Summary"));
  children.push(new Paragraph({
    children: [new TextRun({ text: summary, size: 20, color: DARK, italics: true })],
    spacing: { after: 80 }
  }));
}

// ── SKILLS ──────────────────────────────────────
if (skills && Object.keys(skills).length > 0) {
  children.push(sectionHeading("Technical Skills"));
  for (const [category, items] of Object.entries(skills)) {
    const itemList = Array.isArray(items) ? items.join(", ") : items;
    children.push(new Paragraph({
      children: [
        new TextRun({ text: category + ": ", bold: true, size: 20, color: DARK }),
        new TextRun({ text: itemList, size: 20, color: GRAY })
      ],
      spacing: { before: 60, after: 40 }
    }));
  }
}

// ── EXPERIENCE ───────────────────────────────────
if (experience && experience.length > 0) {
  children.push(sectionHeading("Professional Experience"));
  for (const exp of experience) {
    children.push(new Paragraph({
      children: [
        new TextRun({ text: exp.title || "", bold: true, size: 22, color: DARK }),
        new TextRun({ text: "  |  ", size: 20, color: GRAY }),
        new TextRun({ text: exp.company || "", bold: true, size: 20, color: BLUE })
      ],
      spacing: { before: 120, after: 30 }
    }));
    children.push(new Paragraph({
      children: [new TextRun({ text: (exp.duration || exp.date || ""), size: 18, color: GRAY, italics: true })],
      spacing: { after: 60 }
    }));
    for (const pt of (exp.points || exp.bullets || [])) {
      children.push(bullet(pt));
    }
    children.push(spacer(60));
  }
}

// ── PROJECTS ─────────────────────────────────────
if (projects && projects.length > 0) {
  children.push(sectionHeading("Projects"));
  for (const proj of projects) {
    children.push(new Paragraph({
      children: [
        new TextRun({ text: proj.name || "", bold: true, size: 22, color: DARK }),
        proj.tech ? new TextRun({ text: "  |  " + proj.tech, size: 18, color: BLUE }) : new TextRun("")
      ],
      spacing: { before: 120, after: 30 }
    }));
    for (const pt of (proj.points || proj.bullets || [])) {
      children.push(bullet(pt));
    }
    if (proj.github || proj.link) {
      children.push(new Paragraph({
        children: [new TextRun({ text: "Link: " + (proj.github || proj.link), size: 18, color: BLUE })],
        indent: { left: 360 }, spacing: { after: 40 }
      }));
    }
    children.push(spacer(60));
  }
}

// ── EDUCATION ────────────────────────────────────
if (education && education.length > 0) {
  children.push(sectionHeading("Education"));
  for (const edu of education) {
    children.push(new Paragraph({
      children: [
        new TextRun({ text: edu.degree || "", bold: true, size: 22, color: DARK }),
        new TextRun({ text: "  |  ", size: 20, color: GRAY }),
        new TextRun({ text: edu.institution || edu.college || "", size: 20, color: BLUE })
      ],
      spacing: { before: 100, after: 30 }
    }));
    children.push(new Paragraph({
      children: [
        new TextRun({ text: edu.year || "", size: 18, color: GRAY, italics: true }),
        edu.cgpa ? new TextRun({ text: "   CGPA: " + edu.cgpa, size: 18, color: GRAY }) : new TextRun("")
      ],
      spacing: { after: 60 }
    }));
  }
}

// ── CERTIFICATIONS ───────────────────────────────
if (certifications && certifications.length > 0) {
  children.push(sectionHeading("Certifications"));
  for (const cert of certifications) {
    children.push(bullet(typeof cert === "string" ? cert : (cert.name + (cert.issuer ? " — " + cert.issuer : ""))));
  }
}

// ── BUILD DOC ────────────────────────────────────
const doc = new Document({
  sections: [{
    properties: {
      page: {
        margin: { top: 720, bottom: 720, left: 900, right: 900 }
      }
    },
    children: children
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outputPath, buf);
  console.log("SUCCESS:" + outputPath);
});
