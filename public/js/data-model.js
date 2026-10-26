export const DATASET_SCHEMA_VERSION = "1.0.0";
export const DEFAULT_PAGE_SIZE = 50;

const numberFormatter = new Intl.NumberFormat("pt-BR");
const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "long",
  timeStyle: "short",
  timeZone: "America/Araguaina",
});

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function validateDataset(dataset) {
  assert(isPlainObject(dataset), "O dataset deve ser um objeto.");
  assert(dataset.versao_schema === DATASET_SCHEMA_VERSION, "Versão do dataset incompatível.");
  assert(isPlainObject(dataset.candidato), "Dados do candidato ausentes.");
  assert(isPlainObject(dataset.eleicao), "Dados da eleição ausentes.");
  assert(isPlainObject(dataset.resumo), "Resumo ausente.");
  assert(isPlainObject(dataset.fonte), "Proveniência ausente.");
  assert(Array.isArray(dataset.registros), "A lista de registros é inválida.");

  for (const field of ["numero", "nome", "cargo"]) {
    assert(typeof dataset.candidato[field] === "string" && dataset.candidato[field], `Candidato: ${field} inválido.`);
  }
  assert(Number.isInteger(dataset.eleicao.ano), "Ano da eleição inválido.");
  assert(Number.isInteger(dataset.eleicao.turno), "Turno inválido.");
  assert(typeof dataset.eleicao.uf === "string", "UF inválida.");
  assert(typeof dataset.fonte.url === "string" && dataset.fonte.url.startsWith("https://"), "URL oficial inválida.");

  let totalVotes = 0;
  let aggregated = 0;
  const cities = new Set();
  dataset.registros.forEach((record, index) => {
    assert(isPlainObject(record), `Registro ${index + 1} inválido.`);
    for (const field of ["cidade", "codigo_municipio_tse", "zona", "secao"]) {
      assert(typeof record[field] === "string" && record[field], `Registro ${index + 1}: ${field} inválido.`);
    }
    assert(Array.isArray(record.secoes_agregadas), `Registro ${index + 1}: agregações inválidas.`);
    assert(record.secoes_agregadas.every((section) => typeof section === "string"), `Registro ${index + 1}: seção agregada inválida.`);
    assert(Number.isInteger(record.votos) && record.votos >= 0, `Registro ${index + 1}: votos inválidos.`);
    totalVotes += record.votos;
    aggregated += record.secoes_agregadas.length > 0 ? 1 : 0;
    cities.add(record.codigo_municipio_tse);
  });

  const expectedSummary = {
    registros: dataset.registros.length,
    municipios: cities.size,
    registros_com_secao_agregada: aggregated,
    total_votos: totalVotes,
  };
  for (const [field, value] of Object.entries(expectedSummary)) {
    assert(dataset.resumo[field] === value, `Resumo incompatível: ${field}.`);
  }
  return dataset;
}

