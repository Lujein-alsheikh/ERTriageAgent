"use client";

import { useState, useEffect } from "react";
import {
  TRIAGE_COLUMN_NAME,
  TRIAGE_OPTIONS,
  extractTriageNumber,
} from "../lib/utils";

interface DataEntry {
  [key: string]: any;
}

export default function NurseInterface() {
  const [dataStore, setDataStore] = useState<DataEntry[]>([]);
  const [confirmedRows, setConfirmedRows] = useState<number[]>([]);
  const [triageOverrides, setTriageOverrides] = useState<
    Record<number, string>
  >({});
  const [loading, setLoading] = useState(false);

  // Fetch data from API
  const fetchData = async () => {
    try {
      const response = await fetch("/api/data");
      const result = await response.json();
      if (result.data) {
        setDataStore(result.data);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  // Initial fetch and auto-refresh every 2 seconds
  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      fetchData();
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Handle triage level change
  const handleTriageChange = (index: number, value: string) => {
    setTriageOverrides((prev) => ({
      ...prev,
      [index]: value,
    }));
  };

  // Handle confirm button click
  const handleConfirm = async (index: number) => {
    if (confirmedRows.includes(index)) {
      return; // Already confirmed
    }

    setLoading(true);
    try {
      const row = dataStore[index];
      const rowDict = { ...row };

      // Use override if present
      const override = triageOverrides[index];
      if (override !== undefined && TRIAGE_COLUMN_NAME in rowDict) {
        rowDict[TRIAGE_COLUMN_NAME] = override;
      }

      // Send confirmation webhook via API route
      const response = await fetch("/api/confirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(rowDict),
      });

      if (!response.ok) {
        throw new Error("Failed to send confirmation");
      }

      // Mark as confirmed
      setConfirmedRows((prev) => [...prev, index]);
    } catch (error) {
      console.error("Error confirming row:", error);
      alert("Failed to confirm. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Get all column names from data
  const getColumns = (): string[] => {
    if (dataStore.length === 0) return [];
    const allKeys = new Set<string>();
    dataStore.forEach((entry) => {
      Object.keys(entry).forEach((key) => allKeys.add(key));
    });
    return Array.from(allKeys);
  };

  const columns = getColumns();
  const triageColIndex = columns.findIndex(
    (col) => col === TRIAGE_COLUMN_NAME
  );

  return (
    <div style={{ padding: "2rem", maxWidth: "1400px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "2rem" }}>
        🚑 Nurse Interface
      </h1>

      {dataStore.length === 0 ? (
        <div
          style={{
            padding: "1rem",
            backgroundColor: "#e3f2fd",
            borderRadius: "4px",
            color: "#1976d2",
          }}
        >
          No patients yet!
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              backgroundColor: "white",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            <thead>
              <tr style={{ backgroundColor: "#f5f5f5" }}>
                {columns.map((colName, i) => (
                  <th
                    key={i}
                    style={{
                      padding: "12px",
                      textAlign: "left",
                      borderBottom: "2px solid #ddd",
                      fontWeight: "600",
                    }}
                  >
                    {colName}
                  </th>
                ))}
                <th
                  style={{
                    padding: "12px",
                    textAlign: "left",
                    borderBottom: "2px solid #ddd",
                    fontWeight: "600",
                  }}
                >
                  Confirm?
                </th>
              </tr>
            </thead>
            <tbody>
              {dataStore.map((row, idx) => {
                const isConfirmed = confirmedRows.includes(idx);
                
                // Get triage value and extract just the number (1-5)
                const rawTriageValue =
                  triageOverrides[idx] ?? row[TRIAGE_COLUMN_NAME];
                const currentTriageValue = extractTriageNumber(rawTriageValue);

                return (
                  <tr
                    key={idx}
                    style={{
                      borderBottom: "1px solid #eee",
                      backgroundColor: isConfirmed ? "#e0e0e0" : "white",
                      transition: "background-color 0.5s ease-in-out",
                    }}
                  >
                    {columns.map((colName, colIdx) => (
                      <td key={colIdx} style={{ padding: "12px" }}>
                        {colName === TRIAGE_COLUMN_NAME ? (
                          <select
                            value={currentTriageValue || TRIAGE_OPTIONS[0]}
                            onChange={(e) =>
                              handleTriageChange(idx, e.target.value)
                            }
                            disabled={isConfirmed}
                            style={{
                              padding: "6px 12px",
                              borderRadius: "4px",
                              border: "1px solid #ddd",
                              fontSize: "14px",
                              width: "100%",
                              maxWidth: "200px",
                            }}
                          >
                            {TRIAGE_OPTIONS.map((option) => (
                              <option key={option} value={option}>
                                {option}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <span>{String(row[colName] ?? "")}</span>
                        )}
                      </td>
                    ))}
                    <td style={{ padding: "12px" }}>
                      <button
                        onClick={() => handleConfirm(idx)}
                        disabled={isConfirmed || loading}
                        style={{
                          padding: "8px 16px",
                          borderRadius: "4px",
                          border: "none",
                          backgroundColor: isConfirmed
                            ? "#4caf50"
                            : "#2196f3",
                          color: "white",
                          cursor: isConfirmed || loading ? "not-allowed" : "pointer",
                          fontSize: "14px",
                          opacity: isConfirmed || loading ? 0.6 : 1,
                        }}
                      >
                        {isConfirmed ? "done" : "✅"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

