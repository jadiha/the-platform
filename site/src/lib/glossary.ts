// Plain-language definitions for the jargon popups and /glossary.
// Keep each `short` to one or two sentences a 14-year-old would follow.
export interface Term {
	term: string;
	short: string;
	more?: string;
	source?: { title: string; url: string };
}

export const GLOSSARY: Record<string, Term> = {
	'operating-budget': {
		term: 'Operating budget',
		short: 'Money for day-to-day costs: wages, running buses, keeping shelters open. Like rent and groceries.',
		more: 'It has to be spent again every year. Cities in Ontario are not allowed to run a deficit on it.'
	},
	'capital-budget': {
		term: 'Capital budget',
		short: 'Money to build or fix big, long-lasting things: subways, rec centres, roads. Like saving up to buy a car.',
		more: 'Toronto plans it 10 years ahead, so you will often see a "10-year capital plan".'
	},
	'property-tax': {
		term: 'Property tax',
		short: 'A yearly bill homeowners pay the city, based on what their home is worth. Renters pay it too, because it is built into rent.'
	},
	gross: {
		term: 'Gross (total cost)',
		short: 'Everything a service costs, no matter who pays for it.',
		more: 'Example: a program might cost $1.5 billion gross while the city itself pays only $100 million, because the province and federal government cover the rest.'
	},
	net: {
		term: 'Net (paid by the city)',
		short: 'The part of a cost the city pays itself, mostly from property tax, after other governments, fares and fees chip in.'
	},
	deficit: {
		term: 'Deficit',
		short: 'When a government spends more than it takes in during a year. It borrows to cover the gap, which adds to its debt.'
	},
	'ward': {
		term: 'Ward',
		short: 'Toronto is split into 25 areas called wards. Each one elects one city councillor. Scarborough is wards 20 to 25.'
	},
	'riding': {
		term: 'Riding',
		short: 'An area that elects one representative to Queen\'s Park (an MPP) or to Ottawa (an MP). Ridings and wards have different borders.'
	},
	councillor: {
		term: 'City councillor',
		short: 'Your elected rep at Toronto City Hall. Council votes on the city budget every year.'
	},
	mpp: {
		term: 'MPP',
		short: 'Member of Provincial Parliament: your elected rep at Queen\'s Park, where Ontario\'s budget, including schools and hospitals, is decided.'
	},
	mp: {
		term: 'MP',
		short: 'Member of Parliament: your elected rep in Ottawa, for federal money like transit and housing grants.'
	},
	trustee: {
		term: 'School trustee',
		short: 'An elected member of a school board like TDSB. Trustees normally approve the board\'s budget.'
	},
	supervisor: {
		term: 'Provincial supervisor',
		short: 'A person the province appoints to run a school board instead of its elected trustees, usually over money problems.'
	},
	'city-wide': {
		term: 'City-wide spending',
		short: 'Money the city does not tag to any one ward, like the whole TTC system or police. You cannot fairly split it by neighbourhood.'
	},
	'public-accounts': {
		term: 'Public Accounts',
		short: 'Ontario\'s official, audited report of what it actually spent last year, as opposed to what it planned.'
	},
	'budget-vs-actual': {
		term: 'Budget vs. actual',
		short: 'A budget is a plan. Actuals are what really got spent. They are often different.'
	},
	fao: {
		term: 'FAO',
		short: 'Ontario\'s Financial Accountability Office: an independent watchdog that checks the province\'s budget math.',
		source: { title: 'fao-on.org', url: 'https://fao-on.org' }
	},
	'strong-mayor': {
		term: 'Strong-mayor powers',
		short: 'Ontario rules that let Toronto\'s mayor propose the city budget and veto some council changes to it.'
	},
	transfers: {
		term: 'Transfers',
		short: 'Money one government gives another. Ottawa sends money to Ontario; Ontario and Ottawa send money to Toronto.'
	}
};
