# Guía de Orador — Engineering with Gemma: Casos de uso y arquitecturas

- **Orador:** Adrián Catalán (`@adriancs.tech`)
- **Título oficial:** *Engineering with Gemma: Casos de uso y arquitecturas*
- **Abstract oficial:**
  > Exploraremos cómo diseñar soluciones con Gemma combinando ejecución local en edge y orquestación en servicios. Revisaremos código, retos de implementación y lecciones aprendidas construyendo herramientas productivas sobre Android y backend.
- **Duración estimada:** ~50 minutos + Q&A
- **Archivos sincronizados:**
  - Presentación PowerPoint (con notas integradas): `Gemma_Charla_2027.pptx`
  - Consola HTML interactiva de presentador: `presenter/index.html`
  - Codelab interactivo: `codelab/index.html`
- **Repositorios de referencia:**
  - Android / On-Device (`Generador de Excusas` con LiteRT-LM): `https://github.com/ykro/generador-excusas`
  - Backend / Cloud Run (`Cover Letter` con Gemma 4 E2B en Ollama): `https://github.com/ykro/coverletter-gemma`

---

## Mapa General de la Charla (32 Slides)

| Bloque | Slides | Enfoque | Tiempo |
| :--- | :---: | :--- | :---: |
| **Apertura y Ecosistema Gemma 4** | 1 – 6 | Problema del modelo único externo, rol de Gemini vs Gemma 4, mapa de familia `E2B`/`E4B`/`26B-A4B`/`31B` y variantes especializadas | 9.5 min |
| **Arquitectura Interna de Gemma 4** | 7 – 12 | Tokenizador 256k multimodal, Atención Híbrida 5 a 1 + KV Cache + PLE + QAT INT4, `-pt` vs `-it`, prompts deterministas y LiteRT-LM en Android | 10.5 min |
| **Adaptación con Prompting, RAG y QLoRA** | 13 – 17 | Criterios de decisión, RAG con `EmbeddingGemma 2` y vectores Matryoshka (`MRL`), matemática LoRA/QLoRA (`W₀ + B·A`) y entrenamiento con RAFT | 8.0 min |
| **Casos Split-Brain en Android y Cloud Run** | 18 – 27 | Frontera de privacidad determinista, Caso 1 en Android (*Excusa Legendaria* con LiteRT-LM y `LeakDetector.kt`) y Caso 2 en Cloud Run (*Cover Letter* con Ollama en GPU L4, router por niveles en TypeScript y benchmark real vs Qwen 3.5 2B) | 17.5 min |
| **Agentes con ADK para Kotlin y Lecciones** | 28 – 32 | Ciclo de eventos ADK en Android, intercambio de `BaseLlm`, confirmación humana (`requireConfirmation`), apps de referencia y lecciones aprendidas | 6.0 min |

---

## Notas del Presentador Slide por Slide

### Apertura y Ecosistema Gemma 4

#### Slide 01 — Engineering with Gemma — Casos de uso y arquitecturas
- **Tiempo:** `1.5 min` *(Acumulado: `00:00 – 01:30`)*
- **Imagen del slide:** `presenter/slides/slide-01.png`
- **Objetivo:** Dar la bienvenida, presentar la premisa de ingeniería de la charla y alinear expectativas: código real, decisiones de arquitectura y lecciones en producción.
- **Qué decir:**
  > ¡Hola a todos! Qué gusto estar con ustedes. Soy Adrián Catalán (@adriancs.tech) y hoy vamos a hablar de «Engineering with Gemma: Casos de uso y arquitecturas».
  >
  > Durante los últimos dos años, la forma por defecto de construir con IA generativa ha sido abrir un cliente HTTP y mandar absolutamente todo el texto del usuario a un único modelo gigante en la nube. Eso sirve para hacer un prototipo en una tarde, pero cuando llevas software a producción te topas con tres paredes: latencia, costos y, sobre todo, privacidad.
  >
  > En esta sesión vamos a ver cómo diseñar sistemas donde Gemma 4 trabaja en equipo con código determinista y modelos en la nube. Vamos a combinar ejecución local en el borde —directamente sobre la GPU y NPU de un teléfono Android— con orquestación privada en servicios backend sobre Cloud Run. Y lo haremos revisando el código real, los errores que cometimos en el camino y los benchmarks que medimos.
- **Qué señalar en pantalla:**
  - Mencionar que veremos dos sistemas completos de extremo a extremo: una app Android nativa (Excusa Legendaria + ADK para Kotlin) y un sistema web en producción sobre Cloud Run (Cover Letter).
  - Aclarar que no es una charla teórica de marketing de modelos, sino de arquitectura de software aplicada.
- **Transición al siguiente slide:** *Veamos rápidamente cómo está organizada la ruta de los próximos 45 minutos.*

#### Slide 02 — Ruta de la sesión
- **Tiempo:** `1.0 min` *(Acumulado: `01:30 – 02:30`)*
- **Imagen del slide:** `presenter/slides/slide-02.png`
- **Objetivo:** Mostrar el mapa mental de los 5 bloques para que la audiencia ubique la teoría, las técnicas de adaptación y las dos arquitecturas prácticas.
- **Qué decir:**
  > Dividimos el recorrido en cinco bloques conectados entre sí.
  >
  > Primero vamos a entender el ecosistema de Gemma 4 y qué hay realmente debajo del capó: por qué un modelo de 2 mil millones de parámetros efectivos hoy puede leer imágenes, escuchar audio y manejar 128 mil tokens en un teléfono.
  >
  > En el segundo bloque veremos cómo adaptar Gemma a tu dominio: cuándo basta con un buen prompt estructurado, cuándo conectar RAG con embeddings Matryoshka en SQLite, y cuándo vale la pena entrenar un adaptador QLoRA congelando las torres multimodales.
  >
  > Luego entraremos al corazón de la charla: las arquitecturas Split-Brain de privacidad, primero en Android con LiteRT-LM en el caso de Excusa Legendaria, y después en el backend sobre Cloud Run con GPU L4 en el proyecto Cover Letter.
  >
  > Y cerraremos construyendo agentes en Android con el Agent Development Kit (ADK) para Kotlin, viendo cómo intercambiar el modelo entre local y nube con una sola línea de código.
- **Qué señalar en pantalla:**
  - Señalar cómo pasamos de los fundamentos internos del modelo (bloques 1 y 2) a la arquitectura de sistemas en borde y backend (bloques 3, 4 y 5).
- **Transición al siguiente slide:** *Empecemos por la pregunta de arquitectura más importante: ¿por qué no mandar todo a un único LLM externo?*

#### Slide 03 — El problema de enviar todo a un único LLM externo
- **Tiempo:** `2.0 min` *(Acumulado: `02:30 – 04:30`)*
- **Imagen del slide:** `presenter/slides/slide-03.png`
- **Objetivo:** Desmontar el antipatrón de usar un único LLM remoto para todas las subtareas de una aplicación.
- **Qué decir:**
  > Cuando todo tu flujo depende de una sola API remota de frontera, sufres en tres frentes simultáneos.
  >
  > El primero es latencia y conectividad. Incluso con buena red, tienes entre 300 y 1,500 milisegundos de viaje redondo antes de ver el primer token. Y si tu usuario está en un avión, en un sótano o en trabajo de campo sin señal, tu aplicación simplemente deja de funcionar.
  >
  > El segundo frente es el costo operativo. Usar un modelo de cientos de miles de millones de parámetros solo para extraer tres campos JSON, normalizar texto o clasificar una intención es como contratar un tráiler de 18 ruedas para entregar una pizza. Pagas un impuesto por token en tareas mecánicas que un modelo compacto resuelve igual o mejor.
  >
  > Pero el tercer frente es el más crítico en ingeniería: la frontera de privacidad. Si tu aplicación maneja salarios actuales, nombres de clientes, historias clínicas o contratos, enviar esos bytes en crudo a un proveedor externo rompe tu perímetro de seguridad. Y como veremos más adelante, poner en el prompt «por favor ignora el salario» no evita que el dato ya haya viajado por la red.
