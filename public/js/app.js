import {
  DEFAULT_PAGE_SIZE,
  aggregatedSectionsLabel,
  availableCities,
  availableSections,
  availableZones,
  fetchDataset,
  filterRecords,
  filtersFromSearchParams,
  filtersToSearchParams,
  formatDate,
  formatNumber,
  hasActiveFilters,
  normalizeFilters,
  paginate,
  summarizeRecords,
} from "./data-model.js";

const DATASET_URL = "./data/votos_otoniel_25222_TO_2026.json";

const elements = {
  status: document.querySelector("#app-status"),
  summary: document.querySelector("#summary-section"),
  data: document.querySelector("#data-section"),
  source: document.querySelector("#source-section"),
  empty: document.querySelector("#empty-state"),
  error: document.querySelector("#error-state"),
  retry: document.querySelector("#retry-button"),
  candidateName: document.querySelector("#candidate-name"),
  candidateContext: document.querySelector("#candidate-context"),
  electionState: document.querySelector("#election-state"),
  electionYear: document.querySelector("#election-year"),
  summaryVotes: document.querySelector("#summary-votes"),
  summaryCities: document.querySelector("#summary-cities"),
  summaryRecords: document.querySelector("#summary-records"),
  summaryAggregated: document.querySelector("#summary-aggregated"),
  citySearch: document.querySelector("#city-search"),
  cityFilter: document.querySelector("#city-filter"),
  zoneFilter: document.querySelector("#zone-filter"),
  sectionFilter: document.querySelector("#section-filter"),
  clearFilters: document.querySelector("#clear-filters"),
  clearEmptyFilters: document.querySelector("#clear-empty-filters"),
  filteredSummaryTitle: document.querySelector("#filtered-summary-title"),
  activeFilterDescription: document.querySelector("#active-filter-description"),
  filteredVotes: document.querySelector("#filtered-votes"),
  filteredRecords: document.querySelector("#filtered-records"),
  filteredCities: document.querySelector("#filtered-cities"),
  filterEmpty: document.querySelector("#filter-empty-state"),
  tableCard: document.querySelector("#table-card"),
  votesBody: document.querySelector("#votes-body"),
  previous: document.querySelector("#previous-page"),
  next: document.querySelector("#next-page"),
  pageRange: document.querySelector("#page-range"),
  pageNumber: document.querySelector("#page-number"),
  sourceName: document.querySelector("#source-name"),
  sourceLink: document.querySelector("#source-link"),
  generatedAt: document.querySelector("#generated-at"),
  contractVersion: document.querySelector("#contract-version"),
  schemaVersion: document.querySelector("#schema-version"),
};

const state = {
  dataset: null,
  filteredRecords: [],
  filters: { citySearch: "", cityCode: "", zone: "", section: "" },
  page: 1,
};

function hideAllPanels() {
  for (const panel of [elements.summary, elements.data, elements.source, elements.empty, elements.error]) {
    panel.hidden = true;
  }
}

function setApplicationState(name, message) {
  hideAllPanels();
  elements.status.textContent = message;
  elements.status.dataset.state = name;
  if (name === "ready") {
    elements.summary.hidden = false;
    elements.data.hidden = false;
    elements.source.hidden = false;
  } else if (name === "empty") {
    elements.summary.hidden = false;
    elements.source.hidden = false;
    elements.empty.hidden = false;
  } else if (name === "error") {
    elements.error.hidden = false;
  }
}

function setText(element, value) {
  element.textContent = String(value);
}

function renderHeader(dataset) {
  const { candidato, eleicao } = dataset;
  setText(elements.candidateName, `${candidato.nome} — ${candidato.numero}`);
  setText(elements.electionState, eleicao.uf);
  setText(elements.electionYear, eleicao.ano);
  setText(
    elements.candidateContext,
    `${candidato.cargo} · ${eleicao.uf} · Eleições ${eleicao.ano} · ${eleicao.turno}º turno`,
  );
  document.title = `Consulta de votação — ${candidato.nome}`;
}

function renderSummary(dataset) {
  const summary = dataset.resumo;
  setText(elements.summaryVotes, formatNumber(summary.total_votos));
  setText(elements.summaryCities, formatNumber(summary.municipios));
  setText(elements.summaryRecords, formatNumber(summary.registros));
  setText(elements.summaryAggregated, formatNumber(summary.registros_com_secao_agregada));
}

function renderSource(dataset) {
  setText(elements.sourceName, dataset.fonte.nome);
  setText(elements.generatedAt, formatDate(dataset.gerado_em));
  setText(elements.contractVersion, dataset.versao_contrato);
  setText(elements.schemaVersion, dataset.versao_schema);
  elements.sourceLink.href = dataset.fonte.url;
}

function createCell(value, className = "") {
  const cell = document.createElement("td");
  cell.textContent = value;
  if (className) cell.className = className;
  return cell;
}

function populateSelect(select, options, placeholder, selectedValue) {
  select.replaceChildren();
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = placeholder;
  select.append(defaultOption);
  for (const option of options) {
    const element = document.createElement("option");
    if (typeof option === "string") {
      element.value = option;
      element.textContent = option;
    } else {
      element.value = option.value;
      element.textContent = option.label;
    }
    select.append(element);
  }
  select.value = selectedValue;
}

function renderFilterControls() {
  const records = state.dataset.registros;
  elements.citySearch.value = state.filters.citySearch;
  populateSelect(
    elements.cityFilter,
    availableCities(records, state.filters.citySearch),
    "Todas as cidades",
    state.filters.cityCode,
  );
  populateSelect(
    elements.zoneFilter,
    availableZones(records, state.filters.cityCode, state.filters.citySearch),
    "Todas as zonas",
    state.filters.zone,
  );
  populateSelect(
    elements.sectionFilter,
    availableSections(
      records,
      state.filters.cityCode,
      state.filters.zone,
      state.filters.citySearch,
    ),
    "Todas as seções",
    state.filters.section,
  );
  elements.clearFilters.disabled = !hasActiveFilters(state.filters);
}

