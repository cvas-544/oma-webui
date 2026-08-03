// ---------------------------------------------------------------------------
// File:        artifacts.ts
// Description: Persistent store for user-generated artifacts (docs + images).
//              Metadata in localStorage; image blobs in IndexedDB.
// Author:      Vasu Chukka
// Co-author:   Claude Code
// ---------------------------------------------------------------------------
import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { v4 as uuidv4 } from 'uuid';

export type ArtifactItem = {
	id: string;
	type: 'document' | 'image';
	name: string;
	ts: number;
	chatId: string;
	messageId: string;
	// document-only
	url?: string;
	ext?: string;
	// image-only (stored in IndexedDB keyed by id)
};

// ── localStorage for metadata ──────────────────────────────────────────────

const META_KEY = 'invertix_artifacts_meta';

function loadMeta(): ArtifactItem[] {
	if (!browser) return [];
	try {
		return JSON.parse(localStorage.getItem(META_KEY) ?? '[]');
	} catch {
		return [];
	}
}

function saveMeta(items: ArtifactItem[]) {
	if (!browser) return;
	try {
		localStorage.setItem(META_KEY, JSON.stringify(items));
	} catch {
		// storage quota exceeded — silently skip
	}
}

function createStore() {
	const { subscribe, set, update } = writable<ArtifactItem[]>(browser ? loadMeta() : []);

	return {
		subscribe,
		add(item: Omit<ArtifactItem, 'id'>): string {
			const id = uuidv4();
			update((items) => {
				const next = [{ ...item, id }, ...items];
				saveMeta(next);
				return next;
			});
			return id;
		},
		remove(id: string) {
			update((items) => {
				const next = items.filter((i) => i.id !== id);
				saveMeta(next);
				return next;
			});
			deleteImageBlob(id).catch(() => {});
		}
	};
}

export const artifacts = createStore();

// ── IndexedDB for image blobs ──────────────────────────────────────────────

const DB_NAME = 'invertix_artifact_images';
const STORE_NAME = 'blobs';

let _db: IDBDatabase | null = null;

function openDb(): Promise<IDBDatabase> {
	if (_db) return Promise.resolve(_db);
	return new Promise((resolve, reject) => {
		if (!browser) { reject(new Error('IndexedDB not available')); return; }
		const req = indexedDB.open(DB_NAME, 1);
		req.onupgradeneeded = () => req.result.createObjectStore(STORE_NAME);
		req.onsuccess = () => {
			_db = req.result;
			resolve(_db);
		};
		req.onerror = () => reject(req.error);
	});
}

export async function saveImageBlob(id: string, dataUrl: string): Promise<void> {
	const db = await openDb();
	return new Promise((resolve, reject) => {
		const tx = db.transaction(STORE_NAME, 'readwrite');
		tx.objectStore(STORE_NAME).put(dataUrl, id);
		tx.oncomplete = () => resolve();
		tx.onerror = () => reject(tx.error);
	});
}

export async function loadImageBlob(id: string): Promise<string | null> {
	const db = await openDb();
	return new Promise((resolve, reject) => {
		const tx = db.transaction(STORE_NAME, 'readonly');
		const req = tx.objectStore(STORE_NAME).get(id);
		req.onsuccess = () => resolve((req.result as string) ?? null);
		req.onerror = () => reject(req.error);
	});
}

async function deleteImageBlob(id: string): Promise<void> {
	const db = await openDb();
	return new Promise((resolve, reject) => {
		const tx = db.transaction(STORE_NAME, 'readwrite');
		tx.objectStore(STORE_NAME).delete(id);
		tx.oncomplete = () => resolve();
		tx.onerror = () => reject(tx.error);
	});
}