- **Qué señalar en pantalla:**
  - Columna 1 (Rojo): RTT de red y dependencia total de conectividad.
  - Columna 2 (Ámbar): Pagar precio de modelo frontera por tareas de extracción o clasificación.
  - Columna 3 (Azul): Datos sensibles que jamás deberían cruzar hacia una API de terceros.
- **Transición al siguiente slide:** *Por eso Google diseñó a Gemini y a Gemma como dos piezas complementarias de una misma arquitectura.*

#### Slide 04 — Gemini y Gemma comparten ciencia pero cumplen roles distintos
- **Tiempo:** `1.5 min` *(Acumulado: `04:30 – 06:00`)*
- **Imagen del slide:** `presenter/slides/slide-04.png`
- **Objetivo:** Posicionar a Gemini y Gemma 4 no como competidores, sino como socios en una topología híbrida (perímetro privado + nube pública).
- **Qué decir:**
  > A veces me preguntan: «Adrián, ¿Gemma es solo el hermano pequeño de Gemini para cuando no tengo presupuesto?». La respuesta es un rotundo no: cumplen roles arquitectónicos distintos.
  >
  > Gemini, consumido como servicio en Vertex AI o Firebase AI Logic, es tu motor de escala masiva. Es ideal cuando necesitas conocimiento enciclopédico del mundo, razonamiento profundo o redacción creativa larga sin administrar infraestructura. Pero en nuestras arquitecturas, Gemini solo recibe payloads ya sanitizados y libres de datos sensibles.
  >
  > Gemma 4, en cambio, tiene pesos abiertos bajo licencia comercial Apache 2.0. Eso significa que tú eres dueño del binario y del proceso donde corre: puede vivir dentro del APK o bundle de Android usando LiteRT-LM, o dentro de tu propio contenedor privado en Cloud Run donde ningún byte sale de tu proyecto de Google Cloud. Gemma es el guardián que opera dentro de tu perímetro de confianza.
- **Qué señalar en pantalla:**
  - Tarjeta izquierda (Gemini): Razonamiento amplio sobre payloads públicos o ya anonimizados.
  - Tarjeta derecha (Gemma 4): Licenciamiento Apache 2.0, 1.1 a 1.8 GB de VRAM en versiones E2B/E4B y control absoluto del perímetro.
- **Transición al siguiente slide:** *Miremos de cerca cómo se compone la familia Gemma 4 hoy.*

#### Slide 05 — El ecosistema Gemma 4 de un vistazo
- **Tiempo:** `2.0 min` *(Acumulado: `06:00 – 08:00`)*
- **Imagen del slide:** `presenter/slides/slide-05.png`
- **Objetivo:** Explicar las dos zonas de despliegue de Gemma 4 (Borde/Móvil con E2B y E4B vs Servidor/Cloud con 26B-A4B MoE y 31B Dense).
- **Qué decir:**
  > En este diagrama vemos el mapa completo de la familia Gemma 4 dividido en dos grandes zonas operativas.
  >
  > A la izquierda tenemos la zona de Borde, Móvil y Contenedores Ligeros con dos modelos estrella: Gemma 4 E2B y Gemma 4 E4B. Esa letra «E» es importantísima y significa «Effective» (parámetros efectivos). Ambos soportan una ventana de contexto de 128 mil tokens y entienden texto, imágenes y audio de forma nativa. Cuantizados a 4 bits, el E2B ocupa entre 1.1 y 1.8 gigabytes de memoria, por lo que corre fluido en un teléfono de gama media o en un contenedor ligero de Cloud Run.
  >
  > A la derecha tenemos la zona de Servidor y Cloud para cargas pesadas, con contexto de hasta 256 mil tokens. Aquí destaca el modelo 26B-A4B, una arquitectura Mixture-of-Experts (MoE) que tiene 26 mil millones de parámetros totales pero solo activa 4 mil millones por cada token generado, dándote calidad de modelo grande con la velocidad y el costo de inferencia de uno de 4B. Y arriba del todo está el 31B Dense para razonamiento complejo, código pesado y agentes maestros.
- **Qué señalar en pantalla:**
  - Señalar el bloque izquierdo (E2B / E4B): destacar que son los protagonistas de nuestros dos casos reales (Android y Cloud Run).
  - Señalar el bloque derecho (26B-A4B MoE y 31B Dense): explicar la diferencia entre parámetros totales y parámetros activos en el MoE.
- **Transición al siguiente slide:** *Además de estos cuatro modelos troncales, el ecosistema incluye modelos quirúrgicos especializados.*

#### Slide 06 — Modelos especializados del ecosistema Gemma
- **Tiempo:** `1.5 min` *(Acumulado: `08:00 – 09:30`)*
- **Imagen del slide:** `presenter/slides/slide-06.png`
- **Objetivo:** Presentar los 4 modelos satelitales especializados para que el desarrollador no use un modelo generativo donde cabe un especialista de 300M.
- **Qué decir:**
  > Un principio clave de ingeniería con modelos abiertos es usar la herramienta más pequeña y especializada para cada trabajo.
  >
  > Si necesitas búsqueda semántica o RAG local, no uses un LLM generativo: usa EmbeddingGemma 2. Tiene apenas 308 millones de parámetros y genera vectores multilingües con representación Matryoshka, que te permiten recortar el vector de 768 a 128 dimensiones para buscar en milisegundos.
  >
  > Si necesitas auditar seguridad, moderar entradas tóxicas o filtrar respuestas antes de mostrarlas al usuario, tienes ShieldGemma 2.
  >
  > Si tu flujo gira en torno a traducir comandos de voz o texto del usuario en llamadas exactas a funciones JSON sin alucinar argumentos, existe FunctionGemma.
  >
  > Y para dominios verticales de visión o medicina, cuentas con PaliGemma 2 y MedGemma como bases listas para afinar.
- **Qué señalar en pantalla:**
  - Destacar EmbeddingGemma 2 (308M) arriba a la izquierda, que retomaremos en la sección de RAG Matryoshka.
  - Subrayar la idea de modularidad: combinar un modelo de 308M para buscar y un E2B para redactar.
- **Transición al siguiente slide:** *Con el mapa del ecosistema claro, abramos la caja negra: ¿qué hace que Gemma 4 sea tan rápido y quepa en tan poca memoria?*

### Arquitectura Interna de Gemma 4

#### Slide 07 — Sección — Arquitectura interna de Gemma 4
- **Tiempo:** `0.5 min` *(Acumulado: `09:30 – 10:00`)*
- **Imagen del slide:** `presenter/slides/slide-07.png`
- **Objetivo:** Hacer la transición hacia los fundamentos técnicos internos de Gemma 4.
- **Qué decir:**
  > Entremos ahora a la arquitectura interna de Gemma 4.
  >
  > Muchas veces tratamos al modelo como un archivo binario mágico, pero entender cuatro detalles de su diseño interno —su tokenizador de 256k, la atención híbrida 5 a 1, los Per-Layer Embeddings y la cuantización QAT— explica exactamente cómo configurar tus servidores y dispositivos móviles para no quedarte sin memoria.
- **Qué señalar en pantalla:**
  - Pausa breve de transición para cambiar de panorama general a anatomía técnica.
- **Transición al siguiente slide:** *Empecemos por la puerta de entrada al modelo: el tokenizador y los codificadores multimodales.*

#### Slide 08 — Tokenización 256k y entradas multimodales nativas
- **Tiempo:** `2.0 min` *(Acumulado: `10:00 – 12:00`)*
- **Imagen del slide:** `presenter/slides/slide-08.png`
- **Objetivo:** Explicar cómo texto, imagen y audio convergen en una misma secuencia de embeddings y por qué el vocabulario de 256k importa en español y código.
- **Qué decir:**
  > Para un Transformer todo en el universo es una secuencia de vectores, pero cómo conviertes la entrada en esos vectores marca una diferencia enorme.
  >
  > En texto, Gemma usa un tokenizador SentencePiece con un vocabulario de 256 mil entradas. ¿Por qué nos importa esto en Latinoamérica y al escribir código? Porque los modelos antiguos con vocabularios de 32k parten palabras en español con tildes o bloques de indentación en muchos pedacitos. Con 256k tokens, el mismo texto en español o código fuente ocupa alrededor de un 30% menos de tokens. Eso significa 30% menos consumo de batería en el móvil y 30% más velocidad de generación.
  >
  > En visión, no necesitas un pipeline externo de OCR. Un codificador ViT divide la foto o captura de pantalla en parches y los proyecta directamente como unos 256 tokens visuales dentro de la misma ventana de contexto.
  >
  > Y en los modelos E2B y E4B tenemos algo extraordinario para móvil: audio nativo basado en USM (Universal Speech Model). Convierte el audio en aproximadamente 25 tokens por segundo. El modelo escucha directamente la nota de voz sin que tengas que montar un modelo Speech-to-Text separado antes.
