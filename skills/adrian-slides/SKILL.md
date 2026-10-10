---
name: adrian-slides
description: Diseña, estructura y genera presentaciones técnicas (.pptx con python-pptx y guías de orador en Markdown) con el estilo editorial, visual y de código de Adrián Catalán (@adriancs.tech). Úsalo siempre que el usuario pida crear, actualizar o revisar slides, charlas técnicas, clases universitarias, talleres o presentaciones.
---

# Estilo de Presentaciones Técnicas — Adrián Catalán (`@adriancs.tech`)

Este skill define las reglas de identidad, narrativa pedagógica, juicio técnico en la era de la IA, diseño editorial claro (`13.333" × 7.5"`), tipografía apta para proyector, límites estrictos de densidad, diagramas vectoriales con `diagram-design`, bloques de código con resaltado de sintaxis y verificación visual + matemática obligatoria para construir presentaciones técnicas de Adrián Catalán.

> **Implementaciones de referencia verificadas:**
> * `/Users/ykro/code/charlas/2027/slides-agy/build_charla1.py`
> * `/Users/ykro/code/charlas/2027/gemma/scripts/build_deck.py` y `/Users/ykro/code/charlas/2027/gemma/scripts/generate_diagrams.py`
> * `/Users/ykro/code/cursos/awa-2027/scripts/generate_unit1_pptx.py`

---

## 1. Identidad, Idioma y Tono del Ponente

* **Nombre y contacto en portada / cierre:** `Adrian Catalan` · `adriancatalan@gmail.com` o `@adriancs.tech` *(NUNCA usar `@ykro1` en portadas ni cierres)*.
* **Idioma y Spanglish Técnico Natural (LatAm):**
  * Español técnico fluido usando los términos en inglés que todo ingeniero usa en la práctica sin traducciones forzadas: **Prompt**, **Tokens**, **Embeddings**, **Fine-Tuning**, **LoRA**, **QLoRA**, **RAG**, **KV Cache**, **Tool Calling**, **Guardrail**, **On-Device**, **Cloud**, **Offline**, **Endpoint**, **Payload**, **Schema**, **Event Loop**, **Thread Pool**, **Settlement**, **Greedy**, **Middleware**, **Status Code**, **DTO**, **Idempotency**.
* **Tono de Ingeniería:**
  * Directo, empírico, basado en arquitectura, invariantes, números medidos y trade-offs concretos.
  * Explica el **por qué** antes del **cómo** y respalda cada decisión con evidencia, diagramas o código verificable.

---

## 2. Reglas Editoriales Estrictas (Cero Tags, Cero Clichés de IA, Cero `:`, Cero Solapamientos, 100% Modo Claro)

1. **100% Modo Claro para todas las diapositivas + Bloques de Código con Syntax Highlighting:**
   * **Todas las diapositivas** (portada, contenido, diagramas, duelos, código y cierre) usan **exclusivamente fondo claro editorial** (`#F8F7F4` o `#FAF9F5` papel cálido) y tarjetas blancas (`#FFFFFF`) con bordes sutiles (`#DFDDD4`). **PROHIBIDO** usar fondos negros u oscuros para una diapositiva completa (ni siquiera en portadas o divisores).
   * **Bloques de código IDE:**
     * **Por defecto:** El fondo oscuro (`#181A24` con barra superior `#232736`, tres puntos estilo macOS y nombre del archivo) se reserva **única y exclusivamente para los contenedores de código**, usando **coloreado de sintaxis token por token** (*syntax highlighting*) y números de línea.
     * **Variante alternativa (solo cuando el usuario pida explícitamente 0% superficies oscuras incluso en código):** Superficie IDE clara (`#F6F8FA` con barra `#EAEEF2`) igualmente con coloreado de sintaxis token por token y números de línea.
2. **PROHIBICIÓN ABSOLUTA de "Tags", "Pills", "Badges" o "Kickers" en TODA la presentación:**
   * **En la Portada (`Slide 1`):** Prohibido poner píldoras, etiquetas o tags (`GEMMA 4`, `APACHE 2.0`, `CURSO 1`, `SEMANA 1`). La portada lleva únicamente título, subtítulo descriptivo y `@adriancs.tech` / `adriancatalan@gmail.com`.
   * **En los Slides Interiores y Tarjetas:** Prohibido poner tags/badges encima de los títulos de diapositiva (`TEORÍA`, `ARQUITECTURA`, `PARTE 1`) y **prohibido poner píldoras/badges dentro de tarjetas, cuadrantes (`quadrants`), flujos (`flow`) o columnas comparativas (`three_column_comparison`)**. Las tarjetas llevan directamente su franja de acento y su título (`18–20 pt Bold`) seguido de su descripción concisa (`2–3 líneas`), como en el patrón limpio de *"Modelos especializados"*.
