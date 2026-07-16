import { afterEach, beforeEach, describe, expect, test } from "bun:test";
import {
	createDefaultReadingState,
	getStoredReadingState,
} from "./storageHelpers";

const originalWindow = Object.getOwnPropertyDescriptor(globalThis, "window");

const createLocalStorage = (initialValue) => {
	const values = new Map(
		initialValue ? [["davar.readingState", initialValue]] : [],
	);

	return {
		getItem: (key) => values.get(key) ?? null,
		setItem: (key, value) => values.set(key, value),
	};
};

beforeEach(() => {
	Object.defineProperty(globalThis, "window", {
		configurable: true,
		value: { localStorage: createLocalStorage() },
	});
});

afterEach(() => {
	if (originalWindow) {
		Object.defineProperty(globalThis, "window", originalWindow);
	} else {
		delete globalThis.window;
	}
});

describe("Hutter announcement persistence", () => {
	test("new reading state has no announcement release receipt", () => {
		expect(createDefaultReadingState().hutterAnnouncementRelease).toBe("");
	});

	test("legacy boolean receipt does not suppress the new OTA announcement", () => {
		const legacyState = {
			...createDefaultReadingState(),
			hutterAnnouncementSeen: true,
		};
		delete legacyState.hutterAnnouncementRelease;

		window.localStorage = createLocalStorage(JSON.stringify(legacyState));

		expect(getStoredReadingState()?.hutterAnnouncementRelease).toBe("");
	});
});