function filterDescription() {
  const descriptions = [];
  if (state.filters.citySearch) descriptions.push(`pesquisa: “${state.filters.citySearch}”`);
  if (state.filters.cityCode) {
    descriptions.push(`cidade: ${elements.cityFilter.selectedOptions[0].textContent}`);
  }
  if (state.filters.zone) descriptions.push(`zona: ${state.filters.zone}`);
  if (state.filters.section) descriptions.push(`seção: ${state.filters.section}`);
  return descriptions.length ? descriptions.join(" · ") : "Nenhum filtro aplicado";
}

function renderFilteredSummary() {
  const summary = summarizeRecords(state.filteredRecords);
  setText(
    elements.filteredSummaryTitle,
    hasActiveFilters(state.filters) ? "Resultado filtrado" : "Todos os registros",
  );
  setText(elements.activeFilterDescription, filterDescription());
  setText(elements.filteredVotes, formatNumber(summary.votes));
  setText(elements.filteredRecords, formatNumber(summary.records));
  setText(elements.filteredCities, formatNumber(summary.cities));
}

function syncFiltersToUrl() {
  const params = filtersToSearchParams(state.filters);
  const query = params.toString();
  const nextUrl = `${window.location.pathname}${query ? `?${query}` : ""}${window.location.hash}`;
  window.history.replaceState({}, "", nextUrl);
}

function applyFilters({ syncUrl = true } = {}) {
  state.filters = normalizeFilters(state.dataset.registros, state.filters);
  state.filteredRecords = filterRecords(state.dataset.registros, state.filters);
  state.page = 1;
  renderFilterControls();
  renderFilteredSummary();
  elements.filterEmpty.hidden = state.filteredRecords.length > 0;
  elements.tableCard.hidden = state.filteredRecords.length === 0;
  if (state.filteredRecords.length > 0) renderTablePage();
  if (syncUrl) syncFiltersToUrl();
}

function clearAllFilters() {
  state.filters = { citySearch: "", cityCode: "", zone: "", section: "" };
  applyFilters();
}

function renderTablePage() {
  const page = paginate(state.filteredRecords, state.page, DEFAULT_PAGE_SIZE);
  state.page = page.page;
  elements.votesBody.replaceChildren();

  const fragment = document.createDocumentFragment();
  for (const record of page.items) {
    const row = document.createElement("tr");
    row.append(createCell(record.cidade));
    row.append(createCell(record.zona));
    row.append(createCell(record.secao));
    const aggregatedCell = createCell(aggregatedSectionsLabel(record.secoes_agregadas));
    aggregatedCell.className = record.secoes_agregadas.length ? "aggregate-pill-cell" : "muted-cell";
    if (record.secoes_agregadas.length) {
      const pill = document.createElement("span");
      pill.className = "aggregate-pill";
      pill.textContent = aggregatedCell.textContent;
      aggregatedCell.replaceChildren(pill);
    }
    row.append(aggregatedCell);
    row.append(createCell(formatNumber(record.votos), "numeric-column"));
    fragment.append(row);
  }
  elements.votesBody.append(fragment);

  setText(elements.pageRange, `Exibindo ${formatNumber(page.start)}–${formatNumber(page.end)} de ${formatNumber(page.total)}`);
  setText(elements.pageNumber, `Página ${formatNumber(page.page)} de ${formatNumber(page.totalPages)}`);
  elements.previous.disabled = page.page <= 1;
  elements.next.disabled = page.page >= page.totalPages;
}

async function loadData() {
  state.dataset = null;
  state.page = 1;
  setApplicationState("loading", "Carregando dados da votação…");
  try {
    const dataset = await fetchDataset(DATASET_URL);
    state.dataset = dataset;
    renderHeader(dataset);
    renderSummary(dataset);
    renderSource(dataset);
    if (dataset.registros.length === 0) {
      setApplicationState("empty", "Dados carregados, sem registros para exibir.");
      return;
    }
    state.filters = normalizeFilters(
      dataset.registros,
      filtersFromSearchParams(window.location.search),
    );
    applyFilters();
    setApplicationState("ready", "Dados oficiais carregados e validados.");
  } catch (error) {
    console.error("Falha ao carregar a votação:", error);
    setApplicationState("error", "Não foi possível carregar os dados da votação.");
  }
}

elements.previous.addEventListener("click", () => {
  state.page -= 1;
  renderTablePage();
});

elements.next.addEventListener("click", () => {
  state.page += 1;
  renderTablePage();
});

elements.cityFilter.addEventListener("change", () => {
  state.filters = { ...state.filters, cityCode: elements.cityFilter.value };
  applyFilters();
});

elements.citySearch.addEventListener("input", () => {
  state.filters = { ...state.filters, citySearch: elements.citySearch.value };
  applyFilters();
});

elements.zoneFilter.addEventListener("change", () => {
  state.filters = { ...state.filters, zone: elements.zoneFilter.value };
  applyFilters();
});

elements.sectionFilter.addEventListener("change", () => {
  state.filters = { ...state.filters, section: elements.sectionFilter.value };
  applyFilters();
});

elements.clearFilters.addEventListener("click", clearAllFilters);
elements.clearEmptyFilters.addEventListener("click", clearAllFilters);

elements.retry.addEventListener("click", loadData);

loadData();
