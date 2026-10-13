// Places on the walk. Home, school and rec centre are representative spots, not specific
// addresses, and the map says so. The named places are at their real coordinates.
export interface Stop {
	id: string;
	label: string;
	lonlat: [number, number];
	exact: boolean;
}

export const STOPS: Stop[] = [
	{ id: 'home', label: 'Home', lonlat: [-79.2575, 43.7505], exact: false },
	{ id: 'kennedy', label: 'Kennedy Station', lonlat: [-79.2637, 43.7326], exact: true },
	{ id: 'school', label: 'Your school', lonlat: [-79.2305, 43.7655], exact: false },
	{ id: 'rec', label: 'Rec centre', lonlat: [-79.2445, 43.8065], exact: false },
	{ id: 'cityhall', label: 'City Hall', lonlat: [-79.3841, 43.6534], exact: true },
	{ id: 'queenspark', label: "Queen's Park", lonlat: [-79.3916, 43.6625], exact: true }
];

/** Which part of the map each story step frames, and which stops are lit. */
export interface View {
	frame: 'scarborough' | 'city';
	upTo: number; // route drawn through STOPS[0..upTo]
	shade?: 'perResident';
}

export const VIEWS: View[] = [
	{ frame: 'scarborough', upTo: 0 },
	{ frame: 'scarborough', upTo: 1 },
	{ frame: 'scarborough', upTo: 2 },
	{ frame: 'scarborough', upTo: 3, shade: 'perResident' },
	{ frame: 'city', upTo: 4, shade: 'perResident' },
	{ frame: 'city', upTo: 5 },
	{ frame: 'city', upTo: 5 },
	{ frame: 'city', upTo: 5 }
];