- **Qué señalar en pantalla:**
  - Tarjeta 1 (Texto): El ahorro del 30% de tokens en español y código gracias a los 256k tokens.
  - Tarjeta 2 (Visión) y Tarjeta 3 (Audio): Todo se proyecta al mismo espacio de embeddings antes de entrar al decoder.
- **Transición al siguiente slide:** *Ahora, una vez que esos tokens entran al Transformer, ¿cómo evita Gemma 4 que la memoria explote cuando le pasas 128 mil tokens?*

#### Slide 09 — Innovaciones que hacen viable Gemma 4 en móvil y GPU ligera
- **Tiempo:** `2.5 min` *(Acumulado: `12:00 – 14:30`)*
- **Imagen del slide:** `presenter/slides/slide-09.png`
- **Objetivo:** Explicar las 3 innovaciones clave de arquitectura: Atención Híbrida 5:1, Per-Layer Embeddings (PLE) y Quantization-Aware Training (QAT).
- **Qué decir:**
  > Este diagrama resume los tres trucos de ingeniería que hacen posible correr Gemma 4 en un teléfono o en una GPU económica.
  >
  > Primero, a la izquierda: la Atención Intercalada 5 a 1. En un Transformer clásico, todas las capas comparan todos los tokens contra todos los demás; eso crece de forma cuadrática y revienta la memoria RAM con contextos largos. Gemma 4 intercala 5 capas de atención local de ventana deslizante (que solo miran los 512 o 1024 tokens vecinos) por cada 1 capa de atención global que mira los 128k tokens completos. Además, las últimas capas comparten el mismo KV Cache. Resultado: el consumo de memoria del contexto cae drásticamente.
  >
  > Segundo, al centro: Per-Layer Embeddings o PLE, que explica la letra «E» en E2B y E4B. Si descargas Gemma 4 E2B verás que en total suma unos 4.6 a 5.1 mil millones de parámetros, pero más de la mitad son tablas de búsqueda por capa (PLE) que pueden vivir en RAM normal o flash, mientras que la GPU o NPU solo activa 2 mil millones de parámetros en multiplicaciones matriciales por cada token. Tienes el vocabulario y matiz de un modelo de casi 5B al costo de cómputo de un 2B.
  >
  > Y tercero, a la derecha: Quantization-Aware Training (QAT). En lugar de entrenar en 16 bits y recortar a 4 bits al final perdiendo calidad, Gemma 4 simula el redondeo INT4 durante el entrenamiento. Por eso el checkpoint oficial QAT conserva casi intacta la precisión del modelo original ocupando cuatro veces menos espacio.
- **Qué señalar en pantalla:**
  - Señalar el bloque izquierdo (5 capas Sliding Window + 1 Global): clave para que el KV Cache no sature la RAM móvil.
  - Señalar el bloque central (PLE): anticipar que en nuestro benchmark de Cloud Run veremos cómo esto hace que Gemma 4 E2B use apenas 1.80 GB de VRAM en una GPU L4.
  - Señalar el bloque derecho (QAT INT4): usar siempre los checkpoints con sufijo `-qat`.
- **Transición al siguiente slide:** *Hablando de sufijos de modelos, hay una confusión muy común al descargar pesos: la diferencia entre `-pt` e `-it`.*

#### Slide 10 — De completar texto a seguir instrucciones en modelos -pt vs -it
- **Tiempo:** `1.5 min` *(Acumulado: `14:30 – 16:00`)*
- **Imagen del slide:** `presenter/slides/slide-10.png`
- **Objetivo:** Aclarar el pipeline de entrenamiento desde Pre-training (-pt) hasta Instruction Tuning (-it) para evitar errores al elegir el checkpoint.
- **Qué decir:**
  > Cuando entras a Hugging Face, Kaggle u Ollama, verás dos variantes de cada modelo: `-pt` (Pre-trained) e `-it` (Instruction-tuned).
  >
  > El modelo `-pt` de la izquierda solo aprendió a predecir el siguiente token sobre billones de palabras. Si a un modelo `-pt` le preguntas «¿Cuál es la capital de Guatemala?», es muy probable que te responda «¿Cuál es la capital de El Salvador? ¿Cuál es la capital de Honduras?», porque asume que está autocompletando un examen de geografía.
  >
  > Para convertirlo en un asistente útil pasa por el pipeline que vemos hacia la derecha: primero Supervised Fine-Tuning (SFT) con marcadores estrictos de turno `<start_of_turn>`, y luego alineación por refuerzo (RLAIF / DPO) junto con QAT.
  >
  > Regla práctica: para cualquier aplicación de chat, extracción JSON o agentes en producción, usa siempre el checkpoint `-it`. El `-pt` solo se usa si vas a hacer pre-entrenamiento continuo sobre un corpus masivo propio.
- **Qué señalar en pantalla:**
  - Recorrer las 4 etapas del diagrama de izquierda a derecha: Pre-training → SFT → RLAIF/DPO + QAT → Checkpoint `-it` listo para producción.
- **Transición al siguiente slide:** *Veamos en código cómo se ven esos marcadores de turno y cómo estructurar un prompt determinista para un modelo 2B.*

#### Slide 11 — Anatomía de un prompt determinista para Gemma 4
- **Tiempo:** `2.0 min` *(Acumulado: `16:00 – 18:00`)*
- **Imagen del slide:** `presenter/slides/slide-11.png`
- **Objetivo:** Mostrar un ejemplo real de prompt estructurado para Gemma 4 y contar la anécdota real de ambigüedad lingüística en español.
- **Qué decir:**
  > Cuando trabajas con un modelo compacto de 2B o 4B parámetros, no puedes darle instrucciones vagas como harías con un modelo gigante en la nube. Tienes que ser quirúrgico.
  >
  > En el panel de código vemos la estructura exacta de turnos nativos de Gemma 4: `<start_of_turn>user` y `<start_of_turn>model`. Fíjense que definimos el rol, pedimos explícitamente JSON válido sin bloques markdown, damos el esquema exacto y, lo más importante, incluimos un ejemplo concreto (one-shot) antes de la entrada real.
  >
  > Aquí les comparto una lección real que nos pasó construyendo Cover Letter en español: en el primer prompt le pedimos a un modelo de 2B que redactara una «carta de interés» para un puesto de trabajo. ¿Qué hizo el modelo 2B? Nos redactó una carta bancaria formal hablando de tasas de interés compuesto, plazos fijos e IVA. Para un modelo pequeño, «carta de interés» activó el clúster semántico financiero.
  >
  > Bastó con desambiguar el término en el prompt escribiendo «carta de presentación profesional (cover letter) para postular a un empleo» y fijar temperatura 0 en las extracciones para que el problema desapareciera por completo.
- **Qué señalar en pantalla:**
  - Señalar en el código los tokens `<start_of_turn>user` y `<end_of_turn>` y el bloque `Ejemplo:` (one-shot).
  - En la tarjeta derecha, enfatizar la anécdota de «carta de interés» vs «carta de presentación (cover letter)».
- **Transición al siguiente slide:** *Ya tenemos el prompt estructurado. ¿Cómo ejecutamos este modelo directamente dentro de un teléfono Android sin servidor?*

