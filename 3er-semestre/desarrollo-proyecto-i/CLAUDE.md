# CLAUDE.md: Desarrollo de Proyecto I

Subject context. The repo-wide rules are in the root `CLAUDE.md`; this file adds what was decided for
this subject.

## Subject
- NRC 176459, Wednesday (online). Professor: Dra. Ana Rosa Jiménez Meza ("arjm"), who is also the
  advisor reviewing the thesis protocol.
- Main deliverable: the research protocol (thesis), plus class activities.

## Thesis focus (decided 2026-10, after the advisor meeting)
- Topic: labor **mobility** ("movilidad laboral", NOT substitution or displacement as the headline)
  caused by cognitive AI / LLMs, for **careers and occupations around informatics and data science**
  (not only "ingeniería informática"). The earlier manufacturing-in-Jalisco framing was dropped; a
  Jalisco manufacturing mention in the meeting notes was left out pending Carlos's confirmation.
- Scope: Mexico, with Jalisco as a state case only if the ENOE sample allows (occupation 2271 has
  about 38 to 62 sample people per quarter in Jalisco, so national scope is the base). This
  feasibility check is internal; it does not go in the protocol.
- Also assess risk across careers, useful for students choosing a career (advisor's request).

## Protocol rules (`tareas/Protocolo/`)
- Nothing is taken for granted (Carlos, 2026-11-18): every datum, index, source, acronym or method the
  reader may not know says where it comes from (who produced it, with what data) and what it is used
  for in the protocol. Do not write claims that no cited source supports.
- The protocol states the problem and the plan only. **No results of our own**, no thesis numbers as
  evidence. Every datum is explained and cited in APA 7, with formal definitions.
- Built on Carlos's cleaned layout `layout_protocolo_cucea_2026.docx`: `build_protocolo.py` sets the
  cover title (`P[10]`) and date (`P[19]`), removes the old body and inserts the text from
  `contenido_protocolo.py`. Output goes to the repo and to
  `Downloads\Protocolo de investigación MCD con Inteligencia Artificial 2026.docx`.
- Advisor feedback already applied: no "Protocolo de investigación" heading, no identification
  section, no three-questions paragraph; page 2 starts with I. Planteamiento; Khan & Varshney (2026)
  "Dynamic uncertainty..." included.
- Format: `_recursos/Lineamientos presentación de trabajos MCD Ver 2.0.docx` (Times New Roman 12,
  double spacing, Roman-numeral centered headings, margins 3/2.5 cm, APA references 1.5 spacing).
- Sections: Planteamiento (Contexto, Definición, Preguntas), Justificación, Objetivos, Hipótesis
  (H1: young people face higher mobility risk after 2022; H2: exits go to skill-near occupations,
  not unemployment), Antecedentes, Marco teórico, Metodología (ENOE rotating panel, transition
  matrices, multinomial logit, difference in differences, ML with uncertainty, mobility network),
  Recursos, Cronograma, Referencias.
- Key classifications: CMPE 2016 field 06 TIC (061: 0611/0612/0613; 062: 0621/0622/0623; data
  science sits in 0613) plus 0532 Estadística y actuaría; SINCO 2019 occupations 2271, 2272, 2212,
  2651, 1321, 1621; ENOE variable `CS_P14_C` (career code); ENOE panel = 5 panels, 5 quarters, 80 %
  of the sample kept each quarter.
- References are verified (OpenAlex, Semantic Scholar, PDFs in `tareas/Protocolo/fuentes/`). Do not
  add a reference without checking its abstract or PDF. Choi & Leigh was dropped (no abstract).

## Data
- Thesis data only from the thesis repo (`ai-automation-risk-jalisco`) or cited public sources. Never
  invent data or summarize tools (Gemini, NotebookLM, Consensus) Carlos has to run himself.

## Advisor requests checked against the protocol (2026-11-18)
- Done: body starts at Planteamiento; every source cited APA 7; formal definitions now include
  inteligencia artificial (OCDE, 2024) and automatización (Acemoglu y Restrepo, 2019); scope limited to
  cognitive AI / LLMs with Webb (2020) as the reason robotics is excluded; English terms added
  (large language models, labor mobility, displacement, AI exposure); movilidad, not sustitución;
  careers compared; Khan & Varshney (2026) used.
- Not applied on purpose: the Jalisco manufacturing / formal employment centers info and the
  nearshoring definition, because the same meeting dropped manufacturing and robotics. Confirm with
  Carlos if the Dra. still wants a Jalisco paragraph.

## Open items
- Title (chosen 2026-11-18, option 1 of 9): "Riesgo de movilidad laboral por inteligencia artificial en
  carreras de informática y ciencia de datos" (15 words). Cover date 18 de noviembre de 2026.
- Send the protocol to the Dra.; meetings with Dr. Willy Walter Cortez and Dra. Ancona.
- The `.gitkeep` files in `datos/`, `notas/`, `notebooks/`, `proyectos/` were deleted locally and not
  committed; Carlos has not said whether to restore them.

## Other activities
- `tareas/Actividad_Referencias/`: 16-reference analysis (`build_referencias.py`, DOCX/PDF/XLSX),
  from the earlier manufacturing framing.
