#!/usr/bin/env python3
"""
Builds Gemma_Charla_2027.pptx:
"Engineering with Gemma: Casos de uso y arquitecturas"
Combines local edge execution on Android (LiteRT-LM + ADK for Kotlin, Excusa Legendaria)
and private service orchestration on Cloud Run (Ollama + GPU L4/CPU, Cover Letter).
Strictly adheres to adrian-slides skill:
- Minimalist cover without extra summary cards or tags/pills.
- Short, clean subtitle on cover.
- Zero "PARTE 01..05" or numbered counts in section headers/titles.
- Zero AI cliché phrases like "para empezar hoy" / "para empezar el lunes" / "X ideas para llevarte hoy".
- 100% Light Mode slide backgrounds (#FAF9F5). Dark background (#181A24) ONLY for syntax-highlighted code panels.
"""

import re
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from speaker_notes_data import SPEAKER_NOTES

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT_PPTX = ROOT / "Gemma_Charla_2027.pptx"

# 100% Light Editorial Palette
BG_LIGHT = RGBColor(0xFA, 0xF9, 0xF5)     # #FAF9F5 Warm paper
BG_SECTION = RGBColor(0xF3, 0xF1, 0xEC)   # #F3F1EC Soft stone
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x14, 0x17, 0x1F)          # #14171F Deep charcoal ink
SLATE = RGBColor(0x33, 0x41, 0x55)        # #334155 Body text
MUTED = RGBColor(0x64, 0x74, 0x8B)        # #64748B Captions / subtitles
BORDER = RGBColor(0xE2, 0xE8, 0xF0)       # #E2E8F0 Crisp card border

# Semantic Accents
BLUE = RGBColor(0x1A, 0x73, 0xE8)
BLUE_BG = RGBColor(0xEF, 0xF6, 0xFF)
TEAL = RGBColor(0x0D, 0x94, 0x88)
TEAL_BG = RGBColor(0xF0, 0xFD, 0xFA)
AMBER = RGBColor(0xD9, 0x77, 0x06)
AMBER_BG = RGBColor(0xFF, 0xFB, 0xEB)
VIOLET = RGBColor(0x6D, 0x28, 0xD9)
VIOLET_BG = RGBColor(0xF5, 0xF3, 0xFF)
ROSE = RGBColor(0xE1, 0x1D, 0x48)
ROSE_BG = RGBColor(0xFF, 0xF1, 0xF2)

# Code Block Palette (Dark ONLY inside code panels)
CODE_BG = RGBColor(0x18, 0x1A, 0x24)
CODE_HDR = RGBColor(0x23, 0x27, 0x36)
CODE_BORDER = RGBColor(0x33, 0x3B, 0x4D)
SYN_KW = RGBColor(0xF0, 0x8D, 0xD0)       # Pink/magenta keywords
SYN_STR = RGBColor(0xA6, 0xE2, 0x8E)      # Green strings
SYN_CMT = RGBColor(0x8A, 0x93, 0xAD)      # Muted slate comments
SYN_NUM = RGBColor(0xF7, 0xBE, 0x74)      # Amber numbers/constants
SYN_DEC = RGBColor(0x7A, 0xCA, 0xFF)      # Cyan types/annotations/calls
SYN_DEF = RGBColor(0xF1, 0xF3, 0xF8)      # Crisp light foreground

FONT_SANS = "Plus Jakarta Sans"
FONT_MONO = "JetBrains Mono"

TOKEN_RE = re.compile(
    r'("//.*$|#.*$)'
    r'|("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'
    r'|(@\w+|<start_of_turn>|<end_of_turn>|--[a-z0-9-]+)'
    r'|\b(suspend|fun|val|var|class|object|interface|return|if|else|when|for|in|is|true|false|null|private|override|data|sealed|import|from|def|async|await|with|as|try|catch|export|const|type|function|FROM|ENV|ARG|RUN|ENTRYPOINT)\b'
    r'|\b(\d+(?:\.\d+)?[fFL]?)\b'
    r'|\b([A-Z][A-Za-z0-9_]*)\b'
)


def tokenize_code_line(line: str):
    """Splits a code line into (text, RGBColor) tuples for syntax highlighting."""
    stripped = line.lstrip()
    if stripped.startswith("//") or stripped.startswith("#"):
        return [(line, SYN_CMT)]
    tokens = []
    pos = 0
    for m in TOKEN_RE.finditer(line):
        if m.start() > pos:
            tokens.append((line[pos:m.start()], SYN_DEF))
        cmt, string, ann, kw, num, typ = m.groups()
        if cmt:
            tokens.append((cmt, SYN_CMT))
        elif string:
            tokens.append((string, SYN_STR))
        elif ann:
            tokens.append((ann, SYN_DEC))
        elif kw:
            tokens.append((kw, SYN_KW))
        elif num:
            tokens.append((num, SYN_NUM))
        elif typ:
            tokens.append((typ, SYN_DEC))
        pos = m.end()
    if pos < len(line):
        tokens.append((line[pos:], SYN_DEF))
    return tokens if tokens else [("", SYN_DEF)]


def new_slide(prs, bg_color=BG_LIGHT):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = bg_color
    bg.line.fill.background()
    return slide


def add_top_stripe(slide, color=BLUE):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()


def add_header(slide, title: str, subtitle: str = None, accent=BLUE):
    """Clean editorial header using a single text frame so title and subtitle can never overlap."""
    add_top_stripe(slide, accent)
    tb = slide.shapes.add_textbox(Inches(0.75), Inches(0.36), Inches(11.833), Inches(1.12))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.space_after = Pt(6)
    r = p.add_run()
    r.text = title
    r.font.name = FONT_SANS
    r.font.size = Pt(26.5)
    r.font.bold = True
    r.font.color.rgb = INK

    if subtitle:
        sp = tf.add_paragraph()
        sr = sp.add_run()
        sr.text = subtitle
        sr.font.name = FONT_SANS
        sr.font.size = Pt(15)
        sr.font.color.rgb = MUTED


