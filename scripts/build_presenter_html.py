#!/usr/bin/env python3
"""
Generates:
1. /Users/ykro/code/charlas/2027/gemma/presenter/index.html
   Interactive HTML Presenter View & Side-by-Side Study Guide showing each slide image
   next to its full speaker script ("Qué decir", "Qué señalar en pantalla", "Transición").
2. /Users/ykro/code/charlas/2027/gemma/charla-gemma-2027.md
   Synchronized Markdown speaker guide.
"""

import json
from pathlib import Path
from speaker_notes_data import SPEAKER_NOTES

ROOT = Path(__file__).resolve().parent.parent
PRESENTER_DIR = ROOT / "presenter"
OUT_HTML = PRESENTER_DIR / "index.html"
OUT_MD = ROOT / "charla-gemma-2027.md"


def build_markdown():
    lines = [
        "# Guía de Orador — Engineering with Gemma: Casos de uso y arquitecturas",
        "",
        "- **Orador:** Adrián Catalán (`@adriancs.tech`)",
        "- **Título oficial:** *Engineering with Gemma: Casos de uso y arquitecturas*",
        "- **Abstract oficial:**",
        "  > Exploraremos cómo diseñar soluciones con Gemma combinando ejecución local en edge y orquestación en servicios. Revisaremos código, retos de implementación y lecciones aprendidas construyendo herramientas productivas sobre Android y backend.",
        "- **Duración estimada:** ~50 minutos + Q&A",
        "- **Archivos sincronizados:**",
        "  - Presentación PowerPoint (con notas integradas): `Gemma_Charla_2027.pptx`",
        "  - Consola HTML interactiva de presentador: `presenter/index.html`",
        "  - Codelab interactivo: `codelab/index.html`",
        "- **Repositorios de referencia:**",
        "  - Android / On-Device (`Generador de Excusas` con LiteRT-LM): `https://github.com/ykro/generador-excusas`",
        "  - Backend / Cloud Run (`Cover Letter` con Gemma 4 E2B en Ollama): `https://github.com/ykro/coverletter-gemma`",
        "",
        "---",
        "",
        "## Mapa General de la Charla (32 Slides)",
        "",
        "| Bloque | Slides | Enfoque | Tiempo |",
        "| :--- | :---: | :--- | :---: |",
        "| **Apertura y Ecosistema Gemma 4** | 1 – 6 | Problema del modelo único externo, rol de Gemini vs Gemma 4, mapa de familia `E2B`/`E4B`/`26B-A4B`/`31B` y variantes especializadas | 9.5 min |",
        "| **Arquitectura Interna de Gemma 4** | 7 – 12 | Tokenizador 256k multimodal, Atención Híbrida 5 a 1 + KV Cache + PLE + QAT INT4, `-pt` vs `-it`, prompts deterministas y LiteRT-LM en Android | 10.5 min |",
        "| **Adaptación con Prompting, RAG y QLoRA** | 13 – 17 | Criterios de decisión, RAG con `EmbeddingGemma 2` y vectores Matryoshka (`MRL`), matemática LoRA/QLoRA (`W₀ + B·A`) y entrenamiento con RAFT | 8.0 min |",
        "| **Casos Split-Brain en Android y Cloud Run** | 18 – 27 | Frontera de privacidad determinista, Caso 1 en Android (*Excusa Legendaria* con LiteRT-LM y `LeakDetector.kt`) y Caso 2 en Cloud Run (*Cover Letter* con Ollama en GPU L4, router por niveles en TypeScript y benchmark real vs Qwen 3.5 2B) | 17.5 min |",
        "| **Agentes con ADK para Kotlin y Lecciones** | 28 – 32 | Ciclo de eventos ADK en Android, intercambio de `BaseLlm`, confirmación humana (`requireConfirmation`), apps de referencia y lecciones aprendidas | 6.0 min |",
        "",
        "---",
        "",
        "## Notas del Presentador Slide por Slide",
        "",
    ]

    current_block = None
    for note in SPEAKER_NOTES:
        if note["block"] != current_block:
            current_block = note["block"]
            lines.append(f"### {current_block}")
            lines.append("")

        s_num = note["slide"]
        img_rel = f"presenter/slides/slide-{s_num:02d}.png"
        lines.append(f"#### Slide {s_num:02d} — {note['title']}")
        lines.append(f"- **Tiempo:** `{note['duration']}` *(Acumulado: `{note['cumulative']}`)*")
        lines.append(f"- **Imagen del slide:** `{img_rel}`")
        lines.append(f"- **Objetivo:** {note['objective']}")
        lines.append("- **Qué decir:**")
        for p in note["say"]:
            lines.append(f"  > {p}")
            lines.append("  >")
        if lines[-1] == "  >":
            lines.pop()
        lines.append("- **Qué señalar en pantalla:**")
        for pt in note["point_out"]:
            lines.append(f"  - {pt}")
        lines.append(f"- **Transición al siguiente slide:** *{note['transition']}*")
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Updated {OUT_MD}")


