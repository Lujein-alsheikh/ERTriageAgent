import { NextRequest, NextResponse } from "next/server";
import { sendConfirm } from "../../../lib/utils";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    await sendConfirm(body);
    return NextResponse.json({ status: "ok" });
  } catch (error) {
    console.error("Error sending confirmation:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to send confirmation" },
      { status: 500 }
    );
  }
}