#### Slide 12 — Ejecutando Gemma 4 en Android con LiteRT-LM
- **Tiempo:** `2.0 min` *(Acumulado: `18:00 – 20:00`)*
- **Imagen del slide:** `presenter/slides/slide-12.png`
- **Objetivo:** Explicar el código en Kotlin para cargar un archivo `.litertlm` en GPU/NPU móvil y consumir tokens en streaming con LiteRT-LM.
- **Qué decir:**
  > Este es el código real en Kotlin de nuestra clase `LocalGemmaBrain` usando el SDK de LiteRT-LM en Android.
  >
  > Lo primero que notarán es que son menos de veinte líneas de código. El modelo vive en un único archivo con extensión `.litertlm`, que ya trae empaquetados los pesos cuantizados en 4 bits, el vocabulario de SentencePiece y las reglas de parada.
  >
  > En la función `initialize`, creamos un `EngineConfig` pasándole la ruta del archivo local en el almacenamiento del teléfono y especificando `backend = Backend.GPU`. Esta línea es clave: le ordena al runtime delegar las multiplicaciones de matrices a la GPU móvil vía OpenCL o Vulkan, o a la NPU del procesador Qualcomm o MediaTek, liberando la CPU de la aplicación.
  >
  > Luego inicializamos el `Engine`, abrimos una `conversation` y en el método `stream` llamamos a `sendMessageAsync(prompt)`. Como devuelve un `Flow` de Kotlin, recolectamos cada fragmento en tiempo real y actualizamos la interfaz en Jetpack Compose token por token, sin una sola llamada de red.
- **Qué señalar en pantalla:**
  - Señalar `backend = Backend.GPU` en la línea 8 del panel de código.
  - Señalar `sendMessageAsync(prompt)?.collect { chunk -> ... }` mostrando la integración nativa con corrutinas y Flows de Kotlin.
- **Transición al siguiente slide:** *Ahora bien: ¿qué pasa cuando el conocimiento que necesita Gemma cambia todos los días o necesitamos afinar su comportamiento?*

### Adaptación con Prompting, RAG y QLoRA

#### Slide 13 — Sección — Adaptación con Prompting, RAG y QLoRA
- **Tiempo:** `0.5 min` *(Acumulado: `20:00 – 20:30`)*
- **Imagen del slide:** `presenter/slides/slide-13.png`
- **Objetivo:** Introducir el bloque de adaptación y personalización de modelos Gemma.
- **Qué decir:**
  > Pasemos al siguiente bloque: cómo adaptar Gemma a las reglas y datos de nuestro problema.
  >
  > Uno de los errores más caros en ingeniería de IA es saltar directamente a hacer Fine-Tuning cuando el problema se resolvía con un buen diseño de prompt o con búsqueda vectorial local. Veamos cómo tomar esa decisión con criterio.
- **Qué señalar en pantalla:**
  - Pausa breve de transición hacia la escalera de complejidad técnica.
- **Transición al siguiente slide:** *Aquí está la matriz de decisión que usamos antes de escribir una sola línea de entrenamiento.*

#### Slide 14 — Criterios para elegir entre Prompting, RAG y Fine-Tuning
- **Tiempo:** `2.0 min` *(Acumulado: `20:30 – 22:30`)*
- **Imagen del slide:** `presenter/slides/slide-14.png`
- **Objetivo:** Dar una regla clara de ingeniería para decidir entre Prompt Engineering, RAG con EmbeddingGemma 2 y Fine-Tuning con QLoRA.
- **Qué decir:**
  > Piensen en estas tres técnicas como una escalera donde solo subes al siguiente escalón cuando el anterior ya no alcanza.
  >
  > El primer escalón es Prompt Engineering con esquemas estructurados. Si puedes explicar la regla en diez líneas y un par de ejemplos —como hicimos para extraer requisitos de una oferta laboral en JSON—, quédate aquí. Cuesta cero GPUs de entrenamiento y puedes iterar en segundos.
  >
  > El segundo escalón es RAG con Embeddings. Si el modelo necesita responder sobre datos que cambian cada hora o cada día —como el catálogo de una tienda, notas clínicas del paciente o manuales técnicos—, nunca entrenes un modelo para memorizar hechos dinámicos. Usa EmbeddingGemma 2 para recuperar solo los tres párrafos relevantes e inyéctalos en el prompt.
  >
  > ¿Cuándo subes al tercer escalón, el Fine-Tuning con QLoRA? Cuando necesitas cambiar el comportamiento profundo, el formato nativo, el tono o enseñar un idioma o jerga de bajos recursos que el modelo base no domina, y donde meter cincuenta ejemplos en cada prompt saturaría tu ventana de contexto y tu latencia.
- **Qué señalar en pantalla:**
  - Recorrer de izquierda a derecha: Prompting (instrucciones estáticas) → RAG (hechos dinámicos que cambian a diario) → QLoRA (comportamiento, jerga o formato profundo).
- **Transición al siguiente slide:** *Veamos cómo funciona el segundo escalón en la práctica con EmbeddingGemma 2 y los vectores Matryoshka.*

#### Slide 15 — RAG con EmbeddingGemma 2 y representación Matryoshka
- **Tiempo:** `2.0 min` *(Acumulado: `22:30 – 24:30`)*
- **Imagen del slide:** `presenter/slides/slide-15.png`
- **Objetivo:** Explicar cómo Matryoshka Representation Learning (MRL) permite hacer RAG ultrarrápido en dos etapas dentro de SQLite.
- **Qué decir:**
  > ¿Cómo metes un motor de búsqueda semántica dentro de un teléfono Android o en un contenedor ligero sin levantar un servidor de base de datos vectorial externo? La respuesta es SQLite combinado con EmbeddingGemma 2 y Matryoshka Representation Learning (MRL).
  >
  > En un embedding tradicional de 768 dimensiones, la información está repartida por igual en las 768 casillas: si cortas el vector a la mitad, lo rompes. Pero EmbeddingGemma 2 se entrenó como las muñecas rusas Matryoshka: ordena la información más importante al principio del vector.
  >
  > Como ven en el diagrama, las primeras 128 dimensiones ya concentran cerca del 95% de la señal semántica, ocupando 6 veces menos RAM.
  >
  > Eso nos permite un pipeline en dos etapas: en la Etapa 1 hacemos un barrido ultrarrápido en SQLite comparando únicamente el prefijo recortado de 128 dimensiones para filtrar los mejores 25 candidatos en menos de 2 milisegundos. Y en la Etapa 2 hacemos el re-ranking exacto con las 768 dimensiones completas solo sobre esos 25 candidatos para quedarnos con el Top-3 e inyectarlo al prompt de Gemma 4.
- **Qué señalar en pantalla:**
  - Señalar la barra del vector Matryoshka: cómo el corte `vec[:128]` mantiene la semántica principal.
  - Señalar las dos etapas abajo: Filtro rápido Top-25 en 128-d → Re-ranking exacto Top-3 en 768-d → Prompt aumentado para Gemma 4.
- **Transición al siguiente slide:** *Y cuando sí necesitamos llegar al tercer escalón y modificar los pesos del modelo, entra en juego la matemática de LoRA y QLoRA.*

#### Slide 16 — Matemática de LoRA y QLoRA entrenando menos del 1% de pesos
- **Tiempo:** `1.5 min` *(Acumulado: `24:30 – 26:00`)*
- **Imagen del slide:** `presenter/slides/slide-16.png`
- **Objetivo:** Explicar visualmente la ecuación `h = W₀·x + (B·A)·x` y por qué permite afinar Gemma 4 en una sola GPU con 6 GB de VRAM.
- **Qué decir:**
  > Ajustar todos los parámetros de un modelo de miles de millones de pesos requiere un clúster caro y además suele provocar «olvido catastrófico»: el modelo aprende tu tarea nueva pero olvida cómo hablar bien español.
  >
  > LoRA y QLoRA resuelven esto con una idea algebraica muy elegante que vemos en el diagrama.
  >
  > A la izquierda tenemos la matriz original de pesos de Gemma 4, llamada W sub cero (`W₀`). La congelamos por completo y la comprimimos en formato NormalFloat de 4 bits (`NF4`). No se modifica ni un solo bit de esa matriz durante el entrenamiento.
  >
  > A la derecha colocamos una vía paralela compuesta por dos matrices diminutas, `A` y `B`, con un cuello de botella o rango `r` muy pequeño, típicamente de 8 o 16. Solo entrenamos esas dos matrices pequeñas, que representan menos del 1% de los parámetros totales, y al final sumamos su salida a la del modelo base: `h = W₀·x + (B·A)·x`. Cuando terminas, puedes fusionar matemáticamente `B·A` dentro de `W₀` para que en producción tengas cero latencia adicional.
