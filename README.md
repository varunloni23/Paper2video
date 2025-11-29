# Paper2Video 🎬

Transform your research papers into engaging video presentations powered by AI.

## Features

- 📄 **Multi-format Support**: Upload PDF, DOCX, PPTX, or LaTeX (ZIP) files
- 🤖 **AI-Powered Script Generation**: Uses Google Gemini to create engaging slide scripts
- 🎨 **Multiple Style Presets**: Academic, Corporate, Creative, and Minimal styles
- 🗣️ **Natural TTS Narration**: Microsoft Edge neural voices for high-quality voiceover
- 🎥 **Automated Video Composition**: FFmpeg-powered video generation with transitions
- 👤 **Animated Avatar**: SVG-based talking head with lip-sync animation
- 📊 **Job Dashboard**: Real-time progress tracking and job management

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (Neon serverless)
- **AI**: Google Gemini API
- **TTS**: edge-tts (Microsoft Edge neural voices)
- **Video**: FFmpeg
- **Image**: Pillow (PIL)

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- FFmpeg installed on your system
- PostgreSQL database (Neon recommended)
- Google Gemini API key

## Installation

### 1. Clone the repository

```bash
cd Paper2video
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host/database?ssl=require

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# File Storage Paths
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 4. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html)

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

## Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Start Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs/upload` | Upload a document |
| POST | `/api/jobs/{job_id}/start` | Start processing |
| GET | `/api/jobs/{job_id}` | Get job status |
| GET | `/api/jobs` | List all jobs |
| GET | `/api/jobs/{job_id}/video` | Download video |
| DELETE | `/api/jobs/{job_id}` | Delete a job |
| POST | `/api/jobs/{job_id}/retry` | Retry failed job |

## Project Structure

```
Paper2video/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   └── app/
│       ├── config.py           # Settings management
│       ├── database.py         # Database connection
│       ├── models.py           # SQLAlchemy models
│       ├── routes/
│       │   └── jobs.py         # API routes
│       └── services/
│           ├── document_parser.py      # PDF/DOCX/PPTX/LaTeX parsing
│           ├── slide_generator.py      # Gemini AI script generation
│           ├── tts_generator.py        # Edge TTS voiceover
│           ├── slide_image_generator.py # Slide PNG generation
│           ├── video_composer.py       # FFmpeg video composition
│           ├── avatar_generator.py     # SVG avatar animation
│           └── job_processor.py        # Main processing pipeline
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── src/
│       └── app/
│           ├── layout.tsx      # Root layout
│           ├── page.tsx        # Home page (upload)
│           ├── globals.css     # Global styles
│           ├── dashboard/
│           │   └── page.tsx    # Job dashboard
│           └── job/
│               └── [id]/
│                   └── page.tsx # Job detail page
└── README.md
```

## Usage

1. **Upload**: Go to the home page and drag & drop your research paper
2. **Configure**: Select style preset and avatar option
3. **Process**: Click "Create Video" to start processing
4. **Monitor**: Watch real-time progress on the dashboard
5. **Download**: Once complete, download your video presentation

## Style Presets

- **Academic**: Professional slides with dark background, perfect for academic presentations
- **Corporate**: Clean, business-oriented design with modern typography
- **Creative**: Vibrant, colorful slides with dynamic layouts
- **Minimal**: Simple, distraction-free design focusing on content

## Avatar Options

- **None**: No avatar overlay, just slides with narration
- **Male**: Animated male avatar with lip-sync
- **Female**: Animated female avatar with lip-sync

## Troubleshooting

### FFmpeg not found
Make sure FFmpeg is installed and available in your system PATH:
```bash
ffmpeg -version
```

### Database connection issues
Verify your DATABASE_URL in `.env` is correct and the database is accessible.

### Gemini API errors
Ensure your GEMINI_API_KEY is valid and has sufficient quota.

### TTS generation fails
edge-tts requires an internet connection. Check your network connectivity.

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
