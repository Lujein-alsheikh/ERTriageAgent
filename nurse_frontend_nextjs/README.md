# Nurse Frontend - Next.js Version

This is a Next.js implementation of the Streamlit nurse frontend, designed to be deployed on Vercel.

## Features

- **API Endpoint**: `/api/data` (POST) - Receives patient data from n8n
- **Auto-refresh**: Polls for new data every 2 seconds
- **Editable Triage Levels**: Dropdown to modify triage level before confirmation
- **Confirmation Webhook**: Sends confirmation to n8n webhook when a row is confirmed
- **State Management**: Tracks confirmed rows and triage overrides

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.local.example .env.local
```

3. Edit `.env.local` with your webhook URL (or set it in Vercel dashboard)

## Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Deployment to Vercel

1. Push your code to GitHub/GitLab/Bitbucket
2. Import the project in Vercel
3. **Important**: Since this Next.js app is in a subdirectory (`nurse_frontend_nextjs`), configure Vercel:
   - Go to **Project Settings → General**
   - Under **Root Directory**, click **Edit** and select `nurse_frontend_nextjs`
   - Or when importing, select **"Configure Project"** and set:
     - **Root Directory**: `nurse_frontend_nextjs`
     - **Framework Preset**: Next.js (should auto-detect)
     - **Build Command**: `npm install && npm run build` (or leave default)
4. Set the environment variable `N8N_CONFIRM_WEBHOOK_URL` in Vercel dashboard (Settings → Environment Variables)
5. Deploy!

## API Endpoints

### POST `/api/data`
Receives patient data from external systems (e.g., n8n)

**Request body:**
```json
{
  "patient_id": "123",
  "triage level": "3",
  "name": "John Doe",
  ...
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### GET `/api/data`
Returns all stored patient data (used by frontend for polling)

**Response:**
```json
{
  "data": [...]
}
```

### POST `/api/confirm`
Sends confirmation webhook (internal use by frontend)

## Important Notes

⚠️ **Data Persistence**: The current implementation uses in-memory storage, which means:
- Data will be lost on serverless function cold starts on Vercel
- For production use, consider integrating a database (e.g., Vercel KV, PostgreSQL, MongoDB)

For a production-ready version, you should replace the in-memory store in `lib/dataStore.ts` with a proper database solution.

