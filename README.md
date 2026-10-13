# Engineering with Gemma — Casos de uso y arquitecturas

- **Autor / Orador:** Adrián Catalán (`@adriancs.tech`)
- **Título:** *Engineering with Gemma: Casos de uso y arquitecturas*
- **Abstract:**
  > Exploraremos cómo diseñar soluciones con Gemma combinando ejecución local en edge y orquestación en servicios. Revisaremos código, retos de implementación y lecciones aprendidas construyendo herramientas productivas sobre Android y backend.

## Diapositivas (Versión Más Reciente)

- **Presentación en Google Slides (versión más reciente, 33 slides):** [Engineering with Gemma](https://docs.google.com/presentation/d/1JTB1pReaqPWqmGg2ydelK6VS4uPKRfswLZDCYlsB67M/edit?usp=sharing)
- **Versión anterior (32 slides), guardada en este repositorio:** [`Gemma_Charla_2027.pptx`](./Gemma_Charla_2027.pptx) y su guía de orador [`charla-gemma-2027.md`](./charla-gemma-2027.md)

---

## Demos de la Charla (Repositorios Públicos)

1. **Demo Edge / Android (`Generador de Excusas` con LiteRT-LM y Gemma on-device):**
   - [https://github.com/ykro/generador-excusas](https://github.com/ykro/generador-excusas)
2. **Demo Cloud Run / Arquitectura Split-Brain (`Cover Letter` con Gemma 4 E2B sobre Ollama):**
   - [https://github.com/ykro/coverletter-gemma](https://github.com/ykro/coverletter-gemma)

---

## Taller práctico

El taller de esta charla es **«Split-brain en el navegador»**: Gemma 4 corre en Chrome con WebGPU, encuentra los datos personales y el código los cubre antes de pedirle ayuda a Gemini.

- **Taller:** [https://codelabs-2027-z63pqhhmxq-uc.a.run.app/gemma-en-el-navegador](https://codelabs-2027-z63pqhhmxq-uc.a.run.app/gemma-en-el-navegador)
- **Código:** [ykro/codelabs-2027](https://github.com/ykro/codelabs-2027/tree/main/gemma-en-el-navegador)

La carpeta `codelab/` de este repo es el codelab anterior (CotizaSeguro). Se guarda solo como código y ya no está publicada.

---

## Estructura del Repositorio

```text
.
├── Gemma_Charla_2027.pptx          # Presentación final (32 slides, 16:9, Light Mode + Notas del presentador integradas)
├── charla-gemma-2027.md            # Guía completa del orador en Markdown sincronizada slide por slide
├── presenter/
│   ├── index.html                  # Consola interactiva del presentador (Modo 1 a 1 con cronómetro + Modo Lista de 32 slides)
│   └── slides/                     # Los 32 slides exportados en PNG de alta resolución (slide-01.png .. slide-32.png)
├── codelab/
│   ├── index.html                  # Codelab interactivo estilo Google Codelabs (100% Gemma 4 — Caso CotizaSeguro)
│   ├── assets/                     # Capturas reales verificadas en navegador de la aplicación funcionando
│   └── demo-app/                   # Implementación ejecutable del Codelab (100% Gemma 4 sobre Ollama + Node.js)
│       ├── server.mjs              # Servidor HTTP + Heurísticas + Redactor PII/NDA + Doble Contexto Gemma 4 + Auditoría
│       ├── leak.test.mjs           # Suite de pruebas automatizadas de cero fugas y consistencia numérica (node --test)
│       └── public/index.html       # Interfaz web interactiva de CotizaSeguro
├── scripts/
│   ├── build_deck.py               # Generador programático de Gemma_Charla_2027.pptx con python-pptx
│   ├── speaker_notes_data.py       # Fuente única de verdad para las notas del presentador de los 32 slides
│   ├── build_presenter_html.py     # Generador de presenter/index.html y charla-gemma-2027.md
│   └── generate_diagrams.py        # Generador de diagramas de arquitectura en alta resolución (@2.5x)
├── assets/                         # Diagramas vectoriales renderizados y capturas de Android / Cover Letter
└── skills/adrian-slides/SKILL.md   # Skill con las reglas editoriales y visuales de @adriancs.tech
```

---

## Cómo Regenerar las Diapositivas y la Consola del Presentador

1. **Regenerar el archivo PowerPoint (`Gemma_Charla_2027.pptx`) con las notas integradas:**
   ```bash
   python3 scripts/build_deck.py
   ```

2. **Regenerar la Consola HTML del Presentador (`presenter/index.html`) y la guía Markdown (`charla-gemma-2027.md`):**
   ```bash
   python3 scripts/build_presenter_html.py
   ```

---

## Cómo Ejecutar y Probar la Aplicación del Codelab (`CotizaSeguro` — 100% Gemma 4)

El directorio `codelab/demo-app/` contiene la aplicación completa del Codelab (**CotizaSeguro**):

1. **Ejecutar la suite de pruebas automatizadas de privacidad y consistencia numérica:**
   ```bash
   node --test codelab/demo-app/leak.test.mjs
   ```

2. **Iniciar el servidor web (conecta con `gemma4:e2b` en Ollama en `http://localhost:11434`):**
   ```bash
   node codelab/demo-app/server.mjs
   # Abre http://localhost:4321 en tu navegador
   ```

---

## Despliegue del Codelab en Firebase Hosting

El sitio estático del Codelab (`codelab/`) se despliega con:

```bash
npx firebase-tools deploy --only hosting --project ai-experiments-487722
```
