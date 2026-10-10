"""Generates high-resolution editorial SVG/PNG diagrams for the Gemma 4 presentation.

Follows the diagram-design editorial system (warm paper #FAF9F5, crisp 1px borders,
semantic color fills, orthogonal connectors, zero pill tags).
"""
import asyncio
from html import escape
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
HTML_DIR = ASSETS / "html"
HTML_DIR.mkdir(parents=True, exist_ok=True)

PAPER = "#FAF9F5"
INK = "#14171F"
MUTED = "#475569"
SOFT = "#64748B"
BLUE = "#1A73E8"
TEAL = "#0D9488"
AMBER = "#D97706"
VIOLET = "#6D28D9"
ROSE = "#E11D48"
RULE = "#CBD5E1"

KINDS = {
    "blue": ("#EFF6FF", BLUE, BLUE),
    "teal": ("#F0FDFA", TEAL, TEAL),
    "amber": ("#FFFBEB", AMBER, AMBER),
    "violet": ("#F5F3FF", VIOLET, VIOLET),
    "rose": ("#FFF1F2", ROSE, ROSE),
    "card": ("#FFFFFF", "#94A3B8", INK),
    "muted": ("#F1F5F9", "#94A3B8", MUTED),
}

DEFS = f"""<defs>
  <marker id="arr-muted" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
  <marker id="arr-blue" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{BLUE}"/></marker>
  <marker id="arr-teal" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{TEAL}"/></marker>
  <marker id="arr-amber" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{AMBER}"/></marker>
  <marker id="arr-violet" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{VIOLET}"/></marker>
</defs>"""


def t(x, y, s, size=13, weight=500, color=INK, family="sans", anchor="middle", spacing=None):
    fam = {
        "sans": "'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif",
        "mono": "'JetBrains Mono', 'SF Mono', monospace",
    }[family]
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" '
        f'font-family="{fam}" text-anchor="{anchor}"{ls}>{escape(s)}</text>'
    )


def box(x, y, w, h, kind, title, sub1=None, sub2=None, rx=8):
    fill, stroke, title_col = KINDS[kind]
    cx = x + w / 2
    lines = [s for s in (sub1, sub2) if s]
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
    ]
    if not lines:
        parts.append(t(cx, y + h / 2 + 5, title, size=14, weight=700, color=INK))
    elif len(lines) == 1:
        parts.append(t(cx, y + h / 2 - 4, title, size=14, weight=700, color=title_col if kind != "card" else INK))
        parts.append(t(cx, y + h / 2 + 16, lines[0], size=11.5, weight=500, color=MUTED, family="mono"))
    else:
        parts.append(t(cx, y + h / 2 - 12, title, size=14, weight=700, color=title_col if kind != "card" else INK))
        parts.append(t(cx, y + h / 2 + 6, lines[0], size=11, weight=500, color=INK))
        parts.append(t(cx, y + h / 2 + 23, lines[1], size=10.5, weight=500, color=MUTED, family="mono"))
    return "\n".join(parts)


def zone(x, y, w, h, title, color=BLUE, fill_rgba="rgba(26,115,232,0.03)", dashed=True):
    dash = ' stroke-dasharray="6,4"' if dashed else ""
    lw = len(title) * 7.2 + 24
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill_rgba}" stroke="{color}" stroke-opacity="0.55" stroke-width="1.3"{dash}/>',
        f'<rect x="{x + 18}" y="{y - 10}" width="{lw}" height="20" rx="4" fill="{PAPER}"/>',
        t(x + 18 + lw / 2, y + 4, title, size=10.5, weight=700, color=color, family="mono", spacing="0.08em"),
    ])


def arrow(d, color="muted", dashed=False, width=1.6):
    col_map = {"muted": MUTED, "blue": BLUE, "teal": TEAL, "amber": AMBER, "violet": VIOLET}
    c = col_map[color]
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{width}"{dash} marker-end="url(#arr-{color})"/>'


def pill_label(cx, cy, text, color=MUTED):
    w = len(text) * 6.5 + 16
    return (
        f'<rect x="{cx - w/2}" y="{cy - 10}" width="{w}" height="18" rx="4" fill="{PAPER}" stroke="{RULE}" stroke-width="0.8"/>'
        + t(cx, cy + 3, text, size=10, weight=600, color=color, family="mono")
    )


def wrap_svg(slug, width, height, body):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: {PAPER}; display: inline-block; }}
  svg {{ display: block; }}
