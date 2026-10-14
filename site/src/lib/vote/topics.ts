// Topic colours for candidates' published priorities. Six clearly different hues, so the dots on the
// candidate tiles don't blend together. These colour topics only, never a candidate.
export const TOPIC = { tax: 'Taxes', transit: 'Getting around', housing: 'Housing', safety: 'Safety', money: 'City money', other: 'Other' } as const;
export const TOPIC_COLOR = { tax: '#f08c00', transit: '#1971c2', housing: '#2f9e44', safety: '#7048e8', money: '#d6336c', other: '#868e96' } as const;
export type Topic = keyof typeof TOPIC;
