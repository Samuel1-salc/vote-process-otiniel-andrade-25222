import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  aggregatedSectionsLabel,
  availableCities,
  availableSections,
  availableZones,
  fetchDataset,
  filterRecords,
  filtersFromSearchParams,
  filtersToSearchParams,
  formatNumber,
  hasActiveFilters,
  normalizeFilters,
  normalizeSearchText,
  paginate,
  summarizeRecords,
  validateDataset,
} from "../../public/js/data-model.js";

const datasetPath = new URL("../../public/data/votos_otoniel_25222_TO_2026.json", import.meta.url);

async function officialDataset() {
  return JSON.parse(await readFile(datasetPath, "utf8"));
}

test("valida o dataset oficial e suas métricas", async () => {
  const dataset = validateDataset(await officialDataset());
  assert.equal(dataset.resumo.registros, 1225);
  assert.equal(dataset.resumo.municipios, 89);
  assert.equal(dataset.resumo.registros_com_secao_agregada, 19);
  assert.equal(dataset.resumo.total_votos, 7180);
});

test("pagina 1.225 registros em blocos de 50", async () => {
  const records = (await officialDataset()).registros;
  const first = paginate(records, 1, 50);
  const last = paginate(records, 25, 50);
  assert.equal(first.items.length, 50);
  assert.deepEqual([first.start, first.end, first.totalPages], [1, 50, 25]);
  assert.equal(last.items.length, 25);
  assert.deepEqual([last.start, last.end], [1201, 1225]);
});

test("limita páginas fora da faixa", () => {
  const records = Array.from({ length: 70 }, (_, index) => index);
  assert.equal(paginate(records, -5, 50).page, 1);
  assert.equal(paginate(records, 99, 50).page, 2);
});

test("representa corretamente uma lista vazia", () => {
  assert.deepEqual(paginate([], 1, 50), {
    items: [], page: 0, totalPages: 0, start: 0, end: 0, total: 0,
  });
});

test("formata votos e seções agregadas para pt-BR", () => {
  assert.equal(formatNumber(7180), "7.180");
  assert.equal(aggregatedSectionsLabel([]), "Não");
  assert.equal(aggregatedSectionsLabel(["57", "58"]), "57, 58");
});

test("rejeita versão de schema incompatível", async () => {
  const dataset = await officialDataset();
  dataset.versao_schema = "2.0.0";
  assert.throws(() => validateDataset(dataset), /Versão do dataset incompatível/);
});

test("preserva textos semelhantes a HTML como texto comum", async () => {
  const dataset = await officialDataset();
  dataset.registros[0].cidade = "<img src=x onerror=alert(1)>";
  assert.equal(validateDataset(dataset).registros[0].cidade, "<img src=x onerror=alert(1)>");
});

test("trata erro HTTP ao buscar o dataset", async () => {
  const fakeFetch = async () => ({ ok: false, status: 404 });
  await assert.rejects(fetchDataset("/missing.json", fakeFetch), /Falha HTTP 404/);
});

test("trata resposta JSON inválida", async () => {
  const fakeFetch = async () => ({
    ok: true,
    status: 200,
    json: async () => { throw new SyntaxError("invalid"); },
  });
  await assert.rejects(fetchDataset("/invalid.json", fakeFetch), /não contém JSON válido/);
});

test("sem filtros preserva as métricas oficiais", async () => {
  const records = (await officialDataset()).registros;
  const filtered = filterRecords(records, {});
  assert.deepEqual(summarizeRecords(filtered), { records: 1225, cities: 89, votes: 7180 });
  assert.equal(filtered.length, records.length);
  assert.notEqual(filtered, records);
});

test("filtra Palmas pela chave municipal estável", async () => {
  const records = (await officialDataset()).registros;
  const palmas = availableCities(records).find((city) => city.label === "PALMAS");
  assert.ok(palmas);
  const filtered = filterRecords(records, { cityCode: palmas.value });
  assert.deepEqual(summarizeRecords(filtered), { records: 359, cities: 1, votes: 574 });
});

