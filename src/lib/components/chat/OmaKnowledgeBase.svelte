<!-- ---------------------------------------------------------------------------
  File:        OmaKnowledgeBase.svelte
  Description: OMA Knowledge Base modal — plant document browser showing the
               3-level OKF folder structure (A > B > C) with priority indicators.
               Read-only for users; role-based access handled by backend.
  Author:      Vasu Chukka
  --------------------------------------------------------------------------- -->
<script lang="ts">
	import { fade, slide } from 'svelte/transition';
	import { showOmaKnowledgeBase } from '$lib/stores/omaKnowledgeBase';
	import Database          from '$lib/components/icons/Database.svelte';
	import EnergySolarPlant from '$lib/components/icons/EnergySolarPlant.svelte';
	import Folder     from '$lib/components/icons/Folder.svelte';
	import FolderOpen from '$lib/components/icons/FolderOpen.svelte';
	import Document   from '$lib/components/icons/Document.svelte';
	import ChevronRight from '$lib/components/icons/ChevronRight.svelte';
	import ArrowLeft  from '$lib/components/icons/ArrowLeft.svelte';
	import XMark      from '$lib/components/icons/XMark.svelte';

	// ── Types ──────────────────────────────────────────────────────────────────

	type Plant = {
		id: string;
		name: string;
	};

	type KBFile = {
		id: string;
		name: string;
		priority: 1 | 2 | 3;
	};

	type FolderB = {
		id: string;
		name: string;
		files: KBFile[];
	};

	type FolderA = {
		id: string;
		name: string;
		subfolders: FolderB[];
	};

	// ── Plant list ────────────────────────────────────────────────────────────

	const PLANTS: Plant[] = [
		{ id: 'baalberge',     name: 'Baalberge' },
		{ id: 'bernburg',      name: 'Bernburg' },
		{ id: 'bubenreuth',    name: 'Bubenreuth' },
		{ id: 'cottbus',       name: 'Cottbus' },
		{ id: 'ditfurt',       name: 'Ditfurt' },
		{ id: 'fuerstenwalde', name: 'Fürstenwalde' },
		{ id: 'gahro',         name: 'Gahro' },
		{ id: 'massbach',      name: 'Maßbach' },
	];

	// ── Knowledge Base data (shared structure across all plants) ───────────────

	const KB: FolderA[] = [
		{
			id: 'a01', name: '01 Projektentwicklung',
			subfolders: [
				{ id: 'b01_01', name: '01 Flaechensicherung', files: [
					{ id: 'c1', name: 'Vertraege', priority: 3 },
					{ id: 'c2', name: 'Grundbuchauszuge', priority: 3 },
					{ id: 'c3', name: 'Flurkarte', priority: 3 },
				]},
				{ id: 'b01_02', name: '02 Baurecht', files: [
					{ id: 'c4', name: 'Baugenehmigung', priority: 3 },
					{ id: 'c5', name: 'FNP', priority: 3 },
					{ id: 'c6', name: 'B-Plan', priority: 2 },
					{ id: 'c7', name: 'Weitere Genehmigungen', priority: 3 },
					{ id: 'c8', name: 'Verguetungsvoraussetzungen', priority: 3 },
				]},
				{ id: 'b01_03', name: '03 Bauvorbereitung', files: [
					{ id: 'c9',  name: 'Medienplaene', priority: 3 },
					{ id: 'c10', name: 'Verkehrsrechtliche Genehmigungen', priority: 3 },
					{ id: 'c11', name: 'Kampfmittelfreigabe', priority: 3 },
					{ id: 'c12', name: 'Altlastendokumentation', priority: 3 },
					{ id: 'c13', name: 'Sonstige Genehmigungen', priority: 3 },
					{ id: 'c14', name: 'Schachtscheine', priority: 3 },
				]},
				{ id: 'b01_04', name: '04 Netzanschluss', files: [
					{ id: 'c15', name: 'Netzeinspeisezusage', priority: 3 },
					{ id: 'c16', name: 'Netzparameter', priority: 1 },
					{ id: 'c17', name: 'Technische Regeln', priority: 1 },
					{ id: 'c18', name: 'Netzanschlussvertrag', priority: 3 },
					{ id: 'c19', name: 'Fertigstellungsunterlagen', priority: 3 },
					{ id: 'c20', name: 'Inbetriebnahmeunterlagen', priority: 2 },
					{ id: 'c21', name: 'Messkonzept', priority: 1 },
				]},
				{ id: 'b01_05', name: '05 Gutachten', files: [
					{ id: 'c22', name: 'Baugrundgutachten', priority: 3 },
					{ id: 'c23', name: 'Ertragsgutachten', priority: 1 },
					{ id: 'c24', name: 'Zertifizierung', priority: 1 },
					{ id: 'c25', name: 'Schallgutachten', priority: 2 },
					{ id: 'c26', name: 'Umweltgutachten', priority: 3 },
					{ id: 'c27', name: 'Baufortschrittskontrolle', priority: 3 },
				]},
			]
		},
		{
			id: 'a02', name: '02 Technische Anlagenplanung',
			subfolders: [
				{ id: 'b02_01', name: '01 CAD Datei', files: [] },
				{ id: 'b02_02', name: '02 Allgemein', files: [
					{ id: 'c28', name: 'Anlagenbeschreibung / Technical Proposal', priority: 2 },
					{ id: 'c29', name: 'Standort', priority: 2 },
					{ id: 'c30', name: 'Projektbeteiligtenliste', priority: 3 },
				]},
				{ id: 'b02_03', name: '03 Grundlagentabellen', files: [
					{ id: 'c31', name: 'System Design Chart', priority: 1 },
					{ id: 'c32', name: 'Materialliste', priority: 1 },
					{ id: 'c33', name: 'Dimensionierung Kabel und Sicherungen', priority: 3 },
					{ id: 'c34', name: 'Oberschwingungsbericht', priority: 3 },
					{ id: 'c35', name: 'Datenpunktliste', priority: 1 },
				]},
			]
		},
		{
			id: 'a03', name: '03 Plaene',
			subfolders: [
				{ id: 'b03_00', name: '00 Projektentwicklung', files: [
					{ id: 'c36', name: 'Lageplan', priority: 2 },
					{ id: 'c37', name: 'Flurstuecksplan', priority: 2 },
					{ id: 'c38', name: 'Medienplan', priority: 2 },
					{ id: 'c39', name: 'Trassenplan', priority: 1 },
				]},
				{ id: 'b03_01', name: '01 Gruendung', files: [
					{ id: 'c40', name: 'Rammplan', priority: 3 },
					{ id: 'c41', name: 'Vermesser Daten', priority: 3 },
					{ id: 'c42', name: 'Komponenten Befestigung', priority: 3 },
				]},
				{ id: 'b03_02', name: '02 Module', files: [
					{ id: 'c43', name: 'Modulplan', priority: 1 },
					{ id: 'c44', name: 'Modultypplan', priority: 1 },
				]},
				{ id: 'b03_03', name: '03 Elektroinstallation', files: [
					{ id: 'c45', name: 'Elektroplan', priority: 1 },
					{ id: 'c46', name: 'Stationsbereiche', priority: 1 },
					{ id: 'c47', name: 'Combiner Bereiche', priority: 1 },
					{ id: 'c48', name: 'Single Line Diagramm', priority: 1 },
				]},
				{ id: 'b03_04', name: '04 Erdungsplan', files: [
					{ id: 'c49', name: 'Erdungsplan', priority: 2 },
				]},
				{ id: 'b03_06', name: '06 MS-Plan', files: [
					{ id: 'c50', name: 'MS-Plan', priority: 1 },
				]},
				{ id: 'b03_10', name: '10 Monitoring Container', files: [
					{ id: 'c51', name: 'MC-Uebersichtsplan', priority: 2 },
					{ id: 'c52', name: 'Stromlaufplan', priority: 1 },
					{ id: 'c53', name: 'MC-Aufstellung', priority: 3 },
				]},
				{ id: 'b03_11', name: '11 Zaun und Tore', files: [
					{ id: 'c54', name: 'Zaunverlauf', priority: 1 },
				]},
				{ id: 'b03_13', name: '13 Erste-Hilfe', files: [
					{ id: 'c55', name: 'Feuerwehrplan', priority: 1 },
					{ id: 'c56', name: 'Brandschutzkonzept', priority: 1 },
					{ id: 'c57', name: 'Notfallplan', priority: 1 },
					{ id: 'c58', name: 'Havarieplan', priority: 1 },
				]},
			]
		},
		{
			id: 'a04', name: '04 Komponenten',
			subfolders: [
				{ id: 'b04_01', name: '01 Netzanschluss', files: [
					{ id: 'c59', name: 'Netzanschluss Dokumentation', priority: 2 },
				]},
				{ id: 'b04_02', name: '02 Trafostation', files: [
					{ id: 'c60', name: 'Trafostation Dokumentation', priority: 1 },
				]},
				{ id: 'b04_03', name: '03 Kommunikationssystem', files: [
					{ id: 'c61', name: 'Enerbox', priority: 3 },
					{ id: 'c62', name: 'Router', priority: 3 },
					{ id: 'c63', name: 'Antenne', priority: 3 },
					{ id: 'c64', name: 'Fernwirkanlage', priority: 3 },
					{ id: 'c65', name: 'Parkregler', priority: 3 },
					{ id: 'c66', name: 'Datenlogger', priority: 3 },
				]},
				{ id: 'b04_05', name: '05 Wechselrichter', files: [
					{ id: 'c67', name: 'Datenblatt', priority: 1 },
					{ id: 'c68', name: 'Anleitungen', priority: 1 },
					{ id: 'c69', name: 'Schaltplan', priority: 2 },
					{ id: 'c70', name: 'Garantieerklaerung', priority: 3 },
					{ id: 'c71', name: 'Parametrierungsvorlagen', priority: 1 },
				]},
				{ id: 'b04_06', name: '06 Anschlusskasten', files: [
					{ id: 'c72', name: 'Datenblatt', priority: 2 },
					{ id: 'c73', name: 'Schaltplan', priority: 2 },
					{ id: 'c74', name: 'Konformitaetserklaerung', priority: 3 },
				]},
				{ id: 'b04_07', name: '07 Zaehler', files: [
					{ id: 'c75', name: 'Zaehler O&M', priority: 2 },
					{ id: 'c76', name: 'Zaehler EVU', priority: 2 },
				]},
				{ id: 'b04_08', name: '08 Module', files: [
					{ id: 'c77', name: 'Datenblatt', priority: 1 },
					{ id: 'c78', name: 'Installationsanleitung', priority: 3 },
					{ id: 'c79', name: 'Garantieerklaerung', priority: 3 },
					{ id: 'c80', name: 'Flashlists', priority: 3 },
				]},
				{ id: 'b04_09', name: '09 Gestellsystem', files: [
					{ id: 'c81', name: 'Datenblatt', priority: 2 },
					{ id: 'c82', name: 'Installationsanleitung', priority: 3 },
					{ id: 'c83', name: 'Statikgutachten', priority: 3 },
				]},
				{ id: 'b04_13', name: '13 Sicherheitssystem', files: [
					{ id: 'c84', name: 'Zonen- und Meldegruppenplan', priority: 1 },
					{ id: 'c85', name: 'Benutzereinrichtung', priority: 3 },
					{ id: 'c86', name: 'Errichterdokumentation', priority: 3 },
				]},
				{ id: 'b04_17', name: '17 Batteriemoldule', files: [
					{ id: 'c87', name: 'Datenblatt', priority: 1 },
					{ id: 'c88', name: 'Installationsanleitung', priority: 2 },
					{ id: 'c89', name: 'Garantieerklaerung', priority: 1 },
					{ id: 'c90', name: 'Spezifikation', priority: 2 },
				]},
				{ id: 'b04_18', name: '18 BESS Rack', files: [
					{ id: 'c91', name: 'Datenblatt', priority: 1 },
					{ id: 'c92', name: 'Schaltplan', priority: 1 },
					{ id: 'c93', name: 'Anleitungen', priority: 2 },
				]},
				{ id: 'b04_19', name: '19 BatteryBlocks', files: [
					{ id: 'c94', name: 'Datenblatt', priority: 1 },
					{ id: 'c95', name: 'Anleitungen', priority: 1 },
					{ id: 'c96', name: 'Schaltplan', priority: 1 },
					{ id: 'c97', name: 'Datenpunkliste', priority: 2 },
					{ id: 'c98', name: 'HSE', priority: 2 },
				]},
			]
		},
		{
			id: 'a05', name: '05 Inbetriebnahme',
			subfolders: [
				{ id: 'b05_01', name: '01 Protokolle', files: [
					{ id: 'c99',  name: 'Strang Pruefprotokoll', priority: 2 },
					{ id: 'c100', name: 'AC/DC Pruefprotokoll', priority: 2 },
					{ id: 'c101', name: 'WR IB Protokoll', priority: 2 },
					{ id: 'c102', name: 'Erdung Pruefprotokoll', priority: 2 },
					{ id: 'c103', name: 'MS-Kabel Pruefprotokoll', priority: 2 },
					{ id: 'c104', name: 'FWA Protokoll', priority: 1 },
					{ id: 'c105', name: 'Parkregler IB Protokoll', priority: 1 },
					{ id: 'c106', name: 'Netzanalysator IB Protokoll', priority: 2 },
					{ id: 'c107', name: 'Zaehler Protokoll', priority: 2 },
					{ id: 'c108', name: 'Router Protokoll', priority: 2 },
				]},
				{ id: 'b05_02', name: '02 Errichterbescheinigungen', files: [
					{ id: 'c109', name: 'Elektroinstallation AC/DC', priority: 2 },
					{ id: 'c110', name: 'Erdungsanlage Stationen', priority: 2 },
					{ id: 'c111', name: 'MS-Kabelverlegung und Anschluesse', priority: 2 },
				]},
				{ id: 'b05_03', name: '03 Technische Abnahme', files: [
					{ id: 'c112', name: 'Auftraggeber', priority: 3 },
					{ id: 'c113', name: 'Subunternehmer', priority: 3 },
				]},
			]
		},
		{
			id: 'a06', name: '06 Betrieb',
			subfolders: [
				{ id: 'b06_01', name: '01 Reparatur- und Betriebsvorgangsmanagement', files: [] },
				{ id: 'b06_02', name: '02 Betriebsberichte', files: [
					{ id: 'c114', name: '01 Monatsberichte PV', priority: 2 },
					{ id: 'c115', name: '02 Monatsberichte BESS', priority: 2 },
					{ id: 'c116', name: '03 Monatsberichte NAEXT', priority: 2 },
				]},
				{ id: 'b06_03', name: '03 Inspektionen und Wartung', files: [
					{ id: 'c117', name: 'Inspektionen', priority: 3 },
					{ id: 'c118', name: 'Wartungen', priority: 3 },
					{ id: 'c119', name: 'Kennlinienmessungen', priority: 3 },
					{ id: 'c120', name: 'Thermographie', priority: 3 },
					{ id: 'c121', name: 'Umweltgutachten BESS', priority: 2 },
				]},
				{ id: 'b06_04', name: '04 Betriebsmanagement', files: [
					{ id: 'c122', name: 'AE', priority: 2 },
					{ id: 'c123', name: 'VE', priority: 2 },
					{ id: 'c124', name: 'Betriebsanweisungen', priority: 2 },
					{ id: 'c125', name: 'Schaltprogramm', priority: 2 },
				]},
				{ id: 'b06_05', name: '05 Einweisungen', files: [
					{ id: 'c126', name: 'Einweisungen', priority: 3 },
				]},
			]
		},
		{
			id: 'a07', name: '07 O&M Vertraege',
			subfolders: [
				{ id: 'b07_01', name: '01 O&M Vertrag', files: [
					{ id: 'c127', name: 'PV', priority: 1 },
					{ id: 'c128', name: 'BESS', priority: 1 },
				]},
				{ id: 'b07_02', name: '02 Service Partner Vertrag Sicherheitsdienst', files: [
					{ id: 'c129', name: 'Vertrag Sicherheitsdienst', priority: 1 },
				]},
				{ id: 'b07_03', name: '03 Service Partner Vertrag Alarmzentrale', files: [
					{ id: 'c130', name: 'Vertrag Alarmzentrale', priority: 1 },
				]},
				{ id: 'b07_04', name: '04 Service Partner Vertrag Gruenpflege', files: [
					{ id: 'c131', name: 'Vertrag Gruenpflege', priority: 1 },
				]},
				{ id: 'b07_05', name: '05 Service Partner Vertrag Elektro', files: [
					{ id: 'c132', name: 'Vertrag Elektro', priority: 1 },
				]},
				{ id: 'b07_06', name: '06 Service Partner Vertrag MOMUS', files: [
					{ id: 'c133', name: 'Vertrag MOMUS', priority: 1 },
				]},
			]
		},
		{
			id: 'a08', name: '08 Bilder',
			subfolders: [
				{ id: 'b08_01', name: '01 Anlagenbegehung', files: [
					{ id: 'c134', name: 'Anlagenbegehung Fotos', priority: 3 },
				]},
				{ id: 'b08_02', name: '02 Gestellsystem', files: [
					{ id: 'c135', name: 'Gestellsystem Fotos', priority: 3 },
				]},
				{ id: 'b08_03', name: '03 Module', files: [
					{ id: 'c136', name: 'Module Fotos', priority: 3 },
				]},
				{ id: 'b08_04', name: '04 AC-DC Sammler', files: [
					{ id: 'c137', name: 'AC-DC Sammler Fotos', priority: 3 },
				]},
				{ id: 'b08_05', name: '05 WR', files: [
					{ id: 'c138', name: 'Wechselrichter Fotos', priority: 3 },
				]},
				{ id: 'b08_06', name: '06 Stationen', files: [
					{ id: 'c139', name: 'Stationen Fotos', priority: 3 },
				]},
				{ id: 'b08_07', name: '07 Kommunikationssystem', files: [
					{ id: 'c140', name: 'Kommunikationssystem Fotos', priority: 3 },
				]},
				{ id: 'b08_08', name: '08 Monitoring Container', files: [
					{ id: 'c141', name: 'Monitoring Container Fotos', priority: 3 },
				]},
				{ id: 'b08_09', name: '09 Anlagengelaende', files: [
					{ id: 'c142', name: 'Anlagengelaende Fotos', priority: 3 },
				]},
				{ id: 'b08_10', name: '10 Zaun', files: [
					{ id: 'c143', name: 'Zaun Fotos', priority: 3 },
				]},
			]
		},
	];

	// ── Types (search) ────────────────────────────────────────────────────────

	type SearchResult = {
		file: KBFile;
		pathA: string;
		pathB: string;
	};

	// ── State ──────────────────────────────────────────────────────────────────

	let selectedPlant: Plant | null = null;
	let selectedA: FolderA | null = null;
	let selectedB: FolderB | null = null;
	let expandedA: Set<string> = new Set();
	let searchQuery = '';

	$: searchResults = searchQuery.trim().length >= 2
		? KB.flatMap(a =>
				a.subfolders.flatMap(b =>
					b.files
						.filter(f => f.name.toLowerCase().includes(searchQuery.trim().toLowerCase()))
						.map(f => ({ file: f, pathA: a.name, pathB: b.name } as SearchResult))
				)
			)
		: ([] as SearchResult[]);

	$: isSearching = searchQuery.trim().length >= 2;

	$: currentFolders = selectedA?.subfolders ?? [];
	$: currentFiles   = selectedB?.files ?? [];
	$: breadcrumb = selectedPlant
		? selectedB
			? `${selectedPlant.name} › ${selectedA?.name} › ${selectedB.name}`
			: selectedA
				? `${selectedPlant.name} › ${selectedA.name}`
				: selectedPlant.name
		: 'Knowledge Base';

	function selectPlant(plant: Plant) {
		selectedPlant = plant;
		selectedA = KB[0];
		selectedB = null;
		expandedA = new Set([KB[0].id]);
	}

	function backToPlants() {
		selectedPlant = null;
		selectedA = null;
		selectedB = null;
		expandedA = new Set();
		searchQuery = '';
	}

	function selectA(folder: FolderA) {
		if (selectedA?.id === folder.id) {
			expandedA.has(folder.id) ? expandedA.delete(folder.id) : expandedA.add(folder.id);
			expandedA = new Set(expandedA);
		} else {
			selectedA = folder;
			selectedB = null;
			expandedA = new Set([folder.id]);
		}
	}

	function selectB(folder: FolderB) {
		selectedB = folder;
	}

	function goBack() {
		selectedB = null;
	}

	function close() {
		showOmaKnowledgeBase.set(false);
		selectedPlant = null;
		selectedA = null;
		selectedB = null;
		expandedA = new Set();
		searchQuery = '';
	}

	function handleBackdrop(e: MouseEvent) {
		if (e.target === e.currentTarget) close();
	}

	// Priority dot colour — Enerparc palette
	function priorityColor(p: 1 | 2 | 3): string {
		if (p === 1) return 'bg-[#003877] dark:bg-[#73B2F2]';
		if (p === 2) return 'bg-[#73B2F2] dark:bg-[#A8CEFF]';
		return 'bg-gray-300 dark:bg-gray-600';
	}

	function priorityLabel(p: 1 | 2 | 3): string {
		if (p === 1) return 'Critical';
		if (p === 2) return 'Important';
		return 'Standard';
	}

	function totalFiles(folder: FolderA): number {
		return folder.subfolders.reduce((sum, b) => sum + b.files.length, 0);
	}