3. **Cero Subtítulos en Slides de Contenido y Cero Numeración de Bloques:**
   * Las diapositivas de contenido llevan **únicamente un título de 1 línea (`27 pt Bold`, `≤ 58 caracteres`)** con barra de acento vertical (`add_header`). **Prohibido** poner subtítulos debajo del título o kickers/tags encima del título (`BLOQUE 1 DE 5`, `PARTE 2`).
   * **Prohibido** insertar slides separadores numerados tipo *"BLOQUE 1 DE 5"* ni numeración de página (`1/50`).
4. **Un solo Demo en Vivo a Profundidad + Resumen Conciso del Resto:**
   * Cuando un repositorio o charla incluya múltiples demos o aplicaciones de ejemplo, **elige 1 único demo principal** para desglosar su arquitectura, flujo y código paso a paso.
   * Las demás aplicaciones o demos secundarios deben mencionarse en **un único slide comparativo de resumen**, jamás detallando cada uno con múltiples slides que diluyen el foco de la charla.
5. **Cero Slides de Relleno o Capturas de Terminal sin Valor Pedagógico:**
   * **Prohibidos** los slides cuyo único propósito sea mostrar capturas de terminal con pruebas unitarias pasando (p. ej. *"32 pruebas unitarias pasando sin errores"*) o métricas de vanidad que no enseñan un mecanismo técnico, una invariante de arquitectura o un patrón de código reproducible.
   * Prioriza siempre **slides de teoría profunda** (arquitectura interna, matemática intuitiva, trade-offs de memoria/latencia) acompañados de **snippets de código clave**.
6. **Cero Dos Puntos (`:`) en Prosa, Títulos, Encabezados, Tarjetas y Viñetas:**
   * El uso de `:` en títulos o bullets (`"Pydantic v2: Validación rápida"`, `"Problema: Flotantes"`) es un patrón típico de texto generado por IA.
   * **Regla:** **Cero `:` fuera de los bloques de código.** Usa frases directas o encabezados separados del cuerpo.
7. **Palabras y Frases Prohibidas (Veto Total de Clichés de LLM):**
   * **Palabras prohibidas en cualquier slide:** `real`, `reales`, `honesto`, `honesta`, `honestos`, `honestas`.
     * *Sustitutos:* en lugar de *"caso real"* usa *"caso en producción"* o *"escenario operativo"*; en lugar de *"comparación honesta"* usa *"comparación directa"* o *"evaluación medida"*; en lugar de *"tiempo real"* usa *"baja latencia"* o *"en vivo"*.
   * **Estructuras cliché prohibidas:** *"cola larga"*, *"los tres pilares"*, *"los cuatro pilares"*, *"en tres pasos"*, *"en cuatro pasos"*, *"no es X, es Y"*, *"X cosas/ideas para empezar hoy"*, *"para llevarte hoy"*, *"para empezar el lunes"*. En slides de cierre usa encabezados sobrios de ingeniería como *"Lecciones aprendidas en arquitectura e implementación"*.
8. **Límite Estricto de Densidad (`≤ 55 palabras` por diapositiva) y Prevención de Textos Montados:**
   * Ninguna diapositiva puede superar **55 palabras** en pantalla (excluyendo el bloque de código en fuente monoespaciada). El promedio ideal del deck es **28–42 palabras por slide**.
   * Todo el discurso oral detallado va en las **Speaker Notes (`slide.notes_slide`)** y en el archivo Markdown de guía del orador.
   * En tablas (`clean_table`), cada celda debe tener **`≤ 5 palabras`** (`2–4 palabras` ideal).
   * En bloques de código, máximo **`15–16 líneas`** y **`≤ 58 caracteres` por línea** para que jamás hagan wrap ni desborden la caja oscura/clara.
   * En ecuaciones visuales (`visual_equation`), el encabezado de cada bloque (`part["head"]`) debe tener **`≤ 15 caracteres`** (o escalar automáticamente a `20 pt`) para que ninguna expresión matemática o numérica se parta a mitad de línea.
   * **Regla anti-solapamiento en `python-pptx`:** Nunca coloques un título y un párrafo descriptivo en dos `textbox` independientes con coordenadas `y` cercanas. Usa **un único `text_frame`** con párrafos sucesivos (`tf.add_paragraph()`) y `space_after`, de modo que si una línea hace *wrap*, empuje limpiamente al párrafo siguiente en lugar de montarse sobre él.

