import test from "node:test";
import assert from "node:assert/strict";
import {
  calculateMargin,
  buildPublicProposalPayload,
  auditLeaks,
  checkNumberConsistency,
} from "./server.mjs";

const sampleProfile = {
  consultantName: "Adrián Catalán · Arquitectura IA",
  targetClient: "Seguros Universales S.A.",
  projectRole: "Consultoría de Ingeniería de Software",
  internalHourlyCostUSD: 28,
  proposedHourlyRateUSD: 65,
  estimatedHours: 200,
  ndaClientReference: "Banco Industrial",
  teamAchievements:
    "En Banco Industrial migramos 40 microservicios críticos con latencia menor a 120ms, manteniendo nuestro costo interno de $28/h y logrando 99.98% de disponibilidad.",
  rfpText: "Construir pasarela OAuth2 y pruebas a 500 RPS.",
};

test("1. calculateMargin calcula costo interno, utilidad y margen exacto en código determinista", () => {
  const m = calculateMargin(sampleProfile);
  assert.equal(m.totalCost, 5600);
  assert.equal(m.totalPrice, 13000);
  assert.equal(m.grossProfit, 7400);
  assert.equal(m.marginPct, 56.9);
  assert.equal(m.band, "alto_margen");
});

test("2. buildPublicProposalPayload elimina campos secretos y redacta cliente NDA + costo hora", () => {
  const routed = buildPublicProposalPayload(sampleProfile, [
    "Pasarela API OAuth 2.0",
    "Módulo heredado de Industrial por $5,600",
  ]);
  const serialized = JSON.stringify(routed.payload);

  assert.equal("internalHourlyCostUSD" in routed.payload, false);
  assert.equal("ndaClientReference" in routed.payload, false);
  assert.equal(serialized.includes("28"), false);
  assert.equal(serialized.includes("5,600"), false);
  assert.equal(serialized.toLowerCase().includes("industrial"), false);
  assert.equal(serialized.includes("[CLIENTE_FINANCIERO_NDA]"), true);
  assert.equal(serialized.includes("[COSTO_INTERNO_RESERVADO]"), true);
});

test("3. auditLeaks detecta inmediatamente si una propuesta contiene tokens NDA o costo interno", () => {
  const cleanCheck = auditLeaks(
    "Propuesta para Seguros Universales por 200 horas a $65 USD/h con experiencia en [CLIENTE_FINANCIERO_NDA].",
    sampleProfile
  );
  assert.equal(cleanCheck.passed, true);

  const leakyCheck = auditLeaks(
    "En Industrial nuestro costo interno fue de $28 por hora.",
    sampleProfile
  );
  assert.equal(leakyCheck.passed, false);
  assert.equal(leakyCheck.leaks.length, 2);
});

test("4. checkNumberConsistency detecta cifras alucinadas que no provienen de las heurísticas", () => {
  const ok = checkNumberConsistency(
    "Tu precio total es $13,000 con un margen de 56.9% y piso de $8,000.",
    [13000, 56.9, 8000]
  );
  assert.equal(ok.consistent, true);

  const hallucinated = checkNumberConsistency(
    "Tu precio total es $13,000 con un margen inventado de 74.2%.",
    [13000, 56.9, 8000]
  );
  assert.equal(hallucinated.consistent, false);
  assert.deepEqual(hallucinated.unverifiedNumbers, ["74.2"]);
});