</script>

{#if $showOmaKnowledgeBase}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
		transition:fade={{ duration: 150 }}
		on:click={handleBackdrop}
		on:keydown={(e) => { if (e.key === 'Escape') close(); }}
		role="dialog"
		tabindex="-1"
		aria-modal="true"
		aria-label="Knowledge Base"
	>
		<!-- Modal card — same size as Prompt Library -->
		<div class="relative flex w-full max-w-4xl h-[82vh] max-h-[700px] rounded-2xl bg-white dark:bg-gray-900 shadow-2xl overflow-hidden">

			<!-- ── Left sidebar ──────────────────────────────────────────────── -->
			<div class="flex flex-col w-60 shrink-0 border-r border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-950">

				<!-- Header -->
				<div class="px-4 pt-5 pb-4 border-b border-gray-100 dark:border-gray-800 shrink-0">
					{#if selectedPlant}
						<div class="flex items-center gap-2">
							<Database className="size-7 text-[#003877] dark:text-[#73B2F2] shrink-0" strokeWidth="1.25" />
							<div class="min-w-0">
								<p class="text-xs font-semibold text-gray-900 dark:text-gray-100 truncate">{selectedPlant.name}</p>
								<p class="text-[11px] text-gray-400 dark:text-gray-500">Knowledge Base</p>
							</div>
						</div>
					{:else}
						<div class="flex items-center gap-2">
							<Database className="size-7 text-[#003877] dark:text-[#73B2F2] shrink-0" strokeWidth="1.25" />
							<div>
								<p class="text-xs font-semibold text-gray-900 dark:text-gray-100">Knowledge Base</p>
								<p class="text-[11px] text-gray-400 dark:text-gray-500">Select a plant</p>
							</div>
						</div>
					{/if}
				</div>

				<!-- Search input -->
				<div class="px-3 py-2 border-b border-gray-100 dark:border-gray-800 shrink-0">
					<div class="relative">
						<svg class="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-gray-400 dark:text-gray-500 pointer-events-none" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
							<path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd" />
						</svg>
						<input
							type="text"
							bind:value={searchQuery}
							placeholder="Search files…"
							class="w-full pl-8 pr-7 py-1.5 text-xs rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-[#003877] dark:focus:ring-[#73B2F2]"
						/>
						{#if searchQuery}
							<button
								on:click={() => { searchQuery = ''; }}
								class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition"
								aria-label="Clear search"
							>
								<XMark className="size-3.5" strokeWidth="2" />
							</button>
						{/if}
					</div>
				</div>

				<!-- Sidebar nav — plant list OR folder tree -->
				<nav class="flex-1 overflow-y-auto px-3 py-3">
					{#if !selectedPlant}
						<!-- Plant list -->
						{#each PLANTS as plant}
							<button
								on:click={() => selectPlant(plant)}
								class="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left transition text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-800"
							>
								<EnergySolarPlant className="size-3.5 shrink-0 opacity-70" />
								<span class="truncate">{plant.name}</span>
							</button>
						{/each}
					{:else}
						<!-- Folder tree (Level A + B) -->
						{#each KB as folderA}
							<div>
								<!-- Level A -->
								<button
									on:click={() => selectA(folderA)}
									class="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left transition text-sm
										{selectedA?.id === folderA.id
											? 'bg-[#003877] text-white dark:bg-[#73B2F2]/20 dark:text-[#73B2F2] font-medium'
											: 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-800'}"
								>
									<ChevronRight className="size-3 shrink-0 transition-transform {expandedA.has(folderA.id) ? 'rotate-90' : ''}" strokeWidth="2" />
									{#if expandedA.has(folderA.id)}
										<FolderOpen className="size-3.5 shrink-0 opacity-80" strokeWidth="1.75" />
									{:else}
										<Folder className="size-3.5 shrink-0 opacity-70" strokeWidth="1.75" />
									{/if}
									<span class="truncate text-xs">{folderA.name}</span>
								</button>

								<!-- Level B (expanded) -->
								{#if expandedA.has(folderA.id)}
									<div transition:slide={{ duration: 120 }}>
										{#each folderA.subfolders as folderB}
											<button
												on:click={() => { selectedA = folderA; selectB(folderB); }}
												class="w-full flex items-center gap-2 pl-8 pr-2 py-1.5 rounded-lg text-left transition text-xs
													{selectedB?.id === folderB.id
														? 'bg-[#003877]/10 text-[#003877] dark:bg-[#73B2F2]/10 dark:text-[#73B2F2] font-medium'
														: 'text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800'}"
											>
												<Folder className="size-3 shrink-0 opacity-60" strokeWidth="1.75" />
												<span class="truncate">{folderB.name}</span>
												{#if folderB.files.length > 0}
													<span class="ml-auto text-[10px] bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-full px-1.5 shrink-0">{folderB.files.length}</span>
												{/if}
											</button>
										{/each}
									</div>
								{/if}
							</div>
						{/each}
					{/if}
				</nav>

				<!-- Priority legend -->
				<div class="px-4 py-3 border-t border-gray-100 dark:border-gray-800 shrink-0">
					<p class="text-[10px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-2">Priority</p>
					<div class="flex flex-col gap-1">
						{#each [1, 2, 3] as p}
							<div class="flex items-center gap-2">
								<span class="size-2 rounded-full shrink-0 {priorityColor(p as 1|2|3)}"></span>
								<span class="text-[11px] text-gray-500 dark:text-gray-400">{priorityLabel(p as 1|2|3)}</span>
							</div>
						{/each}
					</div>
				</div>
			</div>

			<!-- ── Right content ──────────────────────────────────────────────── -->
			<div class="flex flex-col flex-1 min-w-0">

				<!-- Header -->
				<div class="flex items-center justify-between px-6 pt-5 pb-4 shrink-0 border-b border-gray-100 dark:border-gray-800">
					<div class="flex items-center gap-2 min-w-0">
						{#if selectedB}
							<button
								on:click={goBack}
								class="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition shrink-0"
								aria-label="Back"
							>
								<ArrowLeft className="size-4 text-gray-500 dark:text-gray-400" strokeWidth="1.75" />
							</button>
						{:else if selectedPlant}
							<button
								on:click={backToPlants}
								class="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition shrink-0"
								aria-label="All Plants"
							>
								<ArrowLeft className="size-4 text-gray-500 dark:text-gray-400" strokeWidth="1.75" />
							</button>
						{/if}
						<!-- Clickable breadcrumb -->
						<nav class="flex items-center gap-1 min-w-0 flex-wrap" aria-label="Breadcrumb">
							{#if !selectedPlant}
								<span class="text-sm font-semibold text-gray-900 dark:text-gray-100">Knowledge Base</span>
							{:else}
								<!-- Plant segment -->
								{#if selectedA}
									<button
										on:click={backToPlants}
										class="text-sm font-semibold text-gray-400 dark:text-gray-500 hover:text-[#003877] dark:hover:text-[#73B2F2] transition shrink-0"
									>{selectedPlant.name}</button>
								{:else}
									<span class="text-sm font-semibold text-gray-900 dark:text-gray-100 shrink-0">{selectedPlant.name}</span>
								{/if}

								{#if selectedA}
									<span class="text-gray-300 dark:text-gray-600 shrink-0">›</span>
									<!-- Level A segment -->
									{#if selectedB}
										<button
											on:click={goBack}
											class="text-sm font-semibold text-gray-400 dark:text-gray-500 hover:text-[#003877] dark:hover:text-[#73B2F2] transition truncate"
										>{selectedA.name}</button>
										<span class="text-gray-300 dark:text-gray-600 shrink-0">›</span>
										<span class="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate">{selectedB.name}</span>
									{:else}
										<span class="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate">{selectedA.name}</span>
									{/if}
								{/if}
							{/if}
						</nav>
					</div>
					<button
						on:click={close}
						class="rounded-full p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition shrink-0"
						aria-label="Close"
					>
						<XMark className="size-5" strokeWidth="2" />
					</button>
				</div>

				<!-- Content -->
				<div class="flex-1 overflow-y-auto px-6 py-5">

					{#if isSearching}
						<!-- ── Search results ────────────────────────────────────────── -->
						<h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-4">
							{searchResults.length} result{searchResults.length !== 1 ? 's' : ''} for "{searchQuery.trim()}"
						</h3>
						{#if searchResults.length === 0}
							<p class="text-sm text-gray-400 dark:text-gray-500 text-center mt-10">No files found.</p>
						{:else}
							<div class="flex flex-col divide-y divide-gray-100 dark:divide-gray-800 rounded-xl border border-gray-100 dark:border-gray-800 overflow-hidden">
								{#each searchResults as result}
									<div class="flex items-center gap-3 px-4 py-3 bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800/60 transition">
										<Document className="size-4 shrink-0 text-gray-400 dark:text-gray-500" strokeWidth="1.5" />
										<div class="flex-1 min-w-0">
											<p class="text-sm text-gray-800 dark:text-gray-200 truncate">{result.file.name}</p>
											<p class="text-[11px] text-gray-400 dark:text-gray-500 truncate">{result.pathA} › {result.pathB}</p>
										</div>
										<span
											title={priorityLabel(result.file.priority)}
											class="size-2.5 rounded-full shrink-0 {priorityColor(result.file.priority)}"
										></span>
									</div>
								{/each}
							</div>
						{/if}

					{:else if !selectedPlant}
						<!-- ── Plant grid ────────────────────────────────────────────── -->
						<h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-4">Plants</h3>
						<div class="grid grid-cols-4 gap-2">
							{#each PLANTS as plant}
								<button
									on:click={() => selectPlant(plant)}
									class="group flex flex-col items-center gap-1.5 p-3 rounded-xl transition hover:bg-[#003877]/5 dark:hover:bg-[#73B2F2]/5 text-center"
								>
									<EnergySolarPlant className="size-11 text-[#003877] dark:text-[#73B2F2] transition-transform group-hover:scale-105" />
									<p class="text-xs font-medium text-gray-900 dark:text-gray-100 leading-snug line-clamp-2">{plant.name}</p>
									<p class="text-[11px] text-gray-400 dark:text-gray-500">{KB.length} Categories</p>
								</button>
							{/each}
						</div>

					{:else if !selectedB}
						<!-- ── Folders grid ──────────────────────────────────────────── -->
						<h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-4">Folders</h3>
						<div class="grid grid-cols-4 gap-2">
							{#each currentFolders as folderB}
								<button
									on:click={() => selectB(folderB)}
									class="group flex flex-col items-center gap-1.5 p-3 rounded-xl transition hover:bg-[#003877]/5 dark:hover:bg-[#73B2F2]/5 text-center"
								>
									<Folder className="size-11 text-gray-600 dark:text-gray-400 transition-transform group-hover:scale-105" strokeWidth="1.5" />
									<p class="text-xs font-medium text-gray-900 dark:text-gray-100 leading-snug line-clamp-2">{folderB.name}</p>
									<p class="text-[11px] text-gray-400 dark:text-gray-500">{folderB.files.length} {folderB.files.length === 1 ? 'File' : 'Files'}</p>
								</button>
							{/each}
						</div>

					{:else}
						<!-- ── Files list ─────────────────────────────────────────────── -->
						<h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-4">Files</h3>

						{#if currentFiles.length === 0}
							<p class="text-sm text-gray-400 dark:text-gray-500 text-center mt-10">No files in this folder.</p>
						{:else}
							<div class="flex flex-col divide-y divide-gray-100 dark:divide-gray-800 rounded-xl border border-gray-100 dark:border-gray-800 overflow-hidden">
								{#each currentFiles as file}
									<div class="flex items-center gap-3 px-4 py-3 bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800/60 transition">
										<!-- Document icon -->
										<Document className="size-4 shrink-0 text-gray-400 dark:text-gray-500" strokeWidth="1.5" />
										<span class="flex-1 text-sm text-gray-800 dark:text-gray-200 truncate">{file.name}</span>
										<!-- Priority dot -->
										<span
											title={priorityLabel(file.priority)}
											class="size-2.5 rounded-full shrink-0 {priorityColor(file.priority)}"
										></span>
									</div>
								{/each}
							</div>
						{/if}
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