- **Qué señalar en pantalla:**
  - Señalar la rama izquierda azul (`W₀` congelado en 4-bit NF4).
  - Señalar la rama derecha violeta (`A` y `B` con `r = 8 o 16`) y la suma `h = W₀·x + (B·A)·x` arriba.
- **Transición al siguiente slide:** *Veamos las tres decisiones críticas en código Python cuando entrenamos un QLoRA sobre Gemma 4.*

#### Slide 17 — Ajustando Gemma 4 con QLoRA y RAFT sobre el decoder
- **Tiempo:** `2.0 min` *(Acumulado: `26:00 – 28:00`)*
- **Imagen del slide:** `presenter/slides/slide-17.png`
- **Objetivo:** Mostrar el snippet real de entrenamiento PEFT/TRL destacando el filtro regex para congelar visión/audio, RAFT (85/15) y `completion_only_loss=True`.
- **Qué decir:**
  > Este script de Python condensa tres aprendizajes reales entrenando Gemma 4 con PEFT y TRL.
  >
  > Miren el punto 1: `target_modules`. Como Gemma 4 E2B y E4B son modelos nativamente multimodales, adentro tienen capas para visión y audio además del decoder de lenguaje. Si pasas `target_modules = 'all-linear'`, inyectarás adaptadores LoRA en las torres de visión y audio aunque solo estés entrenando con texto, desperdiciando VRAM y degradando esas capacidades. Por eso usamos esa expresión regular `r"model\.language_model\..*"` para aplicar LoRA exclusivamente al decoder de texto.
  >
  > En el punto 2 aplicamos RAFT (Retrieval-Augmented Fine-Tuning) con lo que llamamos Glossary Dropout 85/15: en el 85% de los ejemplos de entrenamiento le inyectamos contexto recuperado por RAG (barajado con distractores), y en el 15% se lo quitamos. Así el modelo aprende a obedecer el contexto cuando está presente sin volverse inútil cuando el buscador no encuentra coincidencias.
  >
  > Y en el punto 3 activamos `completion_only_loss = True` en `SFTConfig`. Esto es vital en un modelo 2B: calculamos el gradiente de error únicamente sobre la respuesta del asistente, nunca sobre las instrucciones del prompt, para no gastar capacidad memorizando el enunciado.
- **Qué señalar en pantalla:**
  - Línea 4 del código: el regex `r"model\.language_model\..*(q|k|v|o|gate|up|down)_proj"`.
  - Línea 8: `build_raft_prompt(..., gold_share = 0.85)`.
  - Línea 12: `SFTConfig(completion_only_loss = True)` y el `merge_and_unload()` final.
- **Transición al siguiente slide:** *Ya dominamos la anatomía de Gemma 4 y cómo adaptarla. Ahora entremos a las dos arquitecturas en producción: primero en Android y luego en Cloud Run.*

### Casos Split-Brain en Android y Cloud Run

#### Slide 18 — Sección — Arquitecturas Split-Brain en Android y Cloud Run
- **Tiempo:** `0.5 min` *(Acumulado: `28:00 – 28:30`)*
- **Imagen del slide:** `presenter/slides/slide-18.png`
- **Objetivo:** Presentar el bloque central de arquitecturas Split-Brain de privacidad aplicadas a dos plataformas distintas: móvil y backend serverless.
- **Qué decir:**
  > Entramos al corazón arquitectónico de la charla: las arquitecturas Split-Brain (cerebro dividido).
  >
  > Vamos a ver cómo el mismo principio de ingeniería se aplica primero en un teléfono Android con *Excusa Legendaria*, y después en un servicio web sobre Cloud Run con GPU L4 en *Cover Letter*.
- **Qué señalar en pantalla:**
  - Destacar que veremos tanto arquitectura cliente/borde (Kotlin + LiteRT-LM) como arquitectura backend (TypeScript/Next.js + Ollama en Cloud Run).
- **Transición al siguiente slide:** *Todo este bloque parte de una única tesis de seguridad que quiero que se lleven grabada.*

#### Slide 19 — Tesis de privacidad — Un prompt no es una frontera de seguridad
- **Tiempo:** `1.5 min` *(Acumulado: `28:30 – 30:00`)*
- **Imagen del slide:** `presenter/slides/slide-19.png`
- **Objetivo:** Establecer el axioma de privacidad de la charla: la frontera de seguridad es el proceso que no recibe los bytes, no una instrucción en lenguaje natural.
- **Qué decir:**
  > Lean esta frase con cuidado: «Un prompt no es una frontera de seguridad. Un proceso que no tiene los bytes, sí».
  >
  > Muchos equipos creen que protegen la privacidad del usuario agregando al final del system prompt: «Por favor, no menciones el salario actual del candidato ni el nombre de su jefe en la respuesta». Pero para cuando el LLM externo lee esa instrucción, los bytes con el salario y el nombre ya salieron del teléfono o de tu servidor y ya viajaron a la infraestructura de un tercero.
  >
  > La única forma verificable de garantizar que un modelo externo no filtre ni almacene un dato sensible es que el proceso que llama a ese modelo jamás reciba esos bytes. Y como los modelos pequeños también pueden equivocarse haciendo sumas o porcentajes, nuestra regla de arquitectura combina tres piezas: heurísticas deterministas en código para calcular y validar, Gemma 4 dentro de tu perímetro de confianza para razonar sobre lo privado, y una lista blanca estricta (allowlist) hacia terceros.
- **Qué señalar en pantalla:**
  - Leer textual la cita principal y señalar la línea inferior en tipografía monoespaciada: HEURÍSTICAS EN CÓDIGO + GEMMA EN TU PERÍMETRO + ALLOWLIST HACIA TERCEROS.
- **Transición al siguiente slide:** *Veamos cómo se materializa esta regla en nuestro primer caso real sobre Android: Excusa Legendaria.*

#### Slide 20 — Caso en Android — Frontera Split-Brain en el dispositivo
- **Tiempo:** `1.5 min` *(Acumulado: `30:00 – 31:30`)*
- **Imagen del slide:** `presenter/slides/slide-20.png`
- **Objetivo:** Explicar la separación física entre la zona privada del teléfono Android y la zona pública en la nube (`ykro/generador-excusas`).
- **Qué decir:**
  > Nuestro primer caso de uso se llama *Excusa Legendaria*, y tienen el repositorio completo en `github.com/ykro/generador-excusas`. El usuario escribe una situación real llena de datos personales: por ejemplo, «Se me olvidó la cena de aniversario con Laura en Antigua porque me quedé jugando videojuegos con Carlos».
  >
  > Queremos usar la creatividad de un modelo grande en la nube para redactar una excusa épica o diplomática, pero bajo ninguna circunstancia queremos que los nombres «Laura», «Carlos» o el lugar «Antigua» salgan del teléfono.
  >
  > Como ven en el diagrama, trazamos una frontera dura en el dispositivo: a la izquierda, dentro de la memoria local de Android, Gemma 4 E2B corre sobre LiteRT-LM e identifica las entidades sensibles, reemplazándolas por etiquetas genéricas como `[PERSON_1]`, `[PERSON_2]` y `[PLACE_1]`. A la derecha, hacia la nube, solo cruza el texto con esos placeholders. La nube redacta la historia sobre `[PERSON_1]` sin saber jamás quién es.
- **Qué señalar en pantalla:**
  - Señalar la línea divisoria del diagrama entre el dispositivo Android (donde se queda el mapa de identidades) y la nube (que solo ve `[PERSON_1]`, `[PLACE_1]`).
- **Transición al siguiente slide:** *Pero ¿qué pasa si Gemma 4 E2B comete un error al anonimizar? Veamos el pipeline completo de 8 pasos.*