def add_card(slide, left, top, width, height, title=None, body=None, bullets=None,
             bg=WHITE, border=BORDER, accent=BLUE, title_size=18, body_size=14.5):
    """Clean editorial card with top accent bar and zero overlapping badges."""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    card.adjustments[0] = 0.03
    card.fill.solid()
    card.fill.fore_color.rgb = bg
    card.line.color.rgb = border
    card.line.width = Pt(1)

    if accent:
        stripe = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(left + 0.18), Inches(top), Inches(min(1.1, width - 0.36)), Inches(0.055)
        )
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = accent
        stripe.line.fill.background()

    tb = slide.shapes.add_textbox(
        Inches(left + 0.24), Inches(top + 0.20), Inches(width - 0.48), Inches(height - 0.34)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    first = True
    if title:
        p = tf.paragraphs[0]
        first = False
        p.space_after = Pt(8)
        r = p.add_run()
        r.text = title
        r.font.name = FONT_SANS
        r.font.size = Pt(title_size)
        r.font.bold = True
        r.font.color.rgb = INK

    if body:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(8)
        r = p.add_run()
        r.text = body
        r.font.name = FONT_SANS
        r.font.size = Pt(body_size)
        r.font.color.rgb = SLATE

    if bullets:
        for b in bullets:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_after = Pt(6)
            if isinstance(b, tuple):
                lead, rest = b
                r0 = p.add_run()
                r0.text = "• " + lead + " "
                r0.font.name = FONT_SANS
                r0.font.size = Pt(body_size)
                r0.font.bold = True
                r0.font.color.rgb = INK
                r1 = p.add_run()
                r1.text = rest
                r1.font.name = FONT_SANS
                r1.font.size = Pt(body_size)
                r1.font.color.rgb = SLATE
            else:
                r = p.add_run()
                r.text = "• " + b
                r.font.name = FONT_SANS
                r.font.size = Pt(body_size)
                r.font.color.rgb = SLATE


def add_code_panel(slide, left, top, width, height, filename: str, code_lines: list, font_size=12.5):
    """Dark syntax-highlighted IDE code panel."""
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    box.adjustments[0] = 0.025
    box.fill.solid()
    box.fill.fore_color.rgb = CODE_BG
    box.line.color.rgb = CODE_BORDER
    box.line.width = Pt(1)

    hdr_h = 0.42
    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(hdr_h)
    )
    hdr.adjustments[0] = 0.025
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = CODE_HDR
    hdr.line.fill.background()

    # Traffic light dots
    for idx, col in enumerate([RGBColor(0xFF, 0x5F, 0x56), RGBColor(0xFF, 0xBD, 0x2E), RGBColor(0x27, 0xC9, 0x3F)]):
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(left + 0.18 + idx * 0.20), Inches(top + 0.14), Inches(0.12), Inches(0.12)
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = col
        dot.line.fill.background()

    ftb = slide.shapes.add_textbox(Inches(left + 0.85), Inches(top + 0.08), Inches(width - 1.0), Inches(0.28))
    ftf = ftb.text_frame
    ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
    fp = ftf.paragraphs[0]
    fr = fp.add_run()
    fr.text = filename
    fr.font.name = FONT_MONO
    fr.font.size = Pt(11)
    fr.font.bold = True
    fr.font.color.rgb = SYN_CMT

    ctb = slide.shapes.add_textbox(
        Inches(left + 0.22), Inches(top + hdr_h + 0.12), Inches(width - 0.44), Inches(height - hdr_h - 0.22)
    )
    ctf = ctb.text_frame
    ctf.word_wrap = False
    ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0

    for i, line in enumerate(code_lines):
        p = ctf.paragraphs[0] if i == 0 else ctf.add_paragraph()
        p.space_after = Pt(2.5)
        for text_seg, color_rgb in tokenize_code_line(line):
            r = p.add_run()
            r.text = text_seg if text_seg else " "
            r.font.name = FONT_MONO
            r.font.size = Pt(font_size)
            r.font.color.rgb = color_rgb


def add_fitted_picture(slide, img_path: Path, left: float, top: float, max_w: float, max_h: float, with_card=True):
    """Inserts an image centered within (left, top, max_w, max_h) preserving exact aspect ratio."""
    if with_card:
        frame = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(max_w), Inches(max_h)
        )
        frame.adjustments[0] = 0.02
        frame.fill.solid()
        frame.fill.fore_color.rgb = WHITE
        frame.line.color.rgb = BORDER
        frame.line.width = Pt(1)
        pad = 0.12
    else:
        pad = 0.0

    avail_w = max_w - 2 * pad
    avail_h = max_h - 2 * pad

    with Image.open(img_path) as im:
        iw, ih = im.size
    aspect = iw / ih

    if avail_w / avail_h > aspect:
        h = avail_h
        w = h * aspect
    else:
        w = avail_w
        h = w / aspect

    x = left + pad + (avail_w - w) / 2
    y = top + pad + (avail_h - h) / 2
    slide.shapes.add_picture(str(img_path), Inches(x), Inches(y), width=Inches(w), height=Inches(h))


