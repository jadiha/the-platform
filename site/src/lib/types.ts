// Shapes follow docs/data-contract.md. Money is in $ millions unless `unit` says otherwise.

export type FactStatus = 'verified' | 'single' | 'disagree' | 'reported';

export interface SourceRef {
	title: string;
	url: string;
	locator?: string;
	date?: string;
	value?: number | string;
	note?: string;
}

export interface Fact {
	value: number | string;
	unit: '$M' | '$' | '%' | 'people' | 'date' | 'count' | string;
	label: string;
	basis?: string;
	primary: SourceRef;
	crosscheck?: SourceRef[];
	status: FactStatus;
	note?: string;
	as_of: string;
}

export type Facts = Record<string, Fact>;

export interface Decision {
	date: string;
	what: string;
	vote?: string;
	item?: string;
	source: SourceRef;
}

export interface Quote {
	date: string;
	text: string;
	context?: string;
	source: SourceRef;
}

export interface Person {
	id: string;
	name: string;
	role: string;
	level: 'city' | 'province' | 'federal' | 'school';
	party?: string | null;
	ward_or_riding?: string | null;
	term?: { start?: string; end?: string | null };
	on_ballot_2026?: boolean | null;
	official_url?: string;
	photo?: string;
	decisions?: Decision[];
	quotes?: Quote[];
	as_of: string;
}

export interface BudgetNode {
	id: string;
	name: string;
	category?: string;
	year?: string;
	basis?: string;
	gross: number;
	net?: number | null;
	note?: string;
	source?: SourceRef;
	originalLines?: string[];
	children?: BudgetNode[];
}

export interface TrendPoint {
	year: string;
	value: number;
	kind: 'actual' | 'interim' | 'plan';
	sourceRef?: string;
}

export type Trends = Record<string, Record<string, TrendPoint[]>> & { notes?: unknown };

export interface WardRow {
	ward: number;
	name: string;
	scarborough: boolean;
	population: number;
	capital10yr: number;
	capital2026: number;
	perResident10yr: number;
	topProjects: { name: string; program: string; amount10yr: number; category?: string }[];
}

export interface Wards {
	asOf: string;
	capitalPlan: string;
	cityWide: { capital10yr: number; share: number };
	wards: WardRow[];
}

export interface DataSource {
	id: string;
	title: string;
	url: string;
	fetchedAt: string;
	sha256?: string;
	file?: string;
}