---

## 3. Modo Clase Universitaria y Juicio Técnico para Guiar a la IA

Cuando las diapositivas sean para un **curso universitario o taller de ingeniería de software**, aplica estas reglas pedagógicas adicionales:

1. **Teoría Progresiva desde Cero antes de Diagnosticar Código:**
   * Nunca abras la clase con un diagnóstico de código en frío (*Bug Hunt*) si aún no has explicado los fundamentos teóricos.
   * **Orden pedagógico obligatorio:**
     1. **Contexto y Problema de Ingeniería:** Qué sistema construimos hoy, cómo luce funcionando (screenshots verificados de la app desplegada) y cómo encaja en el curso.
     2. **Fundamentos Teóricos desde Cero:** Explicar los conceptos base (por ejemplo, anatomía de HTTP, métodos, status codes, idempotencia, memoria, concurrencia, contratos de datos, arquitectura en capas, complejidad algorítmica) usando la aplicación demo como hilo conductor concreto.
     3. **Juicio Técnico Humano vs. IA sin Guía (`versus_duel`):** En cada decisión crítica (backend, frontend o mobile), contrastar qué genera una IA por defecto cuando recibe un prompt ambiguo (*código naive*: `float` para dinero, `dict` sin validación, endpoints que mezclan HTTP y negocio, tests que solo prueban `200 OK`) frente a qué exige un **ingeniero con juicio técnico** (`Decimal`/`int` centavos, DTOs estrictos en Pydantic v2, estado aislado inyectado, algoritmos $O(N \log N)$ e invariantes matemáticos).
     4. **Verificación Activa (Bug Hunt al Cierre de la Teoría):** Una vez explicadas las bases, presentar retos cortos de auditoría de código (*"¿Qué falla aquí en producción si aceptas este PR generado por IA?"*) seguidos de su solución explicada.
     5. **Cierre y Práctica:** Lecciones aprendidas de arquitectura, resumen de 4 puntos clave y conexión con el Codelab guiado + Reto autónomo.
2. **Títulos Basados en Conceptos de Ingeniería, No en Burocracia de Archivos:**
   * Prohibido titular una lámina con nombres de archivos administrativos como *"Documentación en ARCHITECTURE_DECISIONS.md"*. Titula siempre con la decisión o principio técnico: *"Por qué documentamos trade-offs e invariantes de arquitectura"*.
3. **Fuente Única de Verdad (`Single-Source Sync` entre `.pptx`, `slides.md` y Hub HTML):**
   * El diccionario `SLIDES` del script generador en Python debe exportar en la misma corrida tanto el archivo `.pptx` como la guía docente `slides.md` (y alimentar el Hub HTML de la unidad si existe), garantizando cero desfase entre las láminas y las notas del profesor.

---

## 4. Sistema Visual, Tipografía y Dimensiones (`13.333" × 7.5"`)

### Dimensiones del Lienzo (Widescreen 16:9)
```python
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
```

