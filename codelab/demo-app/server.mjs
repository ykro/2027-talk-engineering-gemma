import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 4321;
const OLLAMA_URL = process.env.OLLAMA_URL || "http://localhost:11434";
const GEMMA_MODEL = process.env.GEMMA_MODEL || "gemma4:e2b";

// ============================================================================
// 1. HEURÍSTICAS DETERMINISTAS Y REDACTOR DE PRIVACIDAD (Nivel 0)
// ============================================================================
export function calculateMargin(profile) {
  const totalCost = profile.internalHourlyCostUSD * profile.estimatedHours;
  const totalPrice = profile.proposedHourlyRateUSD * profile.estimatedHours;
  const grossProfit = totalPrice - totalCost;
  const marginPct = Math.round((grossProfit / totalPrice) * 1000) / 10;
  const band =
    marginPct < 25 ? "riesgoso" :
    marginPct < 45 ? "saludable" : "alto_margen";
  const minAcceptableTotal = Math.round(totalCost / (1 - 0.30)); // Piso de 30% margen
  return { totalCost, totalPrice, grossProfit, marginPct, band, minAcceptableTotal };
}

export function redactSensitiveData(text, profile) {
  let out = String(text || "");
  const redactions = [];

  // 1. Redactar cliente bajo NDA y sus tokens distintivos (>= 4 letras)
  const genericWords = new Set(["banco", "grupo", "corporacion", "empresa", "sociedad", "financiera"]);
  const tokens = (profile.ndaClientReference || "")
    .split(/\s+/)
    .map(w => w.replace(/[.,;()]/g, ""))
    .filter(w => w.length >= 4 && !genericWords.has(w.toLowerCase()));

  for (const tok of [profile.ndaClientReference, ...tokens]) {
    if (!tok) continue;
    const escaped = tok.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(escaped, "gi");
    if (re.test(out)) {
      redactions.push({ token: tok, replacement: "[CLIENTE_FINANCIERO_NDA]" });
      out = out.replace(re, "[CLIENTE_FINANCIERO_NDA]");
    }
  }

  // 2. Redactar montos confidenciales (costo hora interno y costo total interno)
  const totals = calculateMargin(profile);
  const secretNumbers = [
    profile.internalHourlyCostUSD,
    totals.totalCost,
    totals.grossProfit,
  ];
  for (const num of secretNumbers) {
    if (!num) continue;
    const plain = String(num);
    const comma = Number(num).toLocaleString("en-US");
    for (const variant of [comma, plain]) {
      const re = new RegExp(`(?:USD\\s*|\\$\\s*)?\\b${variant.replace(/,/g, ",?")}\\b(?:\\s*\\/\\s*h(?:ora)?)?`, "gi");
      if (re.test(out)) {
        redactions.push({ token: variant, replacement: "[COSTO_INTERNO_RESERVADO]" });
        out = out.replace(re, "[COSTO_INTERNO_RESERVADO]");
      }
    }
  }

  return { sanitizedText: out, redactions };
}

// ============================================================================
// 2. ROUTER CON ALLOWLIST ESTRICTA Y AUDITOR DE FUGAS
// ============================================================================
export const PUBLIC_ALLOWLIST = [
  "consultantName",
  "targetClient",
  "projectRole",
  "estimatedHours",
  "proposedHourlyRateUSD",
  "sanitizedAchievements",
  "sanitizedDeliverables",
];

export function buildPublicProposalPayload(profile, deliverables) {
  const cleanAch = redactSensitiveData(profile.teamAchievements, profile);
  const cleanDeliv = deliverables.map(d => redactSensitiveData(d, profile).sanitizedText);

  // Allowlist estricta: jamás incluye internalHourlyCostUSD ni ndaClientReference
  return {
    payload: {
      consultantName: profile.consultantName,
      targetClient: profile.targetClient,
      projectRole: profile.projectRole,
      estimatedHours: Number(profile.estimatedHours),
      proposedHourlyRateUSD: Number(profile.proposedHourlyRateUSD),
      sanitizedAchievements: cleanAch.sanitizedText,
      sanitizedDeliverables: cleanDeliv,
    },
    redactionsApplied: cleanAch.redactions,
    strippedFields: ["internalHourlyCostUSD", "ndaClientReference", "totalInternalCostUSD", "marginPct"],
  };
}

