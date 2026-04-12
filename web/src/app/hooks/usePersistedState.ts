import { useCallback, useState } from "react";
import {
	getStoredReadingState,
	type ReadingStateV2,
	saveReadingState,
} from "../utils/storageHelpers";

/**
 * Custom hook that syncs a specific setting to localStorage
 * Automatically persists changes to the reading state
 */
export function usePersistedState<K extends keyof ReadingStateV2>(
	key: K,
	initialValue: ReadingStateV2[K],
): [ReadingStateV2[K], (value: ReadingStateV2[K]) => void] {
	// State for the actual value
	const [value, setValue] = useState<ReadingStateV2[K]>(() => {
		const stored = getStoredReadingState();
		return stored?.[key] ?? initialValue;
	});

	// Callback to update value and persist it
	const setPersisted = useCallback(
		(newValue: ReadingStateV2[K]) => {
			setValue(newValue);

			// Update the entire reading state in localStorage
			const stored = getStoredReadingState();
			if (stored) {
				const updated = { ...stored, [key]: newValue };
				saveReadingState(updated);
			}
		},
		[key],
	);

	return [value, setPersisted];
}

/**
 * Hook to manage per-book position in localStorage
 */
export function usePersistedBookPosition() {
	const [state, setStateInternal] = useState<ReadingStateV2 | null>(() => {
		return getStoredReadingState();
	});

	const setState = useCallback((newState: ReadingStateV2) => {
		setStateInternal(newState);
		saveReadingState(newState);
	}, []);

	return [state, setState] as const;
}
