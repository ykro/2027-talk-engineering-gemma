# Engineering with Gemma — Casos de uso y arquitecturas

- **Autor / Orador:** Adrián Catalán (`@adriancs.tech`)
- **Título:** *Engineering with Gemma: Casos de uso y arquitecturas*
- **Abstract:**
  > Exploraremos cómo diseñar soluciones con Gemma combinando ejecución local en edge y orquestación en servicios. Revisaremos código, retos de implementación y lecciones aprendidas construyendo herramientas productivas sobre Android y backend.

## Diapositivas

- **Presentación en Google Slides (33 slides):** [Engineering with Gemma](https://docs.google.com/presentation/d/1JTB1pReaqPWqmGg2ydelK6VS4uPKRfswLZDCYlsB67M/edit?usp=sharing)

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

La versión anterior de la presentación, su consola de presentador y el codelab anterior (CotizaSeguro) siguen en el historial de git de este repositorio.