#### Slide 21 — Pipeline híbrido de Excusa Legendaria en Android
- **Tiempo:** `2.0 min` *(Acumulado: `31:30 – 33:30`)*
- **Imagen del slide:** `presenter/slides/slide-21.png`
- **Objetivo:** Recorrer el flujo completo de 8 etapas en Android, destacando la compuerta determinista `LeakDetector` y el fallback automático a modo avión.
- **Qué decir:**
  > Un modelo de 2 mil millones de parámetros es excelente, pero es probabilístico: una de cada cien veces podría olvidar reemplazar un segundo apellido o un apodo. Por eso en el paso 4 del diagrama ven una compuerta determinista llamada `LeakDetector` escrita en Kotlin puro.
  >
  > Sigamos el flujo: en el paso 1 entra el texto crudo con PII. En el paso 2, Gemma 4 E2B local extrae las entidades y genera el texto sanitizado junto con una tabla hash en RAM (`PlaceholderMap`).
  >
  > En el paso 4, antes de abrir siquiera el socket de red, `LeakDetector` inspecciona carácter por carácter —normalizando mayúsculas y quitando tildes— que ninguno de los secretos originales aparezca en el texto sanitizado. Si detecta un solo rastro, aborta la llamada a la nube (*fail-closed*).
  >
  > Si pasa la auditoría, en el paso 5 tomamos una decisión según la conectividad: si hay internet, Gemini en la nube redacta el borrador sobre los placeholders; si el usuario va en un avión sin red, el mismo Gemma 4 E2B local redacta el borrador en el dispositivo. Y finalmente, en el paso 7, el `Rehydrator` en Kotlin hace un reemplazo inverso en memoria para devolver los nombres reales a la pantalla del usuario.
- **Qué señalar en pantalla:**
  - Señalar el Paso 4 (`LeakDetector` en Kotlin): el guardia determinista antes de la red.
  - Señalar la bifurcación del Paso 5: Nube con placeholders (Online) vs Gemma 4 E2B local (Offline).
- **Transición al siguiente slide:** *Miremos el código en Kotlin que implementa este orquestador y el detector de fugas.*

#### Slide 22 — Orquestador Split-Brain y detector determinista en Kotlin
- **Tiempo:** `2.0 min` *(Acumulado: `33:30 – 35:30`)*
- **Imagen del slide:** `presenter/slides/slide-22.png`
- **Objetivo:** Explicar la implementación concisa de `ExcusePipeline.kt` y `LeakDetector.kt` en Kotlin.
- **Qué decir:**
  > Aquí tienen el corazón de `ExcusePipeline.kt`. Toda la política de privacidad de la app se lee en cuatro pasos claros dentro de una función `suspend`.
  >
  > En el paso 1 llamamos a `localGemma.anonymize(rawScenario)` y construimos el `PlaceholderMap` en memoria volátil.
  >
  > En el paso 2 ejecutamos `LeakDetector.findLeaks(anon.sanitizedText, map.secrets)`. Noten la regla de oro del subtítulo: nunca uses un segundo LLM para auditar si el primer LLM filtró datos privados. Para verificar fugas usamos código determinista que normaliza Unicode NFD, elimina diacríticos para que «Gómez» y «gomez» coincidan, y divide nombres compuestos en sub-tokens. Si `leaks.isNotEmpty()`, devolvemos `PipelineResult.Blocked` inmediatamente.
  >
  > En el paso 3 el `if (isOnline)` decide quién redacta sobre el texto ya limpio, y en el paso 4 `Rehydrator.restore(draft, map)` restaura los nombres en tiempo lineal O(N) antes de pintar la UI.
- **Qué señalar en pantalla:**
  - Señalar las líneas 6 y 7 del código: `val leaks = LeakDetector.findLeaks(...)` y el retorno temprano `PipelineResult.Blocked(leaks)`.
  - Señalar las líneas 10 y 11: la conmutación transparente entre `cloudGemini` y `localGemma`.
- **Transición al siguiente slide:** *Así se ve esta arquitectura corriendo en un dispositivo Android real.*

#### Slide 23 — Excusa Legendaria ejecutándose en Android
- **Tiempo:** `1.5 min` *(Acumulado: `35:30 – 37:00`)*
- **Imagen del slide:** `presenter/slides/slide-23.png`
- **Objetivo:** Mostrar la evidencia visual de la app Android funcionando tanto en modo avión 100% local como en la vista de auditoría de placeholders.
- **Qué decir:**
  > En estas dos capturas vemos a *Excusa Legendaria* en acción.
  >
  > En la captura de la izquierda el teléfono está en modo avión, sin Wi-Fi ni datos móviles. Gemma 4 E2B se encarga absolutamente de todo el flujo sobre LiteRT-LM en el dispositivo.
  >
  > En la captura de la derecha vemos el panel de inspección de privacidad que incluimos en la app para demostrar la arquitectura: arriba pueden ver exactamente el payload sanitizado con `[PERSON_1]` y `[PLACE_1]` que viajó a la nube, con el sello verde de «0 fugas verificadas por LeakDetector», y abajo el texto final ya rehidratado en el teléfono con los nombres originales.
- **Qué señalar en pantalla:**
  - Captura izquierda: indicador de ejecución 100% local sin conexión.
  - Captura derecha: contraste visual entre el payload sanitizado (con placeholders) y el resultado rehidratado.
- **Transición al siguiente slide:** *Ahora llevemos exactamente esta misma filosofía Split-Brain del teléfono móvil hacia el backend en nuestro segundo caso real: Cover Letter sobre Cloud Run.*

#### Slide 24 — Caso en Cloud Run — Cover Letter y niveles de confianza
- **Tiempo:** `2.0 min` *(Acumulado: `37:00 – 39:00`)*
- **Imagen del slide:** `presenter/slides/slide-24.png`
- **Objetivo:** Explicar la arquitectura de 3 niveles de confianza (Navegador, Cloud Run Privado con Gemma 4 E2B, y Tercero con Gemini) en el proyecto Cover Letter (`ykro/coverletter-gemma`).
- **Qué decir:**
  > ¿Qué pasa cuando estás construyendo una aplicación web y no puedes exigirle al usuario que descargue un modelo de 1.5 gigabytes en el navegador de su teléfono, pero igual manejas información ultrasensible? Ese es el caso de *Cover Letter*, cuyo repositorio abierto está en `github.com/ykro/coverletter-gemma`.
  >
  > En *Cover Letter*, una persona ingresa su perfil profesional, la oferta de trabajo a la que quiere postular, cuánto gana hoy y cuánto quiere ganar. Necesitamos entregarle dos cosas: una carta de presentación impecable y una nota privada de estrategia salarial.
  >
  > Para lograrlo dividimos la arquitectura en tres niveles de confianza que ven en el diagrama:
  >
  > En el Nivel 0 (el navegador del usuario), heurísticas puras en TypeScript calculan al instante la brecha salarial en porcentaje, las bandas de negociación de conservadora a agresiva, convierten quetzales y dólares, y redactan una primera capa de PII. Costo cero y latencia cero.
  >
  > En el Nivel 1 (nuestro Cloud Run privado), desplegamos `gemma4:e2b-it-qat` corriendo dentro de Ollama sobre una GPU NVIDIA L4, protegido por IAM (`--no-allow-unauthenticated`). Como ese contenedor vive dentro de nuestro propio proyecto y escala a cero sin guardar logs de terceros, tiene permiso de ver los números salariales para redactar la nota privada de negociación y extraer los requisitos de la oferta en JSON.
  >
  > Y en el Nivel 2 (el modelo externo, Gemini en Vertex AI), enviamos únicamente un payload filtrado por una lista blanca estricta que jamás incluye el salario actual, ni el salario deseado, ni el nombre del empleador actual.
- **Qué señalar en pantalla:**
  - Señalar los 3 niveles en el diagrama y en la tarjeta derecha: Nivel 0 (TypeScript en navegador), Nivel 1 (Gemma 4 E2B en Cloud Run privado con GPU L4), Nivel 2 (Gemini solo con allowlist).
- **Transición al siguiente slide:** *Veamos en código cómo se empaqueta y despliega Gemma 4 E2B en Cloud Run para que arranque en 3 segundos y sea privado por IAM.*