export function auditLeaks(publicText, profile) {
  const leaks = [];
  const lower = publicText.toLowerCase();
  const genericWords = new Set(["banco", "grupo", "corporacion", "empresa", "sociedad", "financiera"]);
  const ndaTokens = (profile.ndaClientReference || "")
    .split(/\s+/)
    .map(w => w.replace(/[.,;()]/g, "").toLowerCase())
    .filter(w => w.length >= 4 && !genericWords.has(w));

  for (const tok of ndaTokens) {
    if (lower.includes(tok)) leaks.push(`NDA token filtrado: "${tok}"`);
  }

  const costStr = String(profile.internalHourlyCostUSD);
  const costRegex = new RegExp(`\\b${costStr}\\b`);
  if (costRegex.test(publicText)) {
    leaks.push(`Costo hora interno filtrado: "$${costStr}"`);
  }

  return { passed: leaks.length === 0, leaks };
}

export function checkNumberConsistency(strategyText, allowedNumbers) {
  const matches = strategyText.match(/\d+(?:,\d{3})*(?:\.\d+)?/g) || [];
  const allowedSet = new Set(
    allowedNumbers.flatMap(n => [String(n), Number(n).toLocaleString("en-US")])
  );
  // Ignorar números pequeños de listas ("1", "2", "3")
  const unverified = matches.filter(m => Number(m.replace(/,/g, "")) > 5 && !allowedSet.has(m));
  return {
    consistent: unverified.length === 0,
    verifiedNumbers: matches.filter(m => allowedSet.has(m)),
    unverifiedNumbers: unverified,
  };
}

// ============================================================================
// 3. MOTOR GEMMA 4 (Ollama API en vivo + Fallback determinista si no hay daemon)
// ============================================================================
async function callGemmaOllama(messages, format = null) {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 90000);
    const res = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      body: JSON.stringify({
        model: GEMMA_MODEL,
        stream: false,
        think: false,
        options: { temperature: 0, seed: 42, num_predict: 280 },
        ...(format ? { format } : {}),
        messages,
      }),
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { content: data.message.content, live: true, engine: `${GEMMA_MODEL} (Ollama en vivo)` };
  } catch (err) {
    return null;
  }
}