### Paleta 100% Modo Claro + Código con Syntax Highlighting
```python
BG = RGBColor(0xF8, 0xF7, 0xF4)          # Lienzo editorial cálido (#FAF9F5 / #F8F7F4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)       # Superficie de tarjetas
SUBTLE_BG = RGBColor(0xF1, 0xF0, 0xEC)   # Superficie neutra suave
LINE = RGBColor(0xDF, 0xDD, 0xD4)        # Borde limpio

# Contenedor de código (Único elemento con fondo oscuro permitido por defecto)
CODE_BG = RGBColor(0x18, 0x1A, 0x24)     # Superficie IDE oscura (o #F6F8FA si se exige 0% oscuro)
CODE_HEADER = RGBColor(0x23, 0x27, 0x36) # Barra superior IDE oscura (o #EAEEF2 en variante clara)
SYN_KW = RGBColor(0xFF, 0x7B, 0x72)      # Keywords (def, fun, val, class, import)
SYN_STR = RGBColor(0xA5, 0xD6, 0xFF)     # Strings
SYN_COM = RGBColor(0x8B, 0x94, 0x9E)     # Comentarios
SYN_NUM = RGBColor(0xD2, 0xA8, 0xFF)     # Números, constantes y anotaciones (@Tool)
SYN_TYPE = RGBColor(0x79, 0xC0, 0xFF)    # Tipos y clases
SYN_FUNC = RGBColor(0xFF, 0xA6, 0x57)    # Llamadas a funciones / tokens especiales

INK = RGBColor(0x18, 0x18, 0x1B)         # Títulos (Carbón profundo)
BODY = RGBColor(0x3F, 0x3F, 0x46)        # Cuerpo de texto
MUTED = RGBColor(0x71, 0x71, 0x7A)       # Captions y números de línea

GREEN = RGBColor(0x0F, 0x76, 0x6E)       # Éxito / Juicio Técnico / Local On-Device
GREEN_BG = RGBColor(0xEC, 0xFD, 0xF5)
BLUE = RGBColor(0x1D, 0x4E, 0xD8)        # Arquitectura / HTTP / Contratos
BLUE_BG = RGBColor(0xEF, 0xF6, 0xFF)
PURPLE = RGBColor(0x6D, 0x28, 0xD9)      # Algoritmos / LoRA / Internals
PURPLE_BG = RGBColor(0xF5, 0xF3, 0xFF)
CORAL = RGBColor(0xC2, 0x41, 0x0C)       # Cuellos de botella / Trade-offs
CORAL_BG = RGBColor(0xFF, 0xF7, 0xED)
RED = RGBColor(0xB9, 0x1C, 0x1C)         # Bugs / IA sin guía / Errores HTTP
RED_BG = RGBColor(0xFE, 0xF2, 0xF2)
AMBER = RGBColor(0xB4, 0x53, 0x09)       # Cloud / Advertencias / Casos borde
AMBER_BG = RGBColor(0xFF, 0xFB, 0xEB)
```

### Escala Tipográfica (`Helvetica Neue` / `Arial` + `Menlo` / `Courier New`)
* **Título de Portada:** `46 pt Bold` (`#18181B`)
* **Título de Diapositiva (`add_header`):** `27 pt Bold` (`#18181B`), 1 sola línea en `Inches(0.88), Inches(0.38)`
* **Tesis Principal (`big_statement`):** `28 pt Bold` + subtesis `18 pt Regular`
* **Número / Estadística Ancla en Tarjeta:** `21–28 pt Bold` en color de acento
* **Encabezado de Tarjeta / Nodo:** `18–20 pt Bold`
* **Cuerpo de Tarjeta / Viñetas:** `15–16 pt Regular` *(nunca menor a `13.5 pt`)*
* **Celdas de Tabla (`clean_table`):** `14.5 pt` (`15 pt Bold` en encabezados)
* **Código en IDE (`add_code_panel`):** `11.8–12.5 pt Menlo` con coloreado de sintaxis y números de línea `11.5 pt`

---

## 5. Catálogo de Layouts Estructurales, Capturas de UI y Diagramas con `diagram-design`

Usa y combina estos 8 layouts verificados para mantener ritmo visual sin monotonía (recuerda: **sin tags/badges** en ningún layout):

1. **`light_cover`**: Portada minimalista sobre fondo `#F8F7F4` con marco blanco, barra vertical de acento, título `46 pt`, subtítulo `20 pt` y autor `@adriancs.tech` (`≤ 15 palabras`, **cero tags**).
2. **`big_statement`**: Caja central de tesis (`28 pt Bold`) + 3 bloques inferiores con métrica grande (`28 pt Bold`) y descripción corta (`15.5 pt Bold`). Ideal para abrir un concepto fundamental o resumir una regla de oro.
3. **`minimal_cards`**: 2, 3 o 6 tarjetas blancas (ej. cuadrícula `2×3` de *"Modelos especializados"*) con franja superior o lateral de color (`0.08"`), título directo (`18–19 pt Bold`) y descripción concisa de 2–3 líneas (`15 pt`), **sin badges ni tags**.
4. **`visual_diagram`**: Diagramas nativos vectoriales con coordenadas matemáticas exactas:
   * `quadrants`: Cuadrícula `2×2` de tarjetas con franja lateral de color, título (`20 pt`) y descripción (`15.5 pt`) (**sin etiqueta `tag` ni píldora superior**).
   * `flow`: Flujo horizontal de 3 o 4 etapas conectadas por flechas con franja superior de color, título directo y descripción (**sin badge `tag` superior**) + barra de conclusión inferior (`bottom_note`).
   * `three_column_comparison`: 3 columnas comparativas con título directo (**sin badge superior**), bloque central destacado y pie técnico.
   * `layered_stack`: Pila vertical de capas a la izquierda (`x=0.65, w=7.20`) + 2 tarjetas de impacto a la derecha (`x=8.15, w=4.53`).
   * `visual_equation`: Ecuación visual de 3 bloques (`A + B = C`) con encabezados cortos (`≤ 15 caracteres`) + barra inferior explicativa.
   * `horizontal_bars`: Gráfico de barras horizontales comparativas con etiqueta, barra proporcional y valor a la derecha.