#### Slide 25 — Desplegando Gemma 4 E2B sobre Cloud Run con Ollama y GPU L4
- **Tiempo:** `2.0 min` *(Acumulado: `39:00 – 41:00`)*
- **Imagen del slide:** `presenter/slides/slide-25.png`
- **Objetivo:** Explicar las decisiones de infraestructura en el `Dockerfile` y `deploy.sh` de Cloud Run con GPU L4.
- **Qué decir:**
  > Miren el `Dockerfile` en la mitad superior del panel de código. Si tú despliegas Ollama vacío en Cloud Run y descargas el modelo cuando llega el primer usuario, cada arranque en frío va a tardar minutos bajando 4 gigabytes por red.
  >
  > El truco de producción está en las líneas 5 y 6: durante el `docker build`, levantamos el servidor de Ollama en segundo plano (`ollama serve & sleep 5`) y ejecutamos `ollama pull gemma4:e2b-it-qat`. Así los pesos quedan horneados dentro de las capas de la imagen en Artifact Registry. Cuando Cloud Run levanta una instancia nueva con GPU L4, el modelo ya está en disco local y pasa a VRAM en apenas 3.4 segundos.
  >
  > Abajo ven el comando `gcloud run deploy`: asignamos 1 GPU NVIDIA L4 (`--gpu 1 --gpu-type nvidia-l4`), 8 vCPUs, 32 GiB de RAM y configuramos `--min-instances 0` para que cuando nadie usa la app el costo sea exactamente cero dólares.
  >
  > Y fíjense en la última bandera: `--no-allow-unauthenticated`. El contenedor de Ollama no está abierto a internet; solo el backend de Next.js puede invocarlo presentando un ID Token firmado por IAM (`roles/run.invoker`), y además el proxy jamás acepta prompts libres desde el navegador.
- **Qué señalar en pantalla:**
  - Líneas 5–6 del código: `RUN ollama serve & sleep 5 && for m in $MODELS; do ollama pull ...` (pesos horneados en la imagen).
  - Líneas 11–15: `--gpu 1 --gpu-type nvidia-l4`, `--min-instances 0` y `--no-allow-unauthenticated`.
- **Transición al siguiente slide:** *Veamos ahora cómo el router en TypeScript garantiza en código que el salario jamás cruce hacia el Nivel 2.*

#### Slide 26 — Router por nivel de confianza y defensa en profundidad
- **Tiempo:** `2.0 min` *(Acumulado: `41:00 – 43:00`)*
- **Imagen del slide:** `presenter/slides/slide-26.png`
- **Objetivo:** Explicar la defensa en profundidad en `router.ts` (allowlist por tipo, doble redacción de montos/empresas y tests de mutación).
- **Qué decir:**
  > Este fragmento de `src/lib/router.ts` en *Cover Letter* muestra cómo implementamos defensa en profundidad en TypeScript.
  >
  > Primero definimos `TIER_ALLOWLIST`. Mientras que los niveles `device` y `private` (nuestro Gemma 4 en Cloud Run) tienen acceso a `PROFILE_FIELDS`, el nivel `third_party` solo permite cinco campos explícitos: nombre, puesto deseado, empresa destino, años de experiencia y logros. Los campos `currentSalary`, `desiredSalary` y `currentCompany` ni siquiera existen en ese arreglo.
  >
  > Pero ¿qué pasa si el usuario escribió su salario actual o el nombre de su jefe dentro del campo libre de «logros»? Ahí entra la función `buildThirdParty`: antes de validar con un esquema estricto de Zod (`LetterPayloadSchema.parse`), pasa cada texto libre por el redactor contextual `clean()`.
  >
  > Este redactor busca el monto conocido del salario en cualquier formato imaginable (`Q15,000`, `15k`, o incluso `2000` aunque parezca un año) y extrae las palabras distintivas del empleador actual (por ejemplo, «Pantaleon» dentro de «Grupo Pantaleon»), cuidando de no borrar el apellido del propio candidato si coincide.
  >
  > Y para estar seguros de que nuestras pruebas sirven, aplicamos pruebas de mutación en `leak.test.ts`: si comentas la línea del redactor, fallan inmediatamente 13 tests automatizados.
- **Qué señalar en pantalla:**
  - Señalar `TIER_ALLOWLIST.third_party` en las líneas 6–7 del código.
  - Señalar `clean(base.achievements)` y `LetterPayloadSchema.parse` en las líneas 12–16.
- **Transición al siguiente slide:** *Al construir este sistema hicimos un benchmark formal en Cloud Run comparando Gemma 4 E2B contra Qwen 3.5 2B. Los resultados nos sorprendieron.*

#### Slide 27 — Benchmark en Cloud Run y lecciones eligiendo Gemma 4 E2B
- **Tiempo:** `2.5 min` *(Acumulado: `43:00 – 45:30`)*
- **Imagen del slide:** `presenter/slides/slide-27.png`
- **Objetivo:** Presentar los datos duros del benchmark en producción sobre Cloud Run (GPU L4 vs CPU y Gemma 4 E2B vs Qwen 3.5 2B) y por qué Gemma 4 E2B fue elegido.
- **Qué decir:**
  > No elegimos Gemma 4 E2B por fe; construimos un arnés de evaluación reproducible sobre 12 perfiles reales de Latinoamérica y corrimos el benchmark tanto en Cloud Run con GPU L4 como en Cloud Run solo con CPU.
  >
  > Miren el primer hallazgo de rendimiento en la GPU L4: `gemma4:e2b-it-qat` genera a 117.7 tokens por segundo —redacta la nota salarial completa en 2.1 segundos— y ocupa apenas 1.80 gigabytes de VRAM. Compárenlo con `qwen3.5:2b`, que en la misma L4 corrió a 73.5 tokens por segundo ocupando 2.36 GB de VRAM. Gracias a los Per-Layer Embeddings y al QAT de 4 bits, Gemma 4 E2B es 1.6 veces más rápido y usa menos memoria de video.
  >
  > Segundo hallazgo, y la razón definitiva por la que Gemma 4 E2B ganó como modelo por defecto: en el puntaje agregado de calidad hubo un empate técnico (0.846 vs 0.843). Pero cuando miramos la tarea de extraer los requisitos de la oferta en JSON —datos que luego se reenvían al modelo de terceros en el Nivel 2—, Qwen coló la pretensión salarial dentro de los requisitos en 9 de 27 corridas, poniendo en riesgo la frontera de privacidad. Gemma 4 E2B lo hizo 0 de 27 veces.
  >
  > Tercer hallazgo: los números los calcula el código, no el LLM. Descubrimos que en perfiles donde el candidato ya ganaba más de lo que ofrecía el puesto, el modelo pequeño a veces invertía el signo de la brecha. Por eso TypeScript calcula el porcentaje exacto y una función determinista llamada `checkNumberConsistency` subraya en la UI cualquier cifra que el modelo mencione y no venga de las heurísticas.
  >
  > Y un tip real de infraestructura GCP: cuando nuestro proyecto nuevo no tenía cuota de GPU L4 con redundancia zonal en `us-central1`, inspeccionamos la métrica `NvidiaL4GpuAllocNoZonalRedundancy` y desplegamos con `--no-gpu-zonal-redundancy` en `europe-west4`, manteniendo además un servicio en CPU (18.6 tok/s) como fallback automático.
- **Qué señalar en pantalla:**
  - Señalar la tabla de la izquierda: 117.7 tok/s y 1.80 GB VRAM en GPU L4 vs 18.6 tok/s en CPU.
  - Enfatizar el dato de seguridad: 0/27 fugas de pretensión salarial en extracción JSON con Gemma 4 E2B frente a 9/27 en Qwen 3.5 2B.
- **Transición al siguiente slide:** *Con los casos de Android y Cloud Run cubiertos, cerremos los últimos minutos viendo cómo escalar de pipelines fijos a agentes autónomos con ADK para Kotlin.*

### Agentes con ADK para Kotlin y Lecciones