def add_section_slide(prs, title: str, subtitle: str, accent=BLUE):
    """Light editorial section transition slide — zero numbering/counts, never dark background."""
    s = new_slide(prs, BG_SECTION)
    add_top_stripe(s, accent)

    vbar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.95), Inches(2.35), Inches(0.10), Inches(2.6))
    vbar.fill.solid()
    vbar.fill.fore_color.rgb = accent
    vbar.line.fill.background()

    tb = s.shapes.add_textbox(Inches(1.35), Inches(2.35), Inches(10.8), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    p1.space_after = Pt(16)
    r1 = p1.add_run()
    r1.text = title
    r1.font.name = FONT_SANS
    r1.font.size = Pt(42)
    r1.font.bold = True
    r1.font.color.rgb = INK

    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = subtitle
    r2.font.name = FONT_SANS
    r2.font.size = Pt(20)
    r2.font.color.rgb = SLATE
    return s


def add_statement_slide(prs, headline: str, subtext: str, takeaway: str, accent=BLUE):
    """High-impact light editorial statement slide."""
    s = new_slide(prs, BG_LIGHT)
    add_top_stripe(s, accent)

    card = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(1.25), Inches(11.633), Inches(5.0)
    )
    card.adjustments[0] = 0.025
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = BORDER
    card.line.width = Pt(1.2)

    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.85), Inches(1.25), Inches(0.12), Inches(5.0))
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent
    bar.line.fill.background()

    tb = s.shapes.add_textbox(Inches(1.45), Inches(1.75), Inches(10.5), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.space_after = Pt(20)
    r0 = p0.add_run()
    r0.text = headline
    r0.font.name = FONT_SANS
    r0.font.size = Pt(34)
    r0.font.bold = True
    r0.font.color.rgb = INK

    p1 = tf.add_paragraph()
    p1.space_after = Pt(26)
    r1 = p1.add_run()
    r1.text = subtext
    r1.font.name = FONT_SANS
    r1.font.size = Pt(19)
    r1.font.color.rgb = SLATE

    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = takeaway
    r2.font.name = FONT_MONO
    r2.font.size = Pt(15)
    r2.font.bold = True
    r2.font.color.rgb = accent
    return s


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # =========================================================================
    # SLIDE 1: PORTADA MINIMALISTA (Cero tags, subtítulo corto, sin caja derecha)
    # =========================================================================
    s = new_slide(prs, BG_LIGHT)
    add_top_stripe(s, BLUE)

    vbar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.85), Inches(1.75), Inches(0.12), Inches(2.25))
    vbar.fill.solid()
    vbar.fill.fore_color.rgb = BLUE
    vbar.line.fill.background()

    tb = s.shapes.add_textbox(Inches(1.25), Inches(1.70), Inches(10.8), Inches(2.6))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.space_after = Pt(12)
    r0 = p0.add_run()
    r0.text = "Engineering with Gemma"
    r0.font.name = FONT_SANS
    r0.font.size = Pt(50)
    r0.font.bold = True
    r0.font.color.rgb = INK

    p1 = tf.add_paragraph()
    r1 = p1.add_run()
    r1.text = "Casos de uso y arquitecturas"
    r1.font.name = FONT_SANS
    r1.font.size = Pt(24)
    r1.font.color.rgb = SLATE

    # Single clean speaker card at bottom left
    add_card(
        s, 0.85, 5.25, 5.2, 1.35,
        title="Adrián Catalán",
        body="Google Developer Expert · @adriancs.tech",
        bg=WHITE, border=BORDER, accent=BLUE, title_size=20, body_size=15
    )

    # =========================================================================
    # SLIDE 2: MAPA DE LA SESIÓN (Sin numeración 1..5)
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Ruta de la sesión", "De la arquitectura interna de Gemma a implementaciones en Android y Cloud Run")
    blocks = [
        ("Ecosistema y Anatomía de Gemma 4", "Modelos abiertos, tokenización 256k, Atención Híbrida 5 a 1, PLE y QAT INT4.", BLUE, BLUE_BG),
        ("Adaptación con Prompting, RAG y QLoRA", "Búsqueda híbrida BM25 + vectores Matryoshka en SQLite y ajuste fino con RAFT.", VIOLET, VIOLET_BG),
        ("Arquitecturas Split-Brain en Android", "Caso Excusa Legendaria con inferencia local en LiteRT-LM y guardrails en Kotlin.", TEAL, TEAL_BG),
        ("Orquestación Privada en Cloud Run", "Caso Cover Letter con Gemma 4 en Ollama sobre GPU L4, router por niveles y benchmarks.", AMBER, AMBER_BG),
        ("Agentes con ADK para Kotlin", "Tool calling tipado, confirmación humana, Skills bajo demanda y sesiones en Room.", ROSE, ROSE_BG),
    ]
    for idx, (t_str, b_str, col, bg_c) in enumerate(blocks):
        y = 1.65 + idx * 1.04
        add_card(s, 0.75, y, 11.833, 0.90, title=t_str, body=b_str, bg=WHITE, accent=col, title_size=17, body_size=14)

    # =========================================================================
    # SLIDE 3: LA FALACIA DEL MODELO ÚNICO
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "El problema de enviar todo a un único LLM externo", "Depender de un solo modelo remoto para cada tarea compromete latencia, costos y privacidad")
    add_card(
        s, 0.75, 1.75, 3.75, 4.8,
        title="Latencia y Conectividad",
        bullets=[
            ("RTT de red", "300 a 1,500 ms antes de recibir el primer token."),
            ("Modo offline", "En móvil o campo la app falla sin cobertura estable."),
            ("Cold starts", "Despertar instancias remotas exige diseñar estados de espera."),
        ],
        accent=ROSE, title_size=21, body_size=15.5
    )
    add_card(
        s, 4.79, 1.75, 3.75, 4.8,
        title="Costo Operativo",
        bullets=[
            ("Impuesto por token", "Pagar un modelo frontera para extraer un JSON simple o clasificar."),
            ("Contexto repetido", "Reenviar historiales largos encarece cada petición."),
            ("Escalabilidad", "Un modelo 2B propio en el borde o Cloud Run reduce el costo marginal."),
        ],
        accent=AMBER, title_size=21, body_size=15.5
    )
    add_card(
        s, 8.83, 1.75, 3.75, 4.8,
        title="Frontera de Privacidad",
        bullets=[
            ("Datos sensibles", "Salarios, nombres, salud y finanzas no deben llegar a terceros."),
            ("Control del perímetro", "Necesitas decidir qué corre en el cliente, en tu nube o en API externa."),
            ("Verificabilidad", "Un prompt no garantiza que un dato privado no viaje por la red."),
        ],
        accent=BLUE, title_size=21, body_size=15.5
    )

    # =========================================================================
    # SLIDE 4: GEMINI VS GEMMA
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Gemini y Gemma comparten ciencia pero cumplen roles distintos", "Diseñados para combinarse entre el dispositivo del usuario, tus servicios y la nube")
    add_card(
        s, 0.75, 1.75, 5.75, 4.85,
        title="Gemini (API Gestionada en Vertex AI / Firebase)",
        bullets=[
            ("Escala masiva", "Razonamiento amplio y redacción final de alta calidad."),
            ("Cero infraestructura", "Consumo directo por llamada sin administrar GPUs."),
            ("Rol en la arquitectura", "Recibe únicamente payloads ya sanitizados y libres de PII."),
        ],
        bg=AMBER_BG, accent=AMBER, title_size=21, body_size=15.5
    )
    add_card(
        s, 6.83, 1.75, 5.75, 4.85,
        title="Gemma 4 (Pesos Abiertos Apache 2.0)",
        bullets=[
            ("Control del despliegue", "Corre en Android con LiteRT-LM o en tu propio Cloud Run con Ollama."),
            ("Eficiencia extrema", "Modelos E2B y E4B diseñados para operar en 1.1 a 1.8 GB de VRAM."),
            ("Rol en la arquitectura", "Procesa datos sensibles dentro de tu perímetro de confianza."),
        ],
        bg=TEAL_BG, accent=TEAL, title_size=21, body_size=15.5
    )

    # =========================================================================
    # SLIDE 5: DIAGRAMA ECOSISTEMA GEMMA 4 (diagram-design)
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "El ecosistema Gemma 4 de un vistazo", "Desde sub-modelos multimodales para teléfonos hasta arquitecturas MoE para servidores")
    add_fitted_picture(s, ASSETS / "gemma-family-map.png", 0.75, 1.55, 11.833, 5.55)

    # =========================================================================
    # SLIDE 6: MODELOS ESPECIALIZADOS (4 bloques concisos — estilo aprobado)
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Modelos especializados del ecosistema Gemma", "Herramientas quirúrgicas para problemas específicos sin inflar la memoria")
    specs = [
        ("EmbeddingGemma 2 (308M)", "Vectores multilingües con Matryoshka (768 → 128 dims) para búsqueda semántica local en milisegundos.", VIOLET),
        ("ShieldGemma 2 (4B)", "Clasificador de seguridad de texto e imágenes para filtrar prompts tóxicos o fugas antes de responder.", ROSE),
        ("FunctionGemma", "Especializado en traducir lenguaje natural a invocaciones JSON deterministas de herramientas y APIs.", BLUE),
        ("PaliGemma 2 / MedGemma", "Modelos visión-lenguaje para detección de objetos en cámara, lectura de documentos y soporte clínico.", TEAL),
    ]
    coords = [(0.75, 1.75), (6.83, 1.75), (0.75, 4.35), (6.83, 4.35)]
    for (title, desc, col), (x, y) in zip(specs, coords):
        add_card(s, x, y, 5.75, 2.30, title=title, body=desc, accent=col, title_size=20, body_size=15.5)

    # =========================================================================
    # SLIDE 7: SECCIÓN — TEORÍA Y ANATOMÍA INTERNA DE GEMMA 4 (Sin conteo PARTE)
    # =========================================================================
    add_section_slide(
        prs,
        "Arquitectura interna de Gemma 4",
        "Tokenización multimodal, Atención Híbrida 5 a 1, Per-Layer Embeddings, QAT de 4 bits y alineación Instruct.",
        accent=TEAL
    )

    # =========================================================================
    # SLIDE 8: TEORÍA — TOKENIZACIÓN 256K Y MULTIMODALIDAD NATIVA
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Tokenización 256k y entradas multimodales nativas", "Texto, imagen y audio se proyectan al mismo espacio de embeddings antes de entrar al Transformer", accent=TEAL)
    add_card(
        s, 0.75, 1.70, 3.75, 4.9,
        title="Texto (SentencePiece 256k)",
        bullets=[
            ("Vocabulario de 256,000 tokens", "Comprime español y código sin fragmentar palabras."),
            ("30% menos tokens", "Comparado con tokenizadores de 32k, ahorrando batería y KV Cache."),
            ("Byte-fallback", "Soporta emojis, símbolos matemáticos y +140 idiomas sin errores <unk>."),
        ],
        accent=BLUE, title_size=19, body_size=14.5
    )
    add_card(
        s, 4.79, 1.70, 3.75, 4.9,
        title="Visión (Parches ViT)",
        bullets=[
            ("Resolución dinámica", "Divide fotos o capturas de UI en parches visuales."),
            ("Conector lineal", "Proyecta cada parche como ~256 tokens visuales en el flujo."),
            ("Cero OCR externo", "Lee recibos, etiquetas médicas y pantallas de Android directamente."),
        ],
        accent=TEAL, title_size=19, body_size=14.5
    )
    add_card(
        s, 8.83, 1.70, 3.75, 4.9,
        title="Audio Nativo (USM)",
        bullets=[
            ("En E2B y E4B", "Codificador basado en Universal Speech Model."),
            ("~25 tokens por segundo", "Convierte espectrogramas Mel en tokens acústicos discretos."),
            ("Voz directa", "Entiende notas de voz con tono e idioma sin pasar por un STT separado."),
        ],
        accent=VIOLET, title_size=19, body_size=14.5
    )

    # =========================================================================
    # SLIDE 9: DIAGRAMA ATENCIÓN 5:1, KV CACHE, PLE Y QAT
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Innovaciones que hacen viable Gemma 4 en móvil y GPU ligera", "Atención Híbrida 5 a 1 para contexto largo, PLE para capacidad extra y QAT nativo en 4 bits", accent=TEAL)
    add_fitted_picture(s, ASSETS / "attention-kv-qat.png", 0.75, 1.55, 11.833, 5.55)

    # =========================================================================
    # SLIDE 10: PRE-TRAINING (-PT) VS POST-TRAINING (-IT)
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "De completar texto a seguir instrucciones en modelos -pt vs -it", "Por qué nunca debes desplegar un checkpoint -pt directamente en un chat o agente", accent=TEAL)
    add_fitted_picture(s, ASSETS / "training-pipeline.png", 0.75, 1.55, 11.833, 5.55)

    # =========================================================================
    # SLIDE 11: CÓDIGO — FORMATO DE TURNOS Y EXTRACCIÓN JSON EN GEMMA 4
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Anatomía de un prompt determinista para Gemma 4", "En modelos 2B y 4B las restricciones explícitas, el idioma sin ambigüedad y los ejemplos son clave", accent=TEAL)
    add_code_panel(
        s, 0.75, 1.65, 7.65, 5.2,
        "gemma4_structured_prompt.txt",
        [
            "<start_of_turn>user",
            "Eres un extractor de entidades médicas 100% local.",
            "Responde SOLO con JSON válido sin bloques markdown.",
            "",
            "Esquema: {\"paciente\": string, \"med\": string, \"mg\": number}",
            "",
            "Ejemplo:",
            "Entrada: \"Dar a Laura Gómez 500mg de Amoxicilina\"",
            "Salida: {\"paciente\": \"Laura Gómez\", \"med\": \"Amoxicilina\", \"mg\": 500}",
            "",
            "Entrada: \"Carlos Ruiz tomó 400mg de Ibuprofeno\"",
            "Salida:<end_of_turn>",
            "<start_of_turn>model",
            "{\"paciente\": \"Carlos Ruiz\", \"med\": \"Ibuprofeno\", \"mg\": 400}<end_of_turn>",
        ],
        font_size=11.8
    )
    add_card(
        s, 8.65, 1.65, 3.93, 5.2,
        title="Diseño de prompts en 2B / 4B",
        bullets=[
            ("Desambiguar términos", "Un modelo 2B puede leer 'carta de interés' como interés bancario si no aclaras 'cover letter'."),
            ("One-shot sobre Zero-shot", "Un ejemplo concreto reduce errores de esquema JSON en más del 80%."),
            ("Temperatura 0", "Usa temperature = 0 y format JSON Schema en tareas de extracción."),
        ],
        accent=TEAL, title_size=19, body_size=14.5
    )

    # =========================================================================
    # SLIDE 12: CÓDIGO — INFERENCIA LOCAL EN ANDROID CON LITERT-LM
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Ejecutando Gemma 4 en Android con LiteRT-LM", "Carga de un paquete .litertlm cuantizado en GPU/NPU móvil y generación en streaming", accent=TEAL)
    add_code_panel(
        s, 0.75, 1.65, 7.65, 5.2,
        "LocalGemmaBrain.kt (LiteRT-LM SDK)",
        [
            "class LocalGemmaBrain(private val context: Context) {",
            "    private var engine: Engine? = null",
            "    private var conversation: Conversation? = null",
            "",
            "    suspend fun initialize(modelFile: File) {",
            "        val config = EngineConfig(",
            "            modelPath = modelFile.absolutePath,",
            "            backend = Backend.GPU, // Delega a GPU / NPU",
            "            maxNumTokens = 2048",
            "        )",
            "        engine = Engine(config).also { it.initialize() }",
            "        conversation = engine?.createConversation()",
            "    }",
            "",
            "    suspend fun stream(prompt: String, onToken: (String) -> Unit) {",
            "        conversation?.sendMessageAsync(prompt)?.collect { chunk ->",
            "            onToken(chunk.toString())",
            "        }",
            "    }",
            "}",
        ],
        font_size=11.6
    )
    add_card(
        s, 8.65, 1.65, 3.93, 5.2,
        title="Qué resuelve LiteRT-LM",
        bullets=[
            ("Formato .litertlm", "Empaqueta pesos INT4, tokenizer SentencePiece y metadatos de parada."),
            ("Aceleración hardware", "Delega operaciones matriciales a GPU (OpenCL/Vulkan) o NPU Qualcomm/MediaTek."),
            ("Cero servidor", "No requiere claves de API ni conexión de red para inferir."),
        ],
        accent=BLUE, title_size=19, body_size=14.5
    )

    # =========================================================================
    # SLIDE 13: SECCIÓN — ADAPTACIÓN: PROMPTING, RAG Y LORA (Sin conteo PARTE)
    # =========================================================================
    add_section_slide(
        prs,
        "Adaptación con Prompting, RAG y QLoRA",
        "Cuándo inyectar contexto con vectores Matryoshka y cuándo modificar el comportamiento con adaptadores de bajo rango.",
        accent=VIOLET
    )

    # =========================================================================
    # SLIDE 14: MATRIZ DE DECISIÓN: PROMPTING VS RAG VS LORA
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Criterios para elegir entre Prompting, RAG y Fine-Tuning", "Escala la complejidad técnica solo cuando el escalón anterior no resuelve el problema", accent=VIOLET)
    add_card(
        s, 0.75, 1.75, 3.75, 4.85,
        title="Prompt Engineering",
        bullets=[
            ("Qué cambia", "Las instrucciones de entrada, el esquema JSON y ejemplos few-shot."),
            ("Caso de uso", "Reglas claras, extracción de requisitos y redacción guiada."),
            ("Costo e iteración", "0 GPUs de entrenamiento · Ajuste inmediato en código."),
            ("Límite", "Consume ventana de contexto en cada llamada."),
        ],
        accent=BLUE, title_size=20, body_size=14.5
    )
    add_card(
        s, 4.79, 1.75, 3.75, 4.85,
        title="RAG con Embeddings",
        bullets=[
            ("Qué cambia", "El conocimiento disponible dinámicamente desde SQLite o índice local."),
            ("Caso de uso", "Datos que cambian a diario como notas, catálogos o manuales."),
            ("Costo e iteración", "EmbeddingGemma 2 (308M) · Cero re-entrenamiento."),
            ("Ventaja", "Permite citar fuentes exactas y actualizar datos al instante."),
        ],
        accent=TEAL, title_size=20, body_size=14.5
    )
    add_card(
        s, 8.83, 1.75, 3.75, 4.85,
        title="Fine-Tuning (QLoRA)",
        bullets=[
            ("Qué cambia", "El estilo, formato nativo o jerga especializada del modelo."),
            ("Caso de uso", "Cuando un 2B debe responder en un DSL o tono específico sin prompt largo."),
            ("Costo e iteración", "1 GPU (6 GB VRAM) · 500 a 5,000 pares curados."),
            ("Límite", "No debe usarse para inyectar datos que cambian cada hora."),
        ],
        accent=VIOLET, title_size=20, body_size=14.5
    )

    # =========================================================================
    # SLIDE 15: DIAGRAMA RAG LOCAL CON MATRYOSHKA (MRL)
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "RAG con EmbeddingGemma 2 y representación Matryoshka", "Búsqueda semántica en dos etapas con filtro rápido a 128 dimensiones y re-ranking a 768", accent=VIOLET)
    add_fitted_picture(s, ASSETS / "rag-mrl-flow.png", 0.75, 1.55, 11.833, 5.55)

    # =========================================================================
    # SLIDE 16: DIAGRAMA TEORÍA LORA Y QLORA
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Matemática de LoRA y QLoRA entrenando menos del 1% de pesos", "Congelamos Gemma 4 en 4 bits (W₀) e inyectamos dos matrices pequeñas A y B de rango r = 8 o 16", accent=VIOLET)
    add_fitted_picture(s, ASSETS / "lora-qlora.png", 0.75, 1.55, 11.833, 5.55)

    # =========================================================================
    # SLIDE 17: CÓDIGO — ENTRENAMIENTO QLORA CONGELANDO VISIÓN/AUDIO + RAFT
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Ajustando Gemma 4 con QLoRA y RAFT sobre el decoder", "Congelamos las torres de visión y audio y entrenamos con pérdida solo en la respuesta", accent=VIOLET)
    add_code_panel(
        s, 0.75, 1.65, 7.65, 5.2,
        "train_lora_gemma4.py (PEFT + TRL SFTTrainer)",
        [
            "# 1. Congelar visión y audio; aplicar LoRA solo al decoder de texto",
            "lora = LoraConfig(",
            "    r = 16, lora_alpha = 32, lora_dropout = 0.05,",
            "    target_modules = r\"model\\.language_model\\..*(q|k|v|o|gate|up|down)_proj\",",
            ")",
            "",
            "# 2. Glossary Dropout (85% con contexto RAG barajado, 15% sin pista)",
            "prompt = build_raft_prompt(example, gold_share = 0.85, rng = rng)",
            "",
            "# 3. Entrenar midiendo pérdida solo en la respuesta y fusionar",
            "trainer = SFTTrainer(model = model, peft_config = lora,",
            "                     args = SFTConfig(completion_only_loss = True))",
            "trainer.train()",
            "trainer.model.merge_and_unload().save_pretrained(\"gemma4-merged\")",
        ],
        font_size=11.3
    )
    add_card(
        s, 8.65, 1.65, 3.93, 5.2,
        title="Decisiones de entrenamiento",
        bullets=[
            ("Filtro por regex", "Ignora las capas multimodales cuando afinas tareas de texto, ahorrando VRAM."),
            ("RAFT + Dropout 85/15", "El 15% sin contexto obliga a Gemma a no depender a ciegas del bloque RAG."),
            ("Completion Only Loss", "No desperdicia capacidad memorizando las instrucciones del prompt."),
        ],
        accent=VIOLET, title_size=19, body_size=14.2
    )

    # =========================================================================
    # SLIDE 18: SECCIÓN — CASOS DE USO Y ARQUITECTURAS SPLIT-BRAIN (Sin PARTE)
    # =========================================================================
    add_section_slide(
        prs,
        "Arquitecturas Split-Brain en Android y Cloud Run",
        "Combinando Gemma 4, heurísticas deterministas y modelos en la nube en Excusa Legendaria y Cover Letter.",
        accent=AMBER
    )

    # =========================================================================
    # SLIDE 19: TESIS DE PRIVACIDAD (Statement Slide Claro)
    # =========================================================================
    add_statement_slide(
        prs,
        "«Un prompt no es una frontera de seguridad. Un proceso que no tiene los bytes, sí.»",
        "Pedirle a un LLM externo que ignore salarios, nombres o cuentas no evita que esos bytes viajen por la red. La privacidad y la aritmética exigen código determinista y perímetros controlados.",
        "REGLA DE ARQUITECTURA · HEURÍSTICAS EN CÓDIGO + GEMMA EN TU PERÍMETRO + ALLOWLIST HACIA TERCEROS",
        accent=AMBER
    )

    # =========================================================================
    # SLIDE 20: CASO 1 (ANDROID EDGE) — DIAGRAMA FRONTERA SPLIT-BRAIN
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Caso en Android — Frontera Split-Brain en el dispositivo", "En Excusa Legendaria los nombres y lugares nunca salen del teléfono (github.com/ykro/generador-excusas)", accent=AMBER)
    add_fitted_picture(s, ASSETS / "split-brain.es.png", 0.75, 1.55, 11.833, 5.55)

    # =========================================================================
    # SLIDE 21: DIAGRAMA PIPELINE COMPLETO DE EXCUSA LEGENDARIA
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Pipeline híbrido de Excusa Legendaria en Android", "Gemma 4 E2B local anonimiza, Kotlin audita con cero tolerancia y Gemini redacta sin ver PII", accent=AMBER)
    add_fitted_picture(s, ASSETS / "pipeline.es.png", 0.75, 1.55, 11.833, 5.55)

    # =========================================================================
    # SLIDE 22: CÓDIGO — ORQUESTADOR Y LEAK DETECTOR EN KOTLIN (ANDROID)
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Orquestador Split-Brain y detector determinista en Kotlin", "Nunca uses un LLM para auditar si otro LLM filtró datos privados; verifica con código puro", accent=AMBER)
    add_code_panel(
        s, 0.75, 1.65, 7.85, 5.2,
        "ExcusePipeline.kt + LeakDetector.kt",
        [
            "suspend fun run(rawScenario: String, tone: Tone): PipelineResult {",
            "    // 1. Gemma 4 E2B local reemplaza PII por [PERSON_1], [PLACE_1]",
            "    val anon = localGemma.anonymize(rawScenario)",
            "    val map = PlaceholderMap.from(anon.replacements)",
            "",
            "    // 2. Kotlin puro verifica 0 fugas (normalizado sin tildes)",
            "    val leaks = LeakDetector.findLeaks(anon.sanitizedText, map.secrets)",
            "    if (leaks.isNotEmpty()) return PipelineResult.Blocked(leaks)",
            "",
            "    // 3. Nube (online) o Gemma local (offline) redactan con placeholders",
            "    val draft = if (isOnline) cloudGemini.generate(anon.sanitizedText, tone)",
            "                else localGemma.generateDraft(anon.sanitizedText, tone)",
            "",
            "    // 4. Rehidratación O(N) en memoria local del teléfono",
            "    return PipelineResult.Success(Rehydrator.restore(draft, map))",
            "}",
        ],
        font_size=11.5
    )
    add_card(
        s, 8.85, 1.65, 3.73, 5.2,
        title="Garantías en Android",
        bullets=[
            ("Asimetría de datos", "El modelo externo jamás recibe los strings originales del usuario."),
            ("Fail-closed", "Si Gemma olvida un nombre o apellido compuesto, LeakDetector aborta la red."),
            ("Modo avión nativo", "Si no hay conexión, el mismo pipeline conmuta a generación 100% local."),
        ],
        accent=AMBER, title_size=19, body_size=14.5
    )

    # =========================================================================
    # SLIDE 23: CAPTURAS REALES DE LA DEMO EN ANDROID
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Excusa Legendaria ejecutándose en Android", "Izquierda en modo avión 100% local · Derecha comparando el texto sanitizado y el rehidratado", accent=AMBER)
    add_fitted_picture(s, ASSETS / "gemma-local-y-sin-conexion.png", 0.75, 1.60, 5.65, 5.45)
    add_fitted_picture(s, ASSETS / "app-antes-despues.png", 6.93, 1.60, 5.65, 5.45)

    # =========================================================================
    # SLIDE 24: CASO 2 (BACKEND / CLOUD RUN) — COVER LETTER ARQUITECTURA
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Caso en Cloud Run — Cover Letter y niveles de confianza", "Carta de presentación y nota salarial privada con Ollama en Cloud Run (github.com/ykro/coverletter-gemma)", accent=TEAL)
    add_fitted_picture(s, ASSETS / "coverletter-arquitectura.png", 0.75, 1.60, 7.75, 5.45)
    add_card(
        s, 8.70, 1.60, 3.88, 5.45,
        title="Reparto por niveles",
        bullets=[
            ("Nivel 0 · Navegador", "Heurísticas en TypeScript calculan brecha salarial, bandas, tipo de cambio y redactan PII."),
            ("Nivel 1 · Cloud Run Privado", "Gemma 4 E2B en Ollama con GPU L4 protegido por IAM redacta la nota salarial y extrae requisitos JSON."),
            ("Nivel 2 · Tercero (Gemini)", "Recibe solo el payload con allowlist y redactado para escribir la carta; nunca ve el salario."),
        ],
        accent=TEAL, title_size=19, body_size=14.2
    )

    # =========================================================================
    # SLIDE 25: CÓDIGO — DESPLEGANDO GEMMA 4 EN CLOUD RUN CON OLLAMA Y GPU L4
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Desplegando Gemma 4 E2B sobre Cloud Run con Ollama y GPU L4", "Modelos horneados en la imagen Docker para evitar descargas en frío y acceso restringido por IAM", accent=TEAL)
    add_code_panel(
        s, 0.75, 1.65, 7.85, 5.2,
        "coverletter-gemma/ollama/Dockerfile + deploy.sh",
        [
            "# 1. Dockerfile: hornear gemma4:e2b-it-qat dentro de la imagen",
            "FROM ollama/ollama:latest",
            "ENV OLLAMA_HOST=0.0.0.0:8080 OLLAMA_KEEP_ALIVE=-1",
            "ARG MODELS=\"gemma4:e2b-it-qat qwen3.5:2b\"",
            "RUN ollama serve & sleep 5 && \\",
            "    for m in $MODELS; do ollama pull \"$m\" || exit 1; done",
            "ENTRYPOINT [\"ollama\", \"serve\"]",
            "",
            "# 2. deploy.sh: Cloud Run con GPU NVIDIA L4 y escala a cero",
            "gcloud run deploy ollama-coverletter \\",
            "  --image \"$IMAGE\" --region europe-west4 \\",
            "  --gpu 1 --gpu-type nvidia-l4 --no-gpu-zonal-redundancy \\",
            "  --cpu 8 --memory 32Gi --no-cpu-throttling \\",
            "  --min-instances 0 --max-instances 1 --concurrency 4 \\",
            "  --no-allow-unauthenticated",
        ],
        font_size=11.4
    )
    add_card(
        s, 8.85, 1.65, 3.73, 5.2,
        title="Decisiones en Cloud Run",
        bullets=[
            ("Cero descarga en arranque", "Hornear los pesos en el build evita bajar ~4 GB de internet en cada cold start."),
            ("Perímetro IAM", "--no-allow-unauthenticated exige un ID Token de la Service Account de la app (roles/run.invoker)."),
            ("Escala a cero ($0 en reposo)", "Solo pagas por segundo activo de L4; sin cuota de GPU cae limpio a modo CPU."),
        ],
        accent=TEAL, title_size=19, body_size=14.2
    )

    # =========================================================================
    # SLIDE 26: CÓDIGO — ROUTER POR NIVEL Y ALLOWLIST EN TYPESCRIPT (COVER LETTER)
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Router por nivel de confianza y defensa en profundidad", "El cliente no envía prompts libres y el salario actual jamás cruza al modelo de terceros", accent=AMBER)
    add_code_panel(
        s, 0.75, 1.65, 7.85, 5.2,
        "coverletter-gemma/src/lib/router.ts",
        [
            "export type Tier = \"device\" | \"private\" | \"third_party\";",
            "",
            "export const TIER_ALLOWLIST: Record<Tier, ReadonlyArray<keyof Profile>> = {",
            "  device: PROFILE_FIELDS,",
            "  private: PROFILE_FIELDS, // Ollama en Cloud Run propio (IAM)",
            "  third_party: [\"fullName\", \"desiredRole\", \"targetCompany\",",
            "                \"yearsExperience\", \"achievements\"], // Sin salarios",
            "};",
            "",
            "export function buildThirdParty(profile: Profile, extras: Extras = {}) {",
            "  const ctx = redactionContextFor(profile); // Montos en GTQ y USD",
            "  const clean = (s: string) => redact(s, ctx, { currencyWords: true }).text;",
            "  const base = pick(profile, TIER_ALLOWLIST.third_party);",
            "  return LetterPayloadSchema.parse({ // zod .strict() rechaza extras",
            "    ...base, achievements: clean(base.achievements ?? \"\"),",
            "    requirements: (extras.requirements ?? []).map((r) => clean(r)),",
            "  });",
            "}",
        ],
        font_size=11.2
    )
    add_card(
        s, 8.85, 1.65, 3.73, 5.2,
        title="Defensa en profundidad",
        bullets=[
            ("Allowlist explícita", "Un campo nuevo en Profile no viaja a terceros a menos que se agregue y pase las pruebas."),
            ("Doble redacción", "Se redactan montos conocidos ('Q15,000', '15k', '2000') y nombres de empleadores tanto en cliente como en servidor."),
            ("Validación con mutación", "Si apagas el redactor, fallan 13 pruebas automatizadas en leak.test.ts."),
        ],
        accent=AMBER, title_size=19, body_size=14.2
    )

    # =========================================================================
    # SLIDE 27: BENCHMARK Y RETOS REALES EN CLOUD RUN (GEMMA 4 E2B VS QWEN 3.5 2B)
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Benchmark en Cloud Run y lecciones eligiendo Gemma 4 E2B", "Comparación medida en producción sobre GPU L4 y CPU en 12 perfiles (coverletter-gemma/BENCHMARK.md)", accent=VIOLET)
    add_fitted_picture(s, ASSETS / "coverletter-benchmark.png", 0.75, 1.60, 7.45, 5.45)
    add_card(
        s, 8.40, 1.60, 4.18, 5.45,
        title="Hallazgos en producción",
        bullets=[
            ("Velocidad y VRAM en L4", "Gemma 4 E2B (QAT Q4) corre a 117.7 tok/s en 1.80 GB VRAM vs 73.5 tok/s y 2.36 GB de Qwen 3.5 2B."),
            ("Por qué ganó Gemma 4 E2B", "En extracción JSON Qwen coló la pretensión salarial en 9 de 27 corridas; Gemma lo hizo 0 de 27 veces."),
            ("Los números son del código", "La brecha % la calcula TypeScript y checkNumberConsistency subraya cualquier cifra inventada."),
            ("Cuota GPU y Fallback CPU", "Sin cuota en us-central1 se desplegó L4 sin redundancia zonal en europe-west4, con fallback a CPU (18.6 tok/s)."),
        ],
        accent=VIOLET, title_size=18.5, body_size=13.8
    )

    # =========================================================================
    # SLIDE 28: SECCIÓN — AGENTES EN ANDROID CON ADK PARA KOTLIN (Sin PARTE)
    # =========================================================================
    add_section_slide(
        prs,
        "Agentes en Android con ADK para Kotlin",
        "Herramientas tipadas, confirmación humana, Skills bajo demanda y sesiones persistentes sobre Gemma 4 y Gemini.",
        accent=BLUE
    )

    # =========================================================================
    # SLIDE 29: DIAGRAMA ARQUITECTURA ADK PARA KOTLIN
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Arquitectura del Agent Development Kit (ADK) para Kotlin", "Un mismo LlmAgent y Runner en Kotlin pueden operar con Gemma local (LiteRT-LM) o con la nube", accent=BLUE)
    add_fitted_picture(s, ASSETS / "adk-agent-loop.png", 0.75, 1.55, 11.833, 5.55)

    # =========================================================================
    # SLIDE 30: CÓDIGO — DEFINICIÓN DE AGENTE, @TOOL Y CONFIRMACIÓN HUMANA
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Intercambio de modelo con BaseLlm y confirmación humana", "Desacopla el motor de inferencia y exige autorización del usuario en acciones con efectos secundarios", accent=BLUE)
    add_code_panel(
        s, 0.75, 1.65, 7.85, 5.2,
        "AgentFactory.kt + CartTools.kt (ADK for Kotlin)",
        [
            "// 1. Cerebro intercambiable: Gemma 4 en LiteRT-LM o Nube",
            "val localModel: BaseLlm = LiteRtLmModel(appContext, gemmaPath, Backend.GPU)",
            "val cloudModel: BaseLlm = FirebaseAiLogicModel(\"gemini-3-flash\")",
            "",
            "// 2. Herramienta crítica con Human-in-the-Loop (HITL)",
            "val safeCheckout = FunctionTool.create(",
            "    instance = cartTools,",
            "    method = CartTools::checkout,",
            "    requireConfirmation = true // Pausa el Runner y pide permiso en UI",
            ")",
            "",
            "val agent = LlmAgent.builder()",
            "    .name(\"assistant\")",
            "    .model(if (isOffline) localModel else cloudModel)",
            "    .tools(safeCheckout, SkillToolset(AssetsSkillRepository(ctx, \"skills\")))",
            "    .build()",
        ],
        font_size=11.4
    )
    add_card(
        s, 8.85, 1.65, 3.73, 5.2,
        title="Patrones clave en ADK",
        bullets=[
            ("Abstracción BaseLlm", "Tu UI, tus herramientas @Tool y tu base de datos Room no cambian al conmutar entre borde y nube."),
            ("requireConfirmation", "Las lecturas corren directo; pagos o borrados pausan el Runner hasta que el usuario acepta."),
            ("SkillToolset + Room", "Carga manuales bajo demanda para cuidar el contexto del 2B y persiste sesiones en SQLite."),
        ],
        accent=BLUE, title_size=19, body_size=14.2
    )

    # =========================================================================
    # SLIDE 31: PANORAMA DE LAS 3 APPS DE REFERENCIA CON ADK (Un solo slide conciso)
    # =========================================================================
    s = new_slide(prs)
    add_header(s, "Aplicaciones de referencia con ADK para Kotlin", "Casos complementarios en el repositorio para explorar herramientas, persistencia y modo offline", accent=BLUE)
    add_card(
        s, 0.75, 1.75, 3.75, 4.85,
        title="Cart Shop (Comercio)",
        bullets=[
            ("Patrón principal", "FunctionTool (@Tool) + Human-in-the-Loop."),
            ("Qué demuestra", "El agente busca productos y arma el carrito solo, pero exige confirmación humana antes de vaciar o cobrar."),
            ("Foco técnico", "requireConfirmation = true en Compose."),
        ],
        accent=BLUE, title_size=20, body_size=14.5
    )
    add_card(
        s, 4.79, 1.75, 3.75, 4.85,
        title="Recovery Pal (Salud)",
        bullets=[
            ("Patrón principal", "RoomSessionService + inferencia local privada."),
            ("Qué demuestra", "Seguimiento post-operatorio de síntomas y medicación donde ningún dato médico sale del dispositivo."),
            ("Foco técnico", "Estado de sesión sobreviviente al cierre de la app."),
        ],
        accent=TEAL, title_size=20, body_size=14.5
    )
    add_card(
        s, 8.83, 1.75, 3.75, 4.85,
        title="Trail Aid (Supervivencia)",
        bullets=[
            ("Patrón principal", "SkillToolset + 100% Offline con Gemma 4."),
            ("Qué demuestra", "Asistente de primeros auxilios en montaña sin señal celular que carga protocolos médicos desde assets."),
            ("Foco técnico", "Carga perezosa de contexto en modelos pequeños."),
        ],
        accent=AMBER, title_size=20, body_size=14.5
    )

    # =========================================================================
    # SLIDE 32: CIERRE Y LECCIONES APRENDIDAS (Cero clichés "empezar hoy / lunes")
    # =========================================================================
    s = new_slide(prs, BG_LIGHT)
    add_header(s, "Lecciones aprendidas en Android y Cloud Run", "Principios de ingeniería validados con LiteRT-LM, ADK para Kotlin y Ollama sobre GPU L4", accent=BLUE)

    takeaways = [
        ("El código determinista calcula y filtra; el modelo redacta", "Brechas salariales, detección de fugas PII y allowlists por nivel viven en Kotlin o TypeScript probado, nunca en la buena fe del prompt.", BLUE),
        ("Gemma 4 E2B brilla dentro de tu perímetro de confianza", "Ya sea en la NPU del teléfono (.litertlm) o en un contenedor privado de Cloud Run con IAM y GPU L4 (118 tok/s en 1.8 GB VRAM).", TEAL),
        ("Evalúa modelos en las tareas de tu app, no en rankings genéricos", "Medir en tu propio pipeline revela fallos de dominio, sesgos de persona gramatical y riesgos de privacidad antes de salir a producción.", AMBER),
        ("Diseña para degradación elegante y cero pantallas en blanco", "Si la GPU en Cloud Run está en cold start o el teléfono entra en modo avión, las heurísticas y el modelo local mantienen la app funcional.", VIOLET),
    ]
    coords = [(0.75, 1.70), (6.83, 1.70), (0.75, 3.85), (6.83, 3.85)]
    for (t_title, t_body, col), (x, y) in zip(takeaways, coords):
        add_card(s, x, y, 5.75, 1.90, title=t_title, body=t_body, accent=col, title_size=17.5, body_size=14.0)

    add_card(
        s, 0.75, 5.95, 11.833, 1.05,
        title="Adrián Catalán · @adriancs.tech",
        body="Demos y código en github.com/ykro/generador-excusas y github.com/ykro/coverletter-gemma",
        bg=BLUE_BG, accent=BLUE, title_size=19, body_size=14.5
    )

    # =========================================================================
    # INYECTAR NOTAS DEL PRESENTADOR EN CADA SLIDE DE POWERPOINT
    # =========================================================================
    assert len(prs.slides) == len(SPEAKER_NOTES), (
        f"Mismatch between slides ({len(prs.slides)}) and SPEAKER_NOTES ({len(SPEAKER_NOTES)})"
    )
    for slide, note in zip(prs.slides, SPEAKER_NOTES):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        lines = [
            f"[Slide {note['slide']}/32] {note['title']}",
            f"Bloque: {note['block']} | Duración: {note['duration']} ({note['cumulative']})",
            f"Objetivo: {note['objective']}",
            "",
            "QUÉ DECIR:",
        ]
        for paragraph in note["say"]:
            lines.append(f"• {paragraph}")
        lines.append("")
        lines.append("QUÉ SEÑALAR EN PANTALLA:")
        for pt in note["point_out"]:
            lines.append(f"  - {pt}")
        lines.append("")
        lines.append(f"TRANSICIÓN AL SIGUIENTE SLIDE: {note['transition']}")
        tf.text = "\n".join(lines)

    prs.save(str(OUT_PPTX))
    print(f"Saved {OUT_PPTX} with {len(prs.slides)} slides and embedded presenter notes.")


if __name__ == "__main__":
    build_deck()
