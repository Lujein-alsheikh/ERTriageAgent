import { NextRequest, NextResponse } from "next/server";
import { addData, getData } from "../../../lib/dataStore";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    addData(body);
    return NextResponse.json({ status: "ok" });
  } catch (error) {
    return NextResponse.json(
      { status: "error", message: "Invalid JSON" },
      { status: 400 }
    );
  }
}

export async function GET() {
  // Allow GET to view data (used by frontend for polling)
  return NextResponse.json({ data: getData() });
}

