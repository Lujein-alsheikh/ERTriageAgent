// In-memory data store
// Note: On Vercel serverless, this won't persist across cold starts.
// For production, consider using a database or Vercel KV.

interface DataEntry {
  [key: string]: any;
}

const dataStore: DataEntry[] = [];

export function addData(data: DataEntry): void {
  dataStore.push(data);
  console.log("✅ Received data:", data);
  console.log("datastore", dataStore);
}

export function getData(): DataEntry[] {
  return dataStore;
}

export function clearData(): void {
  dataStore.length = 0;
}