def build_html():
    PRESENTER_DIR.mkdir(parents=True, exist_ok=True)
    notes_json = json.dumps(SPEAKER_NOTES, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Notas del Presentador — Engineering with Gemma (32 Slides)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #FAF9F5;
      --surface: #FFFFFF;
      --surface-alt: #F3F1EC;
      --ink: #14171F;
      --slate: #334155;
      --muted: #64748B;
      --border: #E2E8F0;
      --blue: #1A73E8;
      --blue-bg: #EFF6FF;
      --teal: #0D9488;
      --teal-bg: #F0FDFA;
      --amber: #D97706;
      --amber-bg: #FFFBEB;
      --violet: #6D28D9;
      --violet-bg: #F5F3FF;
      --rose: #E11D48;
      --rose-bg: #FFF1F2;
      --script-font-size: 1.12rem;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--ink);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* TOP NAVBAR */
    header.topbar {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--border);
      padding: 0.75rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }}

    .brand-badge {{
      background: var(--blue);
      color: #fff;
      font-weight: 800;
      font-size: 0.8rem;
      padding: 0.35rem 0.65rem;
      border-radius: 6px;
      letter-spacing: 0.03em;
    }}

    .brand-title {{
      font-weight: 800;
      font-size: 1.05rem;
      color: var(--ink);
    }}

    .brand-sub {{
      font-size: 0.82rem;
      color: var(--muted);
    }}

    .controls-bar {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      flex-wrap: wrap;
    }}

    .mode-switch {{
      display: inline-flex;
      background: var(--surface-alt);
      padding: 0.22rem;
      border-radius: 8px;
      border: 1px solid var(--border);
    }}

    .mode-btn {{
      border: none;
      background: transparent;
      padding: 0.42rem 0.85rem;
      border-radius: 6px;
      font-family: inherit;
      font-size: 0.84rem;
      font-weight: 700;
      color: var(--slate);
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .mode-btn.active {{
      background: var(--surface);
      color: var(--blue);
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}

    .timer-box {{
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      background: var(--surface-alt);
      border: 1px solid var(--border);
      padding: 0.32rem 0.7rem;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.88rem;
      font-weight: 600;
    }}

    .btn {{
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--ink);
      padding: 0.4rem 0.75rem;
      border-radius: 7px;
      font-family: inherit;
      font-size: 0.83rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .btn:hover {{
      border-color: var(--blue);
      color: var(--blue);
    }}

    .btn-primary {{
      background: var(--blue);
      color: #fff;
      border-color: var(--blue);
    }}

    .btn-primary:hover {{
      background: #1557B0;
      color: #fff;
    }}

    /* PROGRESS TRACK */
    .progress-track {{
      height: 4px;
      background: var(--border);
      width: 100%;
    }}

    .progress-fill {{
      height: 100%;
      background: linear-gradient(90deg, var(--blue), var(--teal));
      width: 3.125%;
      transition: width 0.2s ease;
    }}

    /* PRESENTER SPLIT VIEW (1 SLIDE AT A TIME) */
    .presenter-view {{
      display: grid;
      grid-template-columns: 52% 48%;
      gap: 1.5rem;
      max-width: 1680px;
      width: 100%;
      margin: 0 auto;
      padding: 1.35rem 1.5rem 2.5rem;
      flex: 1;
    }}

    @media (max-width: 1100px) {{
      .presenter-view {{
        grid-template-columns: 1fr;
      }}
    }}

    .slide-column {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .slide-stage-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem;
      box-shadow: 0 6px 20px rgba(20, 23, 31, 0.05);
    }}

    .slide-stage-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.75rem;
      gap: 0.5rem;
    }}

    .slide-counter {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.86rem;
      font-weight: 700;
      color: var(--blue);
      background: var(--blue-bg);
      padding: 0.28rem 0.65rem;
      border-radius: 6px;
    }}

    .slide-select {{
      flex: 1;
      max-width: 380px;
      padding: 0.38rem 0.65rem;
      border-radius: 7px;
      border: 1px solid var(--border);
      font-family: inherit;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--ink);
      background: var(--surface);
    }}

    .slide-frame {{
      width: 100%;
      aspect-ratio: 16 / 9;
      background: #F8FAFC;
      border-radius: 10px;
      overflow: hidden;
      border: 1px solid var(--border);
      cursor: zoom-in;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .slide-frame img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }}

    .slide-nav-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 0.9rem;
      gap: 0.75rem;
    }}

    .kbd-hint {{
      font-size: 0.78rem;
      color: var(--muted);
    }}

    .kbd {{
      font-family: 'JetBrains Mono', monospace;
      background: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 0.1rem 0.38rem;
      font-size: 0.75rem;
      color: var(--ink);
    }}

    /* NEXT SLIDE MINI PREVIEW */
    .next-preview-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 0.85rem 1rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      cursor: pointer;
      transition: border-color 0.15s ease;
    }}

    .next-preview-card:hover {{
      border-color: var(--blue);
    }}

    .next-thumb {{
      width: 150px;
      aspect-ratio: 16 / 9;
      border-radius: 6px;
      border: 1px solid var(--border);
      overflow: hidden;
      flex-shrink: 0;
      background: var(--surface-alt);
    }}

    .next-thumb img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }}

    .next-info {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}

    .next-label {{
      font-size: 0.73rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
    }}

    .next-title {{
      font-size: 0.92rem;
      font-weight: 700;
      color: var(--ink);
    }}

    /* RIGHT COLUMN: SPEAKER NOTES */
    .notes-column {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .notes-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1.4rem 1.5rem;
      box-shadow: 0 6px 20px rgba(20, 23, 31, 0.05);
      display: flex;
      flex-direction: column;
      gap: 1.15rem;
    }}

    .meta-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.5rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.85rem;
    }}

    .block-pill {{
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--teal);
      background: var(--teal-bg);
      padding: 0.3rem 0.7rem;
      border-radius: 6px;
    }}

    .time-pill {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--amber);
      background: var(--amber-bg);
      padding: 0.3rem 0.7rem;
      border-radius: 6px;
    }}

    .notes-slide-title {{
      font-size: 1.4rem;
      font-weight: 800;
      color: var(--ink);
      line-height: 1.25;
    }}

    .objective-box {{
      background: var(--blue-bg);
      border-left: 4px solid var(--blue);
      padding: 0.75rem 1rem;
      border-radius: 0 8px 8px 0;
      font-size: 0.93rem;
      color: var(--slate);
      line-height: 1.5;
    }}

    .objective-box strong {{
      color: var(--ink);
    }}

    .section-label {{
      font-size: 0.78rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
      margin-bottom: 0.55rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .speech-paragraphs {{
      display: flex;
      flex-direction: column;
      gap: 0.9rem;
    }}

    .speech-p {{
      font-size: var(--script-font-size);
      line-height: 1.68;
      color: var(--ink);
      background: #FCFBF9;
      border: 1px solid #ECEAE2;
      padding: 0.9rem 1.1rem;
      border-radius: 10px;
    }}

    .pointout-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}

    .pointout-list li {{
      position: relative;
      padding-left: 1.35rem;
      font-size: 0.95rem;
      line-height: 1.5;
      color: var(--slate);
    }}

    .pointout-list li::before {{
      content: "👉";
      position: absolute;
      left: 0;
      top: 0;
    }}

    .transition-box {{
      background: var(--violet-bg);
      border-left: 4px solid var(--violet);
      padding: 0.75rem 1rem;
      border-radius: 0 8px 8px 0;
      font-size: 0.94rem;
      color: var(--ink);
      line-height: 1.45;
    }}

    code.inline-code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.88em;
      background: var(--surface-alt);
      border: 1px solid var(--border);
      padding: 0.1rem 0.38rem;
      border-radius: 5px;
      color: #0F172A;
    }}

    /* FULL LIST VIEW (ALL 32 SLIDES SIDE BY SIDE) */
    .list-view {{
      display: none;
      max-width: 1580px;
      width: 100%;
      margin: 0 auto;
      padding: 1.5rem;
      flex-direction: column;
      gap: 1.5rem;
    }}

    .filter-bar {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 0.9rem 1.2rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      flex-wrap: wrap;
    }}

    .search-input {{
      flex: 1;
      min-width: 240px;
      padding: 0.55rem 0.9rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-family: inherit;
      font-size: 0.92rem;
    }}

    .list-row {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1.25rem;
      display: grid;
      grid-template-columns: 44% 56%;
      gap: 1.5rem;
      align-items: start;
      box-shadow: 0 3px 12px rgba(20, 23, 31, 0.04);
    }}

    @media (max-width: 980px) {{
      .list-row {{
        grid-template-columns: 1fr;
      }}
    }}

    .list-slide-col {{
      position: sticky;
      top: 4.8rem;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}

    /* LIGHTBOX MODAL */
    .lightbox {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(20, 23, 31, 0.88);
      z-index: 999;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      cursor: zoom-out;
    }}

    .lightbox.open {{
      display: flex;
    }}

    .lightbox img {{
      max-width: 96vw;
      max-height: 92vh;
      border-radius: 10px;
      box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }}

    @media print {{
      header.topbar, .progress-track, .presenter-view, .filter-bar {{
        display: none !important;
      }}
      .list-view {{
        display: flex !important;
        padding: 0 !important;
      }}
      .list-row {{
        page-break-inside: avoid;
        box-shadow: none;
        border: 1px solid #ccc;
      }}
      .list-slide-col {{
        position: static;
      }}
    }}
  </style>