</style>
</head>
<body>
<svg id="{slug}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
{DEFS}
<rect width="100%" height="100%" fill="{PAPER}"/>
{body}
</svg>
</body>
</html>"""


# 1. Gemma 4 Family Map (960 x 520)
def build_gemma_family():
    parts = [
        # Top core trunk
        box(310, 18, 340, 56, "blue", "Arquitectura Base Gemma 4", "Tokenizer 256k · RoPE · Atención Híbrida 5:1"),
        arrow("M 480,74 V 104", "blue"),
        arrow("M 480,88 H 240 V 118", "teal"),
        arrow("M 480,88 H 720 V 118", "amber"),

        # Left zone: Edge / Android
        zone(24, 118, 440, 235, "BORDE / ANDROID (LITE-RT LM)", TEAL, "rgba(13,148,136,0.04)"),
        box(46, 148, 190, 92, "teal", "Gemma 4 E2B", "2B efectivos (5.1B tot)", "~1.1 GB INT4 · 128k ctx"),
        box(252, 148, 190, 92, "teal", "Gemma 4 E4B", "4B efectivos (8.0B tot)", "~1.6 GB INT4 · 128k ctx"),
        box(46, 256, 396, 76, "card", "Innovaciones On-Device: PLE + MatFormer", "Per-Layer Embeddings en Flash · Sub-modelos anidados", "Texto + Imagen + Audio nativo sin servidor"),

        # Right zone: Cloud / Workstation
        zone(496, 118, 440, 235, "SERVIDOR / CLOUD / GPU", AMBER, "rgba(217,119,6,0.04)"),
        box(518, 148, 190, 92, "amber", "Gemma 4 26B A4B", "Arquitectura MoE", "Solo 3.8B activos/token"),
        box(724, 148, 190, 92, "amber", "Gemma 4 31B", "Modelo Denso", "Calidad frontera · 256k ctx"),
        box(518, 256, 396, 76, "card", "Despliegue en Cloud Run / Vertex AI / vLLM", "12B y 26B A4B ideales para inferencia rápida", "Pesos abiertos con licencia Apache 2.0"),

        # Bottom zone: Specialized companions
        zone(24, 382, 912, 120, "MODELOS ESPECIALIZADOS DEL ECOSISTEMA", VIOLET, "rgba(109,40,217,0.03)"),
        box(46, 408, 276, 76, "violet", "EmbeddingGemma 2 (308M)", "Vectores Matryoshka 768 → 128d", "RAG 100% local con sqlite-vec"),
        box(342, 408, 276, 76, "rose", "ShieldGemma 2 (4B)", "Clasificador de seguridad", "Filtra entradas/salidas e imágenes"),
        box(638, 408, 276, 76, "blue", "FunctionGemma / PaliGemma", "Tool Calling JSON & Visión", "Invocación determinista de APIs"),
    ]
    return wrap_svg("gemma-family-map", 960, 520, "\n".join(parts))


# 2. Attention 5:1 + KV Cache + QAT (960 x 500)
def build_attention_kv_qat():
    parts = [
        # Column 1: 5:1 Hybrid Attention
        zone(24, 28, 440, 448, "1. ATENCIÓN HÍBRIDA 5:1 (128K CONTEXTO)", BLUE, "rgba(26,115,232,0.03)"),
    ]
    # 5 local layers + 1 global layer
    y0 = 64
    for i in range(1, 6):
        parts.append(box(52, y0, 384, 42, "teal", f"Capa {i}: Sliding Window Attention (Local)", "Ventana corta (1024 tokens) · Costo O(W) fijo"))
        y0 += 50
    parts.append(box(52, y0, 384, 52, "blue", "Capa 6: Global Full Attention (RoPE)", "Conecta todo el historial (hasta 128k tokens)"))
    parts.append(box(52, 386, 384, 68, "card", "Impacto en KV Cache en Android", "Reduce ~75% la memoria de contexto largo", "Evita que el OS mate la app por OOM"))

    # Column 2: PLE + QAT
    parts += [
        zone(496, 28, 440, 212, "2. PER-LAYER EMBEDDINGS (PLE)", VIOLET, "rgba(109,40,217,0.03)"),
        box(520, 62, 184, 82, "blue", "Backbone Activo", "2B / 4B params", "Reside en GPU / NPU"),
        box(728, 62, 184, 82, "violet", "Tablas PLE", "3B - 4B params", "Streaming desde Flash"),
        arrow("M 728,103 H 704", "violet"),
        box(520, 158, 392, 64, "card", "Calidad de modelo 8B con RAM de 4B", "Desacopla capacidad de conocimiento de la VRAM activa"),

        zone(496, 264, 440, 212, "3. QUANTIZATION-AWARE TRAINING (QAT)", AMBER, "rgba(217,119,6,0.03)"),
        # Memory bars comparison
        f'<rect x="524" y="302" width="380" height="36" rx="6" fill="#FEE2E2" stroke="{ROSE}" stroke-width="1.2"/>',
        t(714, 325, "FP16 (16-bit): ~8.0 GB RAM  — Imposible en gama media", size=12, weight=700, color=ROSE, family="mono"),
        f'<rect x="524" y="352" width="156" height="36" rx="6" fill="#DCFCE7" stroke="{TEAL}" stroke-width="1.5"/>',
        t(602, 375, "INT4 QAT: ~1.6 GB", size=11.5, weight=700, color=TEAL, family="mono"),
        t(802, 375, "5× menos RAM sin perder precisión", size=11.5, weight=600, color=INK),
        box(520, 402, 392, 58, "card", "Entrenado con ruido de cuantización simulado", "Empaquetado directo en .litertlm listo para NPU"),
    ]
    return wrap_svg("attention-kv-qat", 960, 500, "\n".join(parts))


# 3. Training Pipeline (-pt vs -it) (960 x 470)
def build_training_pipeline():
    parts = [
        zone(24, 30, 425, 290, "FASE 1: PRE-ENTRENAMIENTO (MODELO -PT)", BLUE, "rgba(26,115,232,0.03)"),
        box(48, 64, 377, 62, "muted", "Corpus Multilingüe y Multimodal (6T+ Tokens)", "Código, artículos técnicos, imágenes y audio"),
        arrow("M 236,126 V 150", "blue"),
        box(48, 150, 377, 68, "blue", "Objetivo: Next-Token Prediction", "P(w_t | w_1, ..., w_{t-1}) en clústeres TPU"),
        arrow("M 236,218 V 242", "blue"),
        box(48, 242, 377, 60, "card", "Checkpoint Base: gemma-4-e4b-pt", "Completa texto pero NO sigue instrucciones"),

        arrow("M 449,175 H 511", "teal", width=2.2),
        pill_label(480, 158, "Alineación", TEAL),

        zone(511, 30, 425, 290, "FASE 2: POST-ENTRENAMIENTO (MODELO -IT)", TEAL, "rgba(13,148,136,0.03)"),
        box(535, 64, 377, 62, "teal", "Supervised Fine-Tuning (SFT)", "Miles de diálogos multi-turno y llamadas a tools"),
        arrow("M 723,126 V 150", "teal"),
        box(535, 150, 377, 68, "violet", "RLHF / DPO + Destilación On-Policy", "Aprende razonamiento, rechazos seguros y formato JSON"),
        arrow("M 723,218 V 242", "teal"),
        box(535, 242, 377, 60, "card", "Checkpoint Instruct: gemma-4-e4b-it", "El modelo que usamos en Android y Cloud"),

        # Bottom control tokens box
        zone(24, 344, 912, 106, "FORMATO DE TURNOS OBLIGATORIO EN MODELOS INSTRUCT (-IT)", AMBER, "rgba(217,119,6,0.04)", dashed=False),
        f'<rect x="48" y="368" width="864" height="64" rx="6" fill="#181A24" stroke="#334155" stroke-width="1.2"/>',
        t(480, 395, "<start_of_turn>user\\nExtrae entidades JSON de esta nota<end_of_turn>", size=12.5, weight=600, color="#7ACAFF", family="mono"),
        t(480, 418, "<start_of_turn>model\\n{\"persona\": \"Carlos\", \"lugar\": \"Oficina\"}<end_of_turn>", size=12.5, weight=600, color="#A6E28E", family="mono"),
    ]
    return wrap_svg("training-pipeline", 960, 470, "\n".join(parts))


# 4. On-Device RAG with Matryoshka (MRL) (960 x 480)
def build_rag_mrl():
    parts = [
        zone(24, 28, 912, 175, "FASE 1: INDEXACIÓN SEMÁNTICA LOCAL EN ANDROID", BLUE, "rgba(26,115,232,0.03)"),
        box(46, 68, 195, 110, "muted", "Documentos Locales", "PDFs, notas médicas,", "manuales offline"),
        arrow("M 241,123 H 275", "blue"),
        box(275, 68, 210, 110, "card", "Chunking Semántico", "Fragmentos de 250-400", "tokens con solapamiento"),
        arrow("M 485,123 H 519", "blue"),
        box(519, 68, 205, 110, "violet", "EmbeddingGemma 2", "308M params (<200 MB)", "Inferencia < 15 ms"),
        arrow("M 724,123 H 758", "violet"),
        box(758, 68, 156, 110, "teal", "SQLite + sqlite-vec", "Tabla vectorial", "en el teléfono"),

        zone(24, 228, 912, 230, "FASE 2: BÚSQUEDA EN DOS PASOS CON MATRYOSHKA REPRESENTATION LEARNING (MRL)", TEAL, "rgba(13,148,136,0.04)"),
        # Matryoshka visual bar (non-overlapping segmented bar!)
        t(60, 266, "Un solo vector de 768 dimensiones contiene prefijos auto-contenidos de menor dimensión:", size=12.5, weight=600, color=INK, anchor="start"),
        f'<rect x="60" y="280" width="840" height="44" rx="6" fill="#EFF6FF" stroke="{BLUE}" stroke-width="1.4"/>',
        f'<rect x="60" y="280" width="560" height="44" rx="6" fill="#F5F3FF" stroke="{VIOLET}" stroke-width="1.4"/>',
        f'<rect x="60" y="280" width="330" height="44" rx="6" fill="#FFFBEB" stroke="{AMBER}" stroke-width="1.4"/>',
        f'<rect x="60" y="280" width="180" height="44" rx="6" fill="#F0FDFA" stroke="{TEAL}" stroke-width="2"/>',
        t(150, 307, "128 dims (6× más rápido)", size=11, weight=700, color=TEAL, family="mono"),
        t(315, 307, "256 dims", size=11, weight=700, color=AMBER, family="mono"),
        t(505, 307, "512 dims", size=11, weight=700, color=VIOLET, family="mono"),
        t(760, 307, "768 dims (Precisión total)", size=11, weight=700, color=BLUE, family="mono"),

        # Two-pass flow at bottom
        box(60, 346, 250, 92, "teal", "Paso 1: Filtro Ultrarrápido", "Compara solo las primeras 128 dims", "Descarta el 99% de chunks en <2 ms"),
        arrow("M 310,392 H 355", "teal"),
        box(355, 346, 250, 92, "violet", "Paso 2: Re-ranking Exacto", "Evalúa las 768 dims completas", "Solo sobre el Top-20 candidato"),
        arrow("M 605,392 H 650", "blue"),
        box(650, 346, 250, 92, "blue", "Paso 3: Generación Local", "Inyecta el Top-3 en Gemma 4 E4B", "Respuesta con citas sin usar red"),
    ]
    return wrap_svg("rag-mrl-flow", 960, 480, "\n".join(parts))


# 5. LoRA / QLoRA Architecture (960 x 470)
def build_lora_qlora():
    parts = [
        zone(24, 24, 560, 422, "ARQUITECTURA QLoRA: PESOS CONGELADOS + ADAPTADOR DE BAJO RANGO", VIOLET, "rgba(109,40,217,0.03)"),

        # Bottom input x
        box(180, 368, 250, 56, "muted", "Activación de Entrada x", "Dimensión d = 3072"),

        # Left branch: Frozen W0
        arrow("M 240,368 V 300", "blue"),
        box(52, 150, 236, 150, "blue", "Pesos Base W₀ (Congelados)", "Gemma 4 cuantizado a 4-bit", "d × k (3072 × 3072) · 0% entrenable"),
        arrow("M 170,150 V 96 H 265", "blue"),

        # Right branch: LoRA A and B
        arrow("M 370,368 V 315 H 436 V 295", "violet"),
        box(316, 225, 240, 70, "violet", "Matriz LoRA A (d × r)", "Proyección a rango r = 8 o 16"),
        arrow("M 436,225 V 195", "violet"),
        box(316, 125, 240, 70, "violet", "Matriz LoRA B (r × k)", "Escala α/r · < 1% de parámetros"),
        arrow("M 436,125 V 96 H 345", "violet"),

        # Sum node at top
        f'<circle cx="305" cy="96" r="24" fill="#FFFBEB" stroke="{AMBER}" stroke-width="2"/>',
        t(305, 102, "⊕", size=22, weight=700, color=AMBER),
        t(305, 54, "Salida h = W₀·x + (B·A)·x", size=14, weight=700, color=INK, family="mono"),

        # Right panel: Practical benefits & deployment
        zone(608, 24, 328, 422, "VENTAJAS EN PRODUCCIÓN", TEAL, "rgba(13,148,136,0.03)"),
        box(630, 62, 284, 104, "teal", "Entrenamiento en 1 GPU", "De ~96 GB VRAM (Full FT)", "a ~6 GB VRAM con QLoRA (Unsloth)"),
        box(630, 186, 284, 104, "amber", "Adaptadores Intercambiables", "Un solo Gemma 4 E4B en el teléfono", "+ múltiples LoRAs de 15-30 MB"),
        box(630, 310, 284, 110, "card", "Fusión Cero-Latencia", "Al exportar a .litertlm puedes", "fusionar W = W₀ + B·A sin costo extra"),
    ]
    return wrap_svg("lora-qlora", 960, 470, "\n".join(parts))


# 6. ADK for Kotlin Agent Loop (960 x 490)
def build_adk_agent_loop():
    parts = [
        zone(24, 24, 912, 442, "AGENT DEVELOPMENT KIT (ADK) PARA KOTLIN — ARQUITECTURA EN ANDROID", BLUE, "rgba(26,115,232,0.03)"),

        # Left: UI + Runner + Session
        box(48, 68, 215, 86, "card", "UI Jetpack Compose", "Eventos de usuario y", "diálogos de confirmación"),
        arrow("M 263,111 H 325", "blue"),
        box(48, 195, 215, 105, "teal", "RoomSessionService", "Persistencia SQLite local", "Sobrevive reinicios del OS"),
        arrow("M 263,247 H 325", "teal"),
        box(48, 336, 215, 98, "violet", "SkillToolset (On-Demand)", "Carga instrucciones y", "referencias bajo demanda"),
        arrow("M 263,385 H 370 V 300", "violet"),

        # Center: Runner + LlmAgent
        box(325, 68, 260, 232, "blue", "Runner + LlmAgent", "Ciclo de Eventos tipado en Kotlin", "Orquesta turnos, estado y llamadas"),

        # Right top: Models (Split-Brain)
        arrow("M 585,120 H 655", "teal"),
        pill_label(620, 104, "BaseLlm", TEAL),
        box(655, 64, 255, 104, "teal", "LiteRtLmModel (Local)", "Gemma 4 E2B / E4B en NPU", "Privacidad total · 0 ms red"),

        arrow("M 585,205 H 655", "amber", dashed=True),
        box(655, 184, 255, 96, "amber", "FirebaseAiLogic (Cloud)", "Gemini Cloud / Gemma 26B", "Razonamiento complejo opcional"),

        # Right bottom: Tools + HITL
        arrow("M 585,265 H 620 V 365 H 655", "violet"),
        box(655, 304, 255, 130, "rose", "FunctionTool (@Tool)", "Funciones Kotlin con reflexión", "requireConfirmation = true (HITL)"),
    ]
    return wrap_svg("adk-agent-loop", 960, 490, "\n".join(parts))


# 7. Split-Brain Privacy Boundary (960 x 480)
def build_split_brain():
    parts = [
        zone(24, 28, 630, 424, "EL TELÉFONO · DATOS PRIVADOS (NUNCA SALEN DEL DISPOSITIVO)", TEAL, "rgba(13,148,136,0.04)"),
        zone(686, 28, 250, 424, "LA NUBE (CIEGA A PII)", AMBER, "rgba(217,119,6,0.04)"),

        box(48, 76, 175, 96, "muted", "Historia Real", "Nombres, lugares y", "detalles privados"),
        arrow("M 223,124 H 260", "teal"),
        box(260, 76, 185, 96, "teal", "Gemma 4 E2B Local", "Detecta PII y reemplaza", "por [PERSON_1], [PLACE_1]"),
        arrow("M 445,124 H 482", "blue"),
        box(482, 76, 150, 96, "blue", "LeakDetector", "Kotlin determinista", "Verifica 0 fugas"),

        # Arrow crossing boundary to Cloud
        arrow("M 632,124 H 712", "amber", width=2.0),
        pill_label(672, 102, "Sin PII", AMBER),
        box(712, 76, 198, 96, "amber", "Gemini en la Nube", "Escribe excusa épica", "sin conocer identidades"),

        # Local placeholder map stored in RAM
        arrow("M 352,172 V 212", "violet"),
        box(260, 212, 185, 86, "violet", "Mapa en Memoria RAM", "[PERSON_1] → Laura", "[PLACE_1] → Oficinas Norte"),
        arrow("M 352,298 V 336", "violet"),

        # Return path from Cloud to Local Rehydrator
        arrow("M 811,172 V 382 H 445", "amber", dashed=True, width=1.8),
        pill_label(610, 364, "Borrador con [PERSON_1]", AMBER),

        box(260, 336, 185, 92, "blue", "Rehidratador Local", "Restaura nombres reales", "en Kotlin (0 ms)"),
        arrow("M 260,382 H 223", "teal"),
        box(48, 336, 175, 92, "teal", "Resultado Final", "Historia completa", "lista para el usuario"),
    ]
    return wrap_svg("split-brain.es", 960, 480, "\n".join(parts))


# 8. Excusa Legendaria 8-Step Pipeline (960 x 490)
def build_pipeline():
    parts = [
        zone(24, 24, 912, 442, "PIPELINE HÍBRIDO DE 8 PASOS — EXCUSA LEGENDARIA", BLUE, "rgba(26,115,232,0.03)"),

        # Top row: Steps 1 to 4 + Cloud Step 6b
        box(46, 68, 175, 92, "teal", "1. Anonimizar (Gemma)", "Extrae PII local →", "[PERSON_1], [PLACE_1]"),
        arrow("M 221,114 H 254", "blue"),
        box(254, 68, 175, 92, "blue", "2. LeakDetector", "Código Kotlin puro", "Bloquea si queda PII"),
        arrow("M 429,114 H 462", "teal"),
        box(462, 68, 180, 92, "teal", "3-5. Analizar (Gemma)", "Resumen seguro,", "gravedad y tono"),
        arrow("M 642,114 H 712", "amber"),
        pill_label(677, 94, "Online", AMBER),
        box(712, 68, 200, 92, "amber", "6b. Gemini en Nube", "Redacta excusa creativa", "vía Firebase AI Logic"),

        # Middle row: Offline / Fallback branch 6a & Reviewer 7
        arrow("M 552,160 V 218", "teal"),
        pill_label(552, 189, "Offline / Fallback", TEAL),
        box(462, 218, 180, 92, "teal", "6a. Gemma Escribe", "Generación 100% local", "en modo avión (0 red)"),

        arrow("M 812,160 V 218", "amber"),
        box(712, 218, 200, 92, "violet", "7. Gemma Audita", "Verifica coherencia", "y ausencia de fugas"),

        # Bottom row: Step 8 Rehydrate -> Final Output
        arrow("M 552,310 V 352", "blue"),
        arrow("M 812,310 V 396 H 642", "violet"),
        box(462, 352, 180, 90, "blue", "8. Rehidratar (Kotlin)", "Reemplaza placeholders", "por nombres originales"),
        arrow("M 462,397 H 380", "teal"),
        box(140, 352, 240, 90, "card", "Excusa Épica Lista en UI", "Privacidad garantizada por diseño", "Funciona con o sin internet"),
    ]
    return wrap_svg("pipeline.es", 960, 490, "\n".join(parts))


DIAGRAMS = {
    "gemma-family-map": build_gemma_family,
    "attention-kv-qat": build_attention_kv_qat,
    "training-pipeline": build_training_pipeline,
    "rag-mrl-flow": build_rag_mrl,
    "lora-qlora": build_lora_qlora,
    "adk-agent-loop": build_adk_agent_loop,
    "split-brain.es": build_split_brain,
    "pipeline.es": build_pipeline,
}


async def main():
    for slug, fn in DIAGRAMS.items():
        html_path = HTML_DIR / f"{slug}.html"
        html_path.write_text(fn(), encoding="utf-8")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome")
        page = await browser.new_page(viewport={"width": 1200, "height": 800}, device_scale_factor=2.5)
        for slug in DIAGRAMS:
            html_path = HTML_DIR / f"{slug}.html"
            out_png = ASSETS / f"{slug}.png"
            await page.goto(html_path.resolve().as_uri())
            await page.evaluate("document.fonts.ready")
            await page.wait_for_timeout(250)
            await page.locator("svg").first.screenshot(path=str(out_png))
            print(f"Exported {out_png.name}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