export async function fetchDataset(url, fetchImplementation = globalThis.fetch) {
  assert(typeof fetchImplementation === "function", "Fetch indisponível neste navegador.");
  const response = await fetchImplementation(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Falha HTTP ${response.status} ao carregar os dados.`);
  }
  let dataset;
  try {
    dataset = await response.json();
  } catch (error) {
    throw new Error("O arquivo de dados não contém JSON válido.", { cause: error });
  }
  return validateDataset(dataset);
}

export function paginate(records, requestedPage, pageSize = DEFAULT_PAGE_SIZE) {
  assert(Array.isArray(records), "Registros devem ser uma lista.");
  assert(Number.isInteger(pageSize) && pageSize > 0, "Tamanho de página inválido.");
  const total = records.length;
  if (total === 0) {
    return { items: [], page: 0, totalPages: 0, start: 0, end: 0, total };
  }
  const totalPages = Math.ceil(total / pageSize);
  const page = Math.min(Math.max(Number.isInteger(requestedPage) ? requestedPage : 1, 1), totalPages);
  const offset = (page - 1) * pageSize;
  const items = records.slice(offset, offset + pageSize);
  return {
    items,
    page,
    totalPages,
    start: offset + 1,
    end: offset + items.length,
    total,
  };
}

export function formatNumber(value) {
  return numberFormatter.format(value);
}

export function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Data não informada" : dateFormatter.format(date);
}

export function aggregatedSectionsLabel(sections) {
  return sections.length > 0 ? sections.join(", ") : "Não";
}

export function normalizeSearchText(value) {
  return String(value ?? "")
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLocaleLowerCase("pt-BR")
    .trim();
}

function matchesCitySearch(record, citySearch) {
  const search = normalizeSearchText(citySearch);
  return !search || normalizeSearchText(record.cidade).includes(search);
}

export function filterRecords(records, filters = {}) {
  const { citySearch = "", cityCode = "", zone = "", section = "" } = filters;
  return records.filter((record) => (
    matchesCitySearch(record, citySearch)
    && (!cityCode || record.codigo_municipio_tse === cityCode)
    && (!zone || record.zona === zone)
    && (!section || record.secao === section)
  ));
}

export function summarizeRecords(records) {
  return {
    records: records.length,
    cities: new Set(records.map((record) => record.codigo_municipio_tse)).size,
    votes: records.reduce((total, record) => total + record.votos, 0),
  };
}

export function availableCities(records, citySearch = "") {
  const cities = new Map();
  for (const record of records) {
    if (matchesCitySearch(record, citySearch)) {
      cities.set(record.codigo_municipio_tse, record.cidade);
    }
  }
  return [...cities.entries()]
    .map(([value, label]) => ({ value, label }))
    .sort((left, right) => left.label.localeCompare(right.label, "pt-BR", { sensitivity: "base" }));
}

export function availableZones(records, cityCode = "", citySearch = "") {
  const zones = new Set(
    records
      .filter((record) => (
        matchesCitySearch(record, citySearch)
        && (!cityCode || record.codigo_municipio_tse === cityCode)
      ))
      .map((record) => record.zona),
  );
  return [...zones].sort((left, right) => Number(left) - Number(right));
}

export function availableSections(records, cityCode = "", zone = "", citySearch = "") {
  const sections = new Set(
    records
      .filter((record) => (
        matchesCitySearch(record, citySearch)
        && (!cityCode || record.codigo_municipio_tse === cityCode)
        && (!zone || record.zona === zone)
      ))
      .map((record) => record.secao),
  );
  return [...sections].sort((left, right) => Number(left) - Number(right));
}

export function normalizeFilters(records, candidate = {}) {
  const citySearch = String(candidate.citySearch ?? "").trim();
  const cityValues = new Set(availableCities(records, citySearch).map((option) => option.value));
  const cityCode = cityValues.has(candidate.cityCode) ? candidate.cityCode : "";
  const zoneValues = new Set(availableZones(records, cityCode, citySearch));
  const zone = zoneValues.has(candidate.zone) ? candidate.zone : "";
  const sectionValues = new Set(availableSections(records, cityCode, zone, citySearch));
  const section = sectionValues.has(candidate.section) ? candidate.section : "";
  return { citySearch, cityCode, zone, section };
}

export function hasActiveFilters(filters) {
  return Boolean(filters.citySearch || filters.cityCode || filters.zone || filters.section);
}

export function filtersFromSearchParams(searchParams) {
  const params = searchParams instanceof URLSearchParams
    ? searchParams
    : new URLSearchParams(searchParams);
  return {
    citySearch: params.get("q") || "",
    cityCode: params.get("cidade") || "",
    zone: params.get("zona") || "",
    section: params.get("secao") || "",
  };
}

export function filtersToSearchParams(filters) {
  const params = new URLSearchParams();
  if (filters.citySearch) params.set("q", filters.citySearch);
  if (filters.cityCode) params.set("cidade", filters.cityCode);
  if (filters.zone) params.set("zona", filters.zone);
  if (filters.section) params.set("secao", filters.section);
  return params;
}