</head>
<body>

  <header class="topbar">
    <div class="brand">
      <span class="brand-badge">GEMMA 4</span>
      <div>
        <div class="brand-title">Engineering with Gemma — Consola del Presentador</div>
        <div class="brand-sub">Adrián Catalán (@adriancs.tech) · 32 Slides · Imagen + Guion Lado a Lado</div>
      </div>
    </div>

    <div class="controls-bar">
      <div class="mode-switch">
        <button id="btnModePresenter" class="mode-btn active" onclick="setMode('presenter')">🎤 Modo Presentador (1 a 1)</button>
        <button id="btnModeList" class="mode-btn" onclick="setMode('list')">📋 Ver los 32 Slides Juntos</button>
      </div>

      <div class="timer-box">
        <span>⏱</span>
        <span id="timerDisplay">00:00</span>
        <button class="btn" id="btnTimerToggle" onclick="toggleTimer()">▶</button>
        <button class="btn" onclick="resetTimer()">↺</button>
      </div>

      <button class="btn" onclick="adjustFont(-0.08)" title="Reducir tamaño de letra del guion">A-</button>
      <button class="btn" onclick="adjustFont(0.08)" title="Aumentar tamaño de letra del guion">A+</button>
    </div>
  </header>

  <div class="progress-track">
    <div class="progress-fill" id="progressFill"></div>
  </div>

  <!-- MODO 1: CONSOLA DEL PRESENTADOR (SLIDE ACTUAL + NOTAS AL LADO) -->
  <main class="presenter-view" id="presenterView">
    <!-- Columna Izquierda: Imagen del Slide + Navegación + Siguiente Slide -->
    <section class="slide-column">
      <div class="slide-stage-card">
        <div class="slide-stage-header">
          <span class="slide-counter" id="slideCounter">Slide 01 / 32</span>
          <select class="slide-select" id="slideSelect" onchange="goToSlide(parseInt(this.value, 10))"></select>
        </div>

        <div class="slide-frame" onclick="openLightbox(currentSlideIndex)" title="Clic para ampliar imagen del slide">
          <img id="currentSlideImg" src="slides/slide-01.png" alt="Slide actual" />
        </div>

        <div class="slide-nav-row">
          <button class="btn" id="btnPrev" onclick="prevSlide()">← Anterior</button>
          <span class="kbd-hint">Teclado: <span class="kbd">←</span> <span class="kbd">→</span> o <span class="kbd">Espacio</span> · Clic en el slide para zoom</span>
          <button class="btn btn-primary" id="btnNext" onclick="nextSlide()">Siguiente →</button>
        </div>
      </div>

      <!-- Tarjeta de Siguiente Slide -->
      <div class="next-preview-card" id="nextPreviewCard" onclick="nextSlide()">
        <div class="next-thumb">
          <img id="nextSlideImg" src="slides/slide-02.png" alt="Siguiente slide" />
        </div>
        <div class="next-info">
          <span class="next-label">Siguiente Slide →</span>
          <div class="next-title" id="nextSlideTitle">Slide 02 — Ruta de la sesión</div>
          <div class="brand-sub" id="nextSlideMeta">Apertura y Ecosistema Gemma 4 · 1.0 min</div>
        </div>
      </div>
    </section>

    <!-- Columna Derecha: Notas del Presentador -->
    <section class="notes-column">
      <div class="notes-card">
        <div class="meta-row">
          <span class="block-pill" id="noteBlock">Apertura y Ecosistema Gemma 4</span>
          <span class="time-pill" id="noteTime">Duración: 1.5 min (Acumulado: 00:00 – 01:30)</span>
        </div>

        <h1 class="notes-slide-title" id="noteTitle">Engineering with Gemma — Casos de uso y arquitecturas</h1>

        <div class="objective-box" id="noteObjective">
          <strong>🎯 Objetivo:</strong> Dar la bienvenida y presentar la premisa de ingeniería.
        </div>

        <div>
          <div class="section-label">
            <span>🗣️ Qué decir (Guion sugerido en voz alta)</span>
          </div>
          <div class="speech-paragraphs" id="noteSay"></div>
        </div>

        <div>
          <div class="section-label">
            <span>👉 Qué señalar en pantalla</span>
          </div>
          <ul class="pointout-list" id="notePointOut"></ul>
        </div>

        <div class="transition-box" id="noteTransition">
          <strong>⏭️ Puente al siguiente slide:</strong> ...
        </div>
      </div>
    </section>
  </main>

  <!-- MODO 2: LISTA COMPLETA DE LOS 32 SLIDES (IMAGEN + NOTAS LADO A LADO) -->
  <section class="list-view" id="listView">
    <div class="filter-bar">
      <input
        type="search"
        id="searchInput"
        class="search-input"
        placeholder="Buscar por tema, código, benchmark, LiteRT-LM, Cloud Run, Cover Letter..."
        oninput="renderListView()"
      />
      <select id="blockFilter" class="slide-select" onchange="renderListView()">
        <option value="ALL">Todos los bloques (32 slides)</option>
        <option value="Apertura y Ecosistema Gemma 4">Bloque 1: Apertura y Ecosistema Gemma 4 (Slides 1–6)</option>
        <option value="Arquitectura Interna de Gemma 4">Bloque 2: Arquitectura Interna de Gemma 4 (Slides 7–12)</option>
        <option value="Adaptación con Prompting, RAG y QLoRA">Bloque 3: Adaptación con Prompting, RAG y QLoRA (Slides 13–17)</option>
        <option value="Casos Split-Brain en Android y Cloud Run">Bloque 4: Casos Split-Brain en Android y Cloud Run (Slides 18–27)</option>
        <option value="Agentes con ADK para Kotlin y Lecciones">Bloque 5: Agentes con ADK para Kotlin y Lecciones (Slides 28–32)</option>
      </select>
      <button class="btn" onclick="window.print()">🖨️ Imprimir / Guardar PDF</button>
    </div>

    <div id="listContainer" style="display:flex; flex-direction:column; gap:1.35rem;"></div>
  </section>

  <!-- LIGHTBOX PARA AMPLIAR IMAGEN -->
  <div class="lightbox" id="lightbox" onclick="closeLightbox()">
    <img id="lightboxImg" src="" alt="Slide ampliado" />
  </div>

  <script>
    const SLIDES_DATA = {notes_json};
    let currentSlideIndex = 0;
    let fontScale = 1.12;

    // Cronómetro
    let timerSeconds = 0;
    let timerInterval = null;

    function pad2(n) {{
      return String(n).padStart(2, '0');
    }}

    function slideImagePath(slideNum) {{
      return `slides/slide-${{pad2(slideNum)}}.png`;
    }}

    function formatMd(str) {{
      if (!str) return '';
      const escaped = str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
      return escaped
        .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
        .replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
    }}

    function initSelect() {{
      const sel = document.getElementById('slideSelect');
      sel.innerHTML = SLIDES_DATA.map((item, idx) =>
        `<option value="${{idx}}">Slide ${{pad2(item.slide)}} — ${{item.title}}</option>`
      ).join('');
    }}

    function renderPresenterSlide() {{
      const item = SLIDES_DATA[currentSlideIndex];
      const total = SLIDES_DATA.length;

      document.getElementById('slideCounter').textContent = `Slide ${{pad2(item.slide)}} / ${{total}}`;
      document.getElementById('slideSelect').value = String(currentSlideIndex);
      document.getElementById('currentSlideImg').src = slideImagePath(item.slide);
      document.getElementById('progressFill').style.width = `${{((currentSlideIndex + 1) / total) * 100}}%`;

      document.getElementById('noteBlock').textContent = item.block;
      document.getElementById('noteTime').textContent = `Duración: ${{item.duration}} (Acumulado: ${{item.cumulative}})`;
      document.getElementById('noteTitle').textContent = `${{item.slide}}. ${{item.title}}`;
      document.getElementById('noteObjective').innerHTML = `<strong>🎯 Objetivo:</strong> ${{formatMd(item.objective)}}`;

      const sayEl = document.getElementById('noteSay');
      sayEl.innerHTML = item.say.map(p => `<p class="speech-p">“${{formatMd(p)}}”</p>`).join('');

      const pointEl = document.getElementById('notePointOut');
      pointEl.innerHTML = item.point_out.map(pt => `<li>${{formatMd(pt)}}</li>`).join('');

      document.getElementById('noteTransition').innerHTML = `<strong>⏭️ Puente al siguiente slide:</strong> “${{formatMd(item.transition)}}”`;

      document.getElementById('btnPrev').disabled = currentSlideIndex === 0;
      document.getElementById('btnNext').disabled = currentSlideIndex === total - 1;

      const nextCard = document.getElementById('nextPreviewCard');
      if (currentSlideIndex < total - 1) {{
        const nextItem = SLIDES_DATA[currentSlideIndex + 1];
        nextCard.style.display = 'flex';
        document.getElementById('nextSlideImg').src = slideImagePath(nextItem.slide);
        document.getElementById('nextSlideTitle').textContent = `Slide ${{pad2(nextItem.slide)}} — ${{nextItem.title}}`;
        document.getElementById('nextSlideMeta').textContent = `${{nextItem.block}} · ${{nextItem.duration}}`;
      }} else {{
        nextCard.style.display = 'none';
      }}

      window.history.replaceState(null, '', `#slide-${{item.slide}}`);
    }}

    function goToSlide(idx) {{
      if (idx < 0 || idx >= SLIDES_DATA.length) return;
      currentSlideIndex = idx;
      renderPresenterSlide();
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function nextSlide() {{
      if (currentSlideIndex < SLIDES_DATA.length - 1) {{
        goToSlide(currentSlideIndex + 1);
      }}
    }}

    function prevSlide() {{
      if (currentSlideIndex > 0) {{
        goToSlide(currentSlideIndex - 1);
      }}
    }}

    function setMode(mode) {{
      const pres = document.getElementById('presenterView');
      const list = document.getElementById('listView');
      const bPres = document.getElementById('btnModePresenter');
      const bList = document.getElementById('btnModeList');

      if (mode === 'list') {{
        pres.style.display = 'none';
        list.style.display = 'flex';
        bPres.classList.remove('active');
        bList.classList.add('active');
        renderListView();
      }} else {{
        pres.style.display = 'grid';
        list.style.display = 'none';
        bPres.classList.add('active');
        bList.classList.remove('active');
        renderPresenterSlide();
      }}
    }}

    function renderListView() {{
      const q = (document.getElementById('searchInput').value || '').toLowerCase().trim();
      const blk = document.getElementById('blockFilter').value;
      const container = document.getElementById('listContainer');

      const filtered = SLIDES_DATA.filter(item => {{
        if (blk !== 'ALL' && item.block !== blk) return false;
        if (!q) return true;
        const haystack = [
          item.title,
          item.block,
          item.objective,
          ...item.say,
          ...item.point_out,
          item.transition
        ].join(' ').toLowerCase();
        return haystack.includes(q);
      }});

      container.innerHTML = filtered.map(item => `
        <article class="list-row" id="row-slide-${{item.slide}}">
          <div class="list-slide-col">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span class="slide-counter">Slide ${{pad2(item.slide)}} / 32</span>
              <button class="btn" onclick="setMode('presenter'); goToSlide(${{item.slide - 1}});">🎤 Abrir en Modo Presentador</button>
            </div>
            <div class="slide-frame" onclick="openLightbox(${{item.slide - 1}})">
              <img src="${{slideImagePath(item.slide)}}" alt="Slide ${{item.slide}}" loading="lazy" />
            </div>
          </div>

          <div style="display:flex; flex-direction:column; gap:0.95rem;">
            <div class="meta-row">
              <span class="block-pill">${{item.block}}</span>
              <span class="time-pill">Duración: ${{item.duration}} (${{item.cumulative}})</span>
            </div>
            <h2 class="notes-slide-title">${{item.slide}}. ${{item.title}}</h2>
            <div class="objective-box"><strong>🎯 Objetivo:</strong> ${{formatMd(item.objective)}}</div>

            <div>
              <div class="section-label"><span>🗣️ Qué decir</span></div>
              <div class="speech-paragraphs">
                ${{item.say.map(p => `<p class="speech-p">“${{formatMd(p)}}”</p>`).join('')}}
              </div>
            </div>

            <div>
              <div class="section-label"><span>👉 Qué señalar en pantalla</span></div>
              <ul class="pointout-list">
                ${{item.point_out.map(pt => `<li>${{formatMd(pt)}}</li>`).join('')}}
              </ul>
            </div>

            <div class="transition-box">
              <strong>⏭️ Puente al siguiente slide:</strong> “${{formatMd(item.transition)}}”
            </div>
          </div>
        </article>
      `).join('');
    }}

    function adjustFont(delta) {{
      fontScale = Math.max(0.92, Math.min(1.55, fontScale + delta));
      document.documentElement.style.setProperty('--script-font-size', fontScale.toFixed(2) + 'rem');
    }}

    function openLightbox(idx) {{
      const item = SLIDES_DATA[idx];
      document.getElementById('lightboxImg').src = slideImagePath(item.slide);
      document.getElementById('lightbox').classList.add('open');
    }}

    function closeLightbox() {{
      document.getElementById('lightbox').classList.remove('open');
    }}

    function updateTimerUI() {{
      const mins = Math.floor(timerSeconds / 60);
      const secs = timerSeconds % 60;
      document.getElementById('timerDisplay').textContent = `${{pad2(mins)}}:${{pad2(secs)}}`;
    }}

    function toggleTimer() {{
      const btn = document.getElementById('btnTimerToggle');
      if (timerInterval) {{
        clearInterval(timerInterval);
        timerInterval = null;
        btn.textContent = '▶';
      }} else {{
        timerInterval = setInterval(() => {{
          timerSeconds++;
          updateTimerUI();
        }}, 1000);
        btn.textContent = '⏸';
      }}
    }}

    function resetTimer() {{
      if (timerInterval) {{
        clearInterval(timerInterval);
        timerInterval = null;
      }}
      timerSeconds = 0;
      updateTimerUI();
      document.getElementById('btnTimerToggle').textContent = '▶';
    }}

    window.addEventListener('keydown', (e) => {{
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
      if (e.key === 'Escape') {{
        closeLightbox();
        return;
      }}
      const isList = document.getElementById('listView').style.display === 'flex';
      if (isList) return;

      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown' || e.key === 'j') {{
        e.preventDefault();
        nextSlide();
      }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp' || e.key === 'k') {{
        e.preventDefault();
        prevSlide();
      }}
    }});

    // Inicializar
    initSelect();
    const hashMatch = window.location.hash.match(/slide-(\\d+)/);
    if (hashMatch) {{
      const sNum = parseInt(hashMatch[1], 10);
      if (sNum >= 1 && sNum <= SLIDES_DATA.length) {{
        currentSlideIndex = sNum - 1;
      }}
    }}
    renderPresenterSlide();
  </script>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Generated {OUT_HTML}")


if __name__ == "__main__":
    build_markdown()
    build_html()