5. **`clean_table`**: Tabla limpia y espaciosa (`14.5 pt`, `≤ 5 palabras` por celda) con fila destacada opcional (`highlight: True`).
6. **`versus_duel`**: Duelo lado a lado con banner superior de escenario, tarjeta izquierda en verde (**Ingeniero con Juicio Técnico** / diseño robusto) vs tarjeta derecha en rojo/coral (**IA sin Guía / Código Naive**), y barra inferior con la regla de ingeniería (`takeaway`).
7. **`code_showcase` / `light_code`**: Ventana IDE a la izquierda (`x=0.65, y=1.35, w=7.35, h=5.50`) con barra superior, tres puntos macOS, nombre del archivo en `Menlo 13 pt`, código coloreado token por token con números de línea + 2 o 3 tarjetas de análisis técnico a la derecha (`x=8.28, w=4.40`).
8. **`full_diagram_img`**: Tarjetas de análisis concisas a la izquierda + captura de UI en vivo o diagrama vectorial de alta resolución a la derecha, insertado con `add_fitted_image` preservando el aspect ratio exacto mediante `PIL.Image.size`.

### Reglas para Capturas de UI en Vivo (`Playwright` @2x Retina)
Cuando la presentación incluya capturas de una aplicación funcionando en vivo (como demos de cursos o charlas):
* **Diseño de la UI antes de capturar:** La interfaz de demo debe estar en **100% Modo Claro**, sin emojis y organizada en **pestañas o pantallas simples** (evitando consolas saturadas con múltiples paneles simultáneos que distraen en el proyector).
* **Resolución Retina:** Captura siempre con Playwright (`viewport={"width": 1360, "height": 840}`, `device_scale_factor=2`) mostrando al menos: (1) la vista principal de uso, (2) el resultado del algoritmo o flujo principal, (3) el manejo de un error de validación en vivo (`HTTP 422` / `404`), y (4) el contrato interactivo (`/docs` OpenAPI si es un backend).

### Reglas para Diagramas con `diagram-design` (`scripts/generate_diagrams.py`)
Nunca dibujes diagramas de arquitectura complejos a punta de cajas básicas de PowerPoint. Usa el sistema SVG editorial del skill **`diagram-design`**:
* **Lienzo y Fondo:** Fondo `#FAF9F5` con grilla de puntos sutil (`radial-gradient` o `<pattern>`) y contenedores de zona con borde punteado (`stroke-dasharray="6 4"`) para delimitar fronteras (ej. *El Teléfono vs. La Nube*, *Pesos Congelados vs. Matrices LoRA*).
* **Jerarquía de Color Semántica:**
  * **Verde Esmeralda (`#0D9488` / `#F0FDFA`):** Ejecución local en dispositivo (*On-Device*, NPU, Gemma 4 Local, privacidad).
  * **Azul Google (`#1A73E8` / `#EFF6FF`):** Código determinista Kotlin/Python, orquestación ADK, validación.
  * **Ámbar (`#D97706` / `#FFFBEB`):** Ejecución en la Nube (*Gemini Cloud*, llamadas remotas).
  * **Violeta (`#7C3AED` / `#F5F3FF`):** Memoria, vectores/embeddings, matrices de pesos (`LoRA`, `Room`, `KV Cache`).
* **Conectores y Etiquetas:** Usa rutas SVG ortogonales (`<path d="M ... H ... V ..."/>`) con puntas de flecha (`marker-end`) y verifica que las etiquetas sobre flechas (`pill_label`) tengan al menos `6–10 px` de margen respecto a los bordes de las cajas vecinas.
* **Exportación:** Renderiza con Playwright (`device_scale_factor=2.5`) y verifica cada PNG con `view_file` antes de incrustarlo en el `.pptx`.

---

## 6. Quality Gate Automatizado + Verificación Visual Obligatoria

Antes de entregar cualquier presentación, el script generador **debe ejecutar y pasar sin errores** tres validaciones:

### Paso 1 — Quality Gate Léxico y de Densidad (en Python al construir el deck)
* `count_slide_words(spec) <= 55` en todas las diapositivas (y `<= 15` en la portada).
* **Cero tags/badges/pills** en portada, encabezados, cuadrantes (`quadrants`), flujos (`flow`) o columnas comparativas (`three_column_comparison`).
* Cero dos puntos (`:`) en cualquier campo de texto fuera del código.
* Cero palabras prohibidas (`real`, `reales`, `honesto`, `honesta`, `honestos`, `honestas`, `@ykro1`, `chinchilla`) y cero frases cliché (`cola larga`, `tres pilares`, `cuatro pilares`, `tres pasos`, `cuatro pasos`).
* Cero celdas de tabla con más de 5 palabras.
* Cero encabezados de ecuación (`visual_equation`) con más de 15 caracteres sin ajuste de fuente.
* Cero líneas de código con más de 58 caracteres o bloques con más de 16 líneas.

### Paso 2 — Auditoría Matemática de Bounding Boxes y Fondo Claro (sobre el `.pptx` generado)
* Verificar que todas las diapositivas tengan fondo claro (`rgb > 230`), que el fondo oscuro `#181A24` se use únicamente en paneles de código con *syntax highlighting* (salvo que el usuario pida código claro), fuentes `>= 13.5 pt` (`>= 11.5 pt` en código) y **0 colisiones de texto** entre shapes independientes.

### Paso 3 — Conversión a PDF/PNG e Inspección Visual con `view_file`
> **Nota importante en macOS:** Pasa siempre `-env:UserInstallation=file:///tmp/lo_profile_check` a `soffice` para evitar que LibreOffice salga silenciosamente si hay otra instancia abierta.
```bash
/opt/homebrew/bin/soffice -env:UserInstallation=file:///tmp/lo_profile_check --headless --convert-to pdf --outdir /tmp/slides_preview presentacion.pptx
/opt/homebrew/bin/pdftoppm -png -r 140 /tmp/slides_preview/presentacion.pdf /tmp/slides_preview/slide
```
Inspecciona las imágenes generadas con `view_file` para confirmar **cero textos montados**, **cero tags**, **cero desbordes de código** y legibilidad impecable.

---

## 7. Notas del Presentador, Consola HTML Interactiva y Codelabs Verificados

1. **Fuente Única de Notas del Presentador (`scripts/speaker_notes_data.py`):**
   * Cada diapositiva debe contar con notas estructuradas (`block`, `title`, `duration`, `cumulative`, `objective`, `say`, `point_out`, `transition`).
   * **Doble salida obligatoria:**
     1. **Nativa en PowerPoint:** Inyectar el guion completo en `slide.notes_slide.notes_text_frame.text` dentro de `build_deck.py`.
     2. **Consola HTML Interactiva (`presenter/index.html`):** Exportar todas las diapositivas a `presenter/slides/slide-01.png` … `slide-NN.png` y generar un visor HTML interactivo con **Modo Presentador 1 a 1** (imagen del slide actual + miniatura del siguiente slide a la izquierda, guion *"Qué decir"*, *"Qué señalar en pantalla"* y *"Puente al siguiente slide"* a la derecha, con cronómetro y ajuste de fuente `A-`/`A+`) y **Modo Lista Completa** (todas las diapositivas lado a lado con buscador y soporte de impresión PDF).
2. **Higiene de Versiones de Modelos (Cero Modelos Deprecados):**
   * **Prohibido** referenciar modelos deprecados en snippets o diagramas (como `gemini-1.5-*`, `gemini-2.0-*` o `gemini-2.5-flash`). Usa siempre los identificadores vigentes (`gemma4:e2b-it-qat`, `gemma4:e4b-it-qat`, `gemma4:26b-a4b`, `gemma4:31b`, `gemini-3-flash`, `gemini-3.1-pro`).
3. **Codelabs Alineados al Tema y con Screenshots Reales Ejecutados:**
   * Si la charla es sobre **Gemma**, el Codelab debe ser **100% Gemma** (sin depender de modelos externos ni desviar el taller hacia configuración de infraestructura ajena al foco).
   * **Prohibido entregar un Codelab sin capturas de pantalla:** Siempre construye y ejecuta la app del Codelab, ábrela en el navegador, captura screenshots reales de la interfaz funcionando (`assets/step*.png`) e incrústalos en los pasos del Codelab.
   * Para publicar sitios estáticos de charlas (Codelab + Consola del Presentador), prefiere **Firebase Hosting** por su CDN global instantáneo y SSL automático.