async function runGemmaPipeline(profile) {
  const t0 = Date.now();
  const metrics = calculateMargin(profile);

  // Paso A: Extracción JSON de entregables desde el RFP con Gemma 4 (temperature = 0)
  const extractSchema = {
    type: "object",
    properties: {
      deliverables: { type: "array", items: { type: "string" } },
      securityLevel: { type: "string" },
    },
    required: ["deliverables", "securityLevel"],
  };

  let extracted = null;
  const gemmaExtract = await callGemmaOllama([
    {
      role: "system",
      content: "Eres un extractor técnico. Devuelve SOLO JSON con los entregables técnicos del RFP sin incluir presupuestos ni montos.",
    },
    { role: "user", content: profile.rfpText },
  ], extractSchema);

  if (gemmaExtract) {
    try {
      extracted = JSON.parse(gemmaExtract.content);
    } catch {
      extracted = null;
    }
  }

  if (!extracted) {
    extracted = {
      deliverables: [
        "Pasarela API RESTful con autenticación OAuth 2.0 y mTLS",
        "Módulo de conciliación transaccional en tiempo casi real (< 300 ms)",
        "Suite de pruebas de carga verificada a 500 peticiones por segundo (RPS)",
        "Despliegue automatizado en contenedores con monitoreo de SLOs",
      ],
      securityLevel: "Crítico · Grado Financiero / Asegurador",
    };
  }

  // Paso B: Construir Payload Sanitizado para el documento del cliente (Allowlist + Redactor)
  const routed = buildPublicProposalPayload(profile, extracted.deliverables);
  const safe = routed.payload;

  // Paso C: Gemma 4 (Contexto Privado) -> Nota Interna de Rentabilidad y Negociación
  let strategyNote = null;
  const gemmaStrategy = await callGemmaOllama([
    {
      role: "system",
      content: "Eres un estratega de precios B2B. Redacta una nota privada en segunda persona usando SOLO las cifras provistas.",
    },
    {
      role: "user",
      content: `Costo hora interno: $${profile.internalHourlyCostUSD}/h. Tarifa propuesta: $${profile.proposedHourlyRateUSD}/h. Horas: ${profile.estimatedHours}. Costo interno total: $${metrics.totalCost.toLocaleString("en-US")}. Precio total: $${metrics.totalPrice.toLocaleString("en-US")}. Ganancia bruta: $${metrics.grossProfit.toLocaleString("en-US")}. Margen: ${metrics.marginPct}% (${metrics.band}). Piso mínimo (30% margen): $${metrics.minAcceptableTotal.toLocaleString("en-US")}.`,
    },
  ]);

  if (gemmaStrategy) {
    strategyNote = gemmaStrategy.content;
  } else {
    strategyNote =
      `Tu cotización para ${profile.targetClient} proyecta un precio total de $${metrics.totalPrice.toLocaleString("en-US")} USD (${profile.estimatedHours} horas a $${profile.proposedHourlyRateUSD}/h) frente a un costo interno real de $${metrics.totalCost.toLocaleString("en-US")} USD ($${profile.internalHourlyCostUSD}/h), generando una utilidad bruta de $${metrics.grossProfit.toLocaleString("en-US")} USD y un margen de ${metrics.marginPct}% (banda: ${metrics.band}).\n\n` +
      `1. Ancla de negociación: Presenta el valor de los 4 entregables técnicos antes de discutir descuentos por volumen.\n` +
      `2. Piso financiero: Si compras solicita descuento, tu piso con 30% de margen mínimo es $${metrics.minAcceptableTotal.toLocaleString("en-US")} USD. Nunca reveles tu costo base de $${profile.internalHourlyCostUSD}/h ni menciones por nombre a ${profile.ndaClientReference}.`;
  }

  // Paso D: Gemma 4 (Contexto Sanitizado) -> Propuesta Técnica Ejecutiva para el Cliente
  let publicProposal = null;
  const gemmaProposal = await callGemmaOllama([
    {
      role: "system",
      content: "Redacta una propuesta comercial ejecutiva en español profesional usando únicamente el payload sanitizado.",
    },
    {
      role: "user",
      content: JSON.stringify(safe),
    },
  ]);

  if (gemmaProposal) {
    publicProposal = gemmaProposal.content;
  } else {
    publicProposal =
      `Estimado Comité de Evaluación de ${safe.targetClient},\n\n` +
      `Por medio de la presente, ${safe.consultantName} (${safe.projectRole}) presenta la propuesta técnica para la modernización de su plataforma transaccional, contemplando una inversión de ${safe.estimatedHours} horas de ingeniería especializada a una tarifa de $${safe.proposedHourlyRateUSD} USD/hora ($${metrics.totalPrice.toLocaleString("en-US")} USD totales).\n\n` +
      `Alcance Técnico Comprometido:\n` +
      safe.sanitizedDeliverables.map((d, i) => `${i + 1}. ${d}`).join("\n") +
      `\n\nExperiencia Relevante Verificada:\n` +
      `${safe.sanitizedAchievements}\n\n` +
      `Quedamos a su disposición para iniciar la fase de arquitectura detallada.`;
  }

  // Paso E: Auditoría determinista post-generación
  const leakAudit = auditLeaks(publicProposal, profile);
  const numberCheck = checkNumberConsistency(strategyNote, [
    profile.internalHourlyCostUSD,
    profile.proposedHourlyRateUSD,
    profile.estimatedHours,
    metrics.totalCost,
    metrics.totalPrice,
    metrics.grossProfit,
    metrics.marginPct,
    metrics.minAcceptableTotal,
    30,
    4,
  ]);

  const elapsedMs = Date.now() - t0;
  const isLive = Boolean(gemmaExtract?.live && gemmaStrategy?.live && gemmaProposal?.live);

  return {
    model: GEMMA_MODEL,
    liveInference: isLive,
    engineLabel: isLive ? `${GEMMA_MODEL} (Ollama en vivo · ${elapsedMs} ms)` : `${GEMMA_MODEL} (Modo instantáneo)`,
    elapsedMs,
    metrics,
    extracted,
    routed,
    strategyNote,
    publicProposal,
    audit: {
      leakAudit,
      numberCheck,
    },
  };
}

// ============================================================================
// 4. SERVIDOR HTTP
// ============================================================================
const server = http.createServer(async (req, res) => {
  if (req.method === "POST" && req.url === "/api/quote") {
    let body = "";
    req.on("data", chunk => { body += chunk; });
    req.on("end", async () => {
      try {
        const profile = JSON.parse(body);
        const result = await runGemmaPipeline(profile);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(result, null, 2));
      } catch (err) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: String(err) }));
      }
    });
    return;
  }

  const filePath = path.join(__dirname, "public", req.url === "/" ? "index.html" : req.url);
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    const ext = path.extname(filePath);
    const mime = ext === ".html" ? "text/html; charset=utf-8" : ext === ".css" ? "text/css" : "application/javascript";
    res.writeHead(200, { "Content-Type": mime });
    res.end(fs.readFileSync(filePath));
  } else {
    res.writeHead(404);
    res.end("Not found");
  }
});

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  server.listen(PORT, () => {
    console.log(`CotizaSeguro (100% Gemma 4) corriendo en http://localhost:${PORT}`);
  });
}