test("filtra Natividade e o recorte da seção 81", async () => {
  const records = (await officialDataset()).registros;
  const natividade = availableCities(records).find((city) => city.label === "NATIVIDADE");
  assert.ok(natividade);
  const cityRecords = filterRecords(records, { cityCode: natividade.value });
  assert.deepEqual(summarizeRecords(cityRecords), { records: 27, cities: 1, votes: 85 });
  const sectionRecords = filterRecords(records, {
    cityCode: natividade.value,
    zone: "19",
    section: "81",
  });
  assert.deepEqual(summarizeRecords(sectionRecords), { records: 1, cities: 1, votes: 4 });
});

test("filtros diretos inexistentes retornam resultado vazio", async () => {
  const records = (await officialDataset()).registros;
  assert.deepEqual(filterRecords(records, { cityCode: "00000" }), []);
});

test("opções dependentes respeitam cidade e zona", async () => {
  const records = (await officialDataset()).registros;
  const natividade = availableCities(records).find((city) => city.label === "NATIVIDADE");
  assert.ok(natividade);
  assert.deepEqual(availableZones(records, natividade.value), ["19"]);
  const sections = availableSections(records, natividade.value, "19");
  assert.equal(sections.length, 27);
  assert.ok(sections.includes("81"));
  assert.deepEqual([...sections].sort((a, b) => Number(a) - Number(b)), sections);
});

test("normalização limpa filtros dependentes incompatíveis", async () => {
  const records = (await officialDataset()).registros;
  const natividade = availableCities(records).find((city) => city.label === "NATIVIDADE");
  assert.ok(natividade);
  assert.deepEqual(
    normalizeFilters(records, { cityCode: natividade.value, zone: "999", section: "81" }),
    { citySearch: "", cityCode: natividade.value, zone: "", section: "81" },
  );
  assert.deepEqual(
    normalizeFilters(records, { cityCode: "inexistente", zone: "999", section: "999" }),
    { citySearch: "", cityCode: "", zone: "", section: "" },
  );
});

test("serializa e restaura filtros válidos na URL", () => {
  const filters = { citySearch: "natividade", cityCode: "94811", zone: "19", section: "81" };
  const params = filtersToSearchParams(filters);
  assert.equal(params.toString(), "q=natividade&cidade=94811&zona=19&secao=81");
  assert.deepEqual(filtersFromSearchParams(params), filters);
  assert.equal(hasActiveFilters(filters), true);
  assert.equal(hasActiveFilters({ citySearch: "", cityCode: "", zone: "", section: "" }), false);
});

test("pesquisa cidade por trecho, sem diferenciar caixa ou acento", async () => {
  const records = (await officialDataset()).registros;
  const partial = filterRecords(records, { citySearch: "  PALm  " });
  assert.deepEqual(summarizeRecords(partial), { records: 361, cities: 3, votes: 576 });
  const palmas = filterRecords(records, { citySearch: "  PALMAS  " });
  assert.deepEqual(summarizeRecords(palmas), { records: 359, cities: 1, votes: 574 });
  const saoCities = availableCities(records, "sao");
  assert.ok(saoCities.length > 0);
  assert.ok(saoCities.every((city) => normalizeSearchText(city.label).includes("sao")));
});

test("pesquisa textual funciona junto com cidade, zona e seção", async () => {
  const records = (await officialDataset()).registros;
  const result = filterRecords(records, {
    citySearch: "nativi",
    cityCode: "94811",
    zone: "19",
    section: "81",
  });
  assert.deepEqual(summarizeRecords(result), { records: 1, cities: 1, votes: 4 });
  assert.deepEqual(availableZones(records, "", "nativi"), ["19"]);
  assert.ok(availableSections(records, "", "19", "nativi").includes("81"));
});

test("pesquisa incompatível limpa filtros dependentes", async () => {
  const records = (await officialDataset()).registros;
  assert.deepEqual(
    normalizeFilters(records, {
      citySearch: "palmas",
      cityCode: "94811",
      zone: "19",
      section: "81",
    }),
    { citySearch: "palmas", cityCode: "", zone: "", section: "" },
  );
});

test("filtragem não altera o dataset original", async () => {
  const records = (await officialDataset()).registros;
  const snapshot = JSON.stringify(records);
  filterRecords(records, { zone: "19", section: "81" });
  availableCities(records);
  availableZones(records, "94811");
  availableSections(records, "94811", "19");
  assert.equal(JSON.stringify(records), snapshot);
});
