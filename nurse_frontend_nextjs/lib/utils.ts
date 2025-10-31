// Utility functions

export function normalizeKey(name: string): string {
  return name.replace(/_/g, "").replace(/\s/g, "").toLowerCase();
}

export function extractField(
  row: Record<string, any>,
  candidateNames: string[]
): any {
  // Try exact match first
  for (const name of candidateNames) {
    if (name in row) {
      return row[name];
    }
  }

  // Try case-insensitive match
  const lowerMap: Record<string, any> = {};
  for (const key in row) {
    lowerMap[key.toLowerCase()] = row[key];
  }
  for (const name of candidateNames) {
    if (name.toLowerCase() in lowerMap) {
      return lowerMap[name.toLowerCase()];
    }
  }

  // Try normalized match
  const normMap: Record<string, any> = {};
  for (const key in row) {
    normMap[normalizeKey(key)] = row[key];
  }
  for (const name of candidateNames) {
    if (normalizeKey(name) in normMap) {
      return normMap[normalizeKey(name)];
    }
  }

  return null;
}

export async function sendConfirm(row: Record<string, any>): Promise<void> {
  const CONFIRM_WEBHOOK_URL =
    process.env.N8N_CONFIRM_WEBHOOK_URL ||
    "https://lujein.app.n8n.cloud/webhook/triage-confirmation";

  if (!CONFIRM_WEBHOOK_URL) {
    return;
  }

  const payload = {
    patient_id: extractField(row, ["patient_id", "patient id", "id"]),
    triage_level: row["triage level"],
  };

  try {
    const response = await fetch(CONFIRM_WEBHOOK_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    // Silently handle errors (matching original behavior)
    if (!response.ok) {
      console.error("Failed to send confirmation webhook");
    }
  } catch (error) {
    // Silently handle errors (matching original behavior)
    console.error("Error sending confirmation webhook:", error);
  }
}

export const TRIAGE_COLUMN_NAME = "triage level";
export const TRIAGE_OPTIONS = ["1", "2", "3", "4", "5"];

/**
 * Extracts the triage level number (1-5) from any format
 * Examples: "2" -> "2", "level 2" -> "2", "Level 2" -> "2", "3 - Vital Signs" -> "3"
 */
export function extractTriageNumber(value: any): string {
  if (value === null || value === undefined) {
    return "";
  }

  const strValue = String(value).trim();

  // Try direct match first (fast path)
  if (TRIAGE_OPTIONS.includes(strValue)) {
    return strValue;
  }

  // Extract number 1-5 from string using regex
  const match = strValue.match(/\b([1-5])\b/);
  if (match && match[1]) {
    return match[1];
  }

  // If no number found, return empty string
  return "";
}