#### Slide 28 — Sección — Agentes en Android con ADK para Kotlin
- **Tiempo:** `0.5 min` *(Acumulado: `45:30 – 46:00`)*
- **Imagen del slide:** `presenter/slides/slide-28.png`
- **Objetivo:** Introducir el bloque final sobre el Agent Development Kit (ADK) para Kotlin en Android.
- **Qué decir:**
  > En los dos casos anteriores nosotros programamos el orden exacto de los pasos del pipeline.
  >
  > Pero ¿qué pasa cuando queremos que el modelo decida dinámicamente qué herramientas invocar, consulte manuales bajo demanda y recuerde la sesión en una base de datos local? Para eso usamos el Agent Development Kit (ADK) para Kotlin.
- **Qué señalar en pantalla:**
  - Transición hacia la arquitectura agéntica sobre Android.
- **Transición al siguiente slide:** *Veamos cómo funciona el ciclo de eventos de ADK en Android.*

#### Slide 29 — Arquitectura del Agent Development Kit (ADK) para Kotlin
- **Tiempo:** `1.5 min` *(Acumulado: `46:00 – 47:30`)*
- **Imagen del slide:** `presenter/slides/slide-29.png`
- **Objetivo:** Explicar los componentes del ADK para Kotlin (`Runner`, `LlmAgent`, `BaseLlm`, `FunctionTool`, `SkillToolset` y `RoomSessionService`).
- **Qué decir:**
  > Lo mejor del ADK para Kotlin es que trae los mismos patrones de diseño de agentes del backend directamente a una aplicación Android nativa, sin depender de un servidor intermedio.
  >
  > En el centro del diagrama tenemos el `Runner` y el `LlmAgent`. Fíjense en la parte superior: el agente no está acoplado a un proveedor fijo; habla contra una interfaz común llamada `BaseLlm`. Eso significa que abajo puedes conectarle `LiteRtLmModel` con Gemma 4 corriendo en la NPU del teléfono, o `FirebaseAiLogicModel` apuntando a Gemini en la nube.
  >
  > Y en la parte inferior el agente se conecta con tres piezas clave: `FunctionTool` para ejecutar funciones de Kotlin tipadas con `@Tool`, `SkillToolset` para cargar instrucciones especializadas solo cuando hacen falta sin llenar la ventana de contexto del modelo 2B, y `RoomSessionService` para guardar cada turno de conversación en SQLite local.
- **Qué señalar en pantalla:**
  - Señalar la abstracción `BaseLlm` arriba (`LiteRtLmModel` vs `FirebaseAiLogicModel`).
  - Señalar las tres capacidades inferiores: `@Tool`, `SkillToolset` y `RoomSessionService`.
- **Transición al siguiente slide:** *Miremos en código qué tan limpio es intercambiar el modelo y agregar confirmación humana.*

#### Slide 30 — Intercambio de modelo con BaseLlm y confirmación humana
- **Tiempo:** `1.5 min` *(Acumulado: `47:30 – 49:00`)*
- **Imagen del slide:** `presenter/slides/slide-30.png`
- **Objetivo:** Mostrar el snippet de `AgentFactory.kt` donde se intercambia `BaseLlm` en una línea y se protege una herramienta crítica con `requireConfirmation = true`.
- **Qué decir:**
  > Miren las primeras tres líneas del código en `AgentFactory.kt`: instanciamos `localModel` con `LiteRtLmModel` apuntando a nuestro archivo de Gemma 4 en GPU, e instanciamos `cloudModel` con `FirebaseAiLogicModel`.
  >
  > Cuando construimos el `LlmAgent` en la línea 12, literalmente hacemos `.model(if (isOffline) localModel else cloudModel)`. Ni tu interfaz en Jetpack Compose, ni tus herramientas, ni tu base de datos Room se enteran del cambio.
  >
  > Y miren las líneas 5 a 9: cuando le das herramientas a un agente para que ejecute acciones reales —como vaciar un carrito de compras o procesar un pago en `CartTools::checkout`—, nunca quieres que un modelo tome esa decisión a ciegas. Al declarar `requireConfirmation = true` en `FunctionTool.create`, el `Runner` de ADK intercepta la llamada antes de ejecutar el código Kotlin, pausa el flujo y emite un evento a la UI para que el usuario humano presione «Confirmar» o «Cancelar».
- **Qué señalar en pantalla:**
  - Líneas 2–3 y 12: la conmutación en una línea entre `localModel` y `cloudModel`.
  - Línea 8: `requireConfirmation = true` para Human-in-the-Loop nativo.
- **Transición al siguiente slide:** *En el repositorio de la charla incluimos tres aplicaciones de referencia que demuestran cada uno de estos patrones.*

#### Slide 31 — Aplicaciones de referencia con ADK para Kotlin
- **Tiempo:** `1.0 min` *(Acumulado: `49:00 – 50:00`)*
- **Imagen del slide:** `presenter/slides/slide-31.png`
- **Objetivo:** Resumir brevemente las 3 apps complementarias (Cart Shop, Recovery Pal y Trail Aid) para que la audiencia sepa qué explorar en el repositorio.
- **Qué decir:**
  > Para que puedan explorar estos patrones funcionando, tenemos tres aplicaciones de referencia construidas con ADK para Kotlin:
  >
  > La primera es *Cart Shop*, un asistente de comercio electrónico que demuestra el patrón de `FunctionTool` con confirmación humana obligatoria antes de pagar o vaciar el carrito.
  >
  > La segunda es *Recovery Pal*, un asistente de seguimiento médico post-operatorio donde todos los síntomas y recordatorios de medicación se procesan localmente y se persisten con `RoomSessionService`, garantizando que ningún dato clínico salga del teléfono.
  >
  > Y la tercera es *Trail Aid*, pensada para senderismo y supervivencia en montaña sin señal celular: corre 100% offline con Gemma 4 y usa `SkillToolset` para cargar manuales de primeros auxilios desde los `assets` bajo demanda, manteniendo limpio el contexto del modelo.
- **Qué señalar en pantalla:**
  - Señalar brevemente cada tarjeta asociándola con su patrón técnico: Cart Shop (`requireConfirmation`), Recovery Pal (`RoomSessionService`) y Trail Aid (`SkillToolset` 100% offline).
- **Transición al siguiente slide:** *Terminemos resumiendo las cuatro lecciones de ingeniería más importantes de todo este recorrido.*

#### Slide 32 — Lecciones aprendidas en Android y Cloud Run
- **Tiempo:** `1.5 min` *(Acumulado: `50:00 – 51:30`)*
- **Imagen del slide:** `presenter/slides/slide-32.png`
- **Objetivo:** Cerrar con fuerza dejando los 4 principios arquitectónicos validados en Android y Cloud Run, e invitar a explorar el código y el codelab.
- **Qué decir:**
  > Si nos quedamos con cuatro principios de ingeniería después de construir y medir estos sistemas en Android y Cloud Run, son estos:
  >
  > Primero: el código determinista calcula y filtra; el modelo redacta. Nunca delegues aritmética salarial ni auditoría de fugas PII a la buena fe de un prompt. Usa Kotlin o TypeScript probado con tests de mutación.
  >
  > Segundo: Gemma 4 E2B brilla cuando opera dentro de tu perímetro de confianza. Ya sea en la NPU del teléfono con LiteRT-LM a costo cero, o en tu propio contenedor de Cloud Run con GPU L4 e IAM generando a 118 tokens por segundo en apenas 1.8 GB de VRAM.
  >
  > Tercero: evalúa los modelos en las tareas reales de tu aplicación, no por su posición en un ranking genérico. Medir en nuestro propio pipeline fue lo que nos reveló la ambigüedad de «carta de interés» y el riesgo de fuga en extracción JSON.
  >
  > Y cuarto: diseña siempre para una degradación elegante. Si la GPU en Cloud Run está despertando o el usuario entra a un túnel sin señal, tus heurísticas instantáneas y el fallback local mantienen la aplicación viva sin pantallas de error.
  >
  > Ahí tienen mis datos de contacto (`@adriancs.tech`) y el repositorio con el código, los diagramas y el benchmark completo. ¡Muchas gracias y abrimos espacio para preguntas!
- **Qué señalar en pantalla:**
  - Recorrer las 4 tarjetas de cierre y señalar los enlaces finales a `github.com/ykro/generador-excusas` y `github.com/ykro/coverletter-gemma`.
- **Transición al siguiente slide:** *¡Muchas gracias! Abrimos el micrófono para preguntas.*
