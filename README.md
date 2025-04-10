# ReelsBuilder.ai Clone

A full-stack application for generating professional motivational videos using free APIs and tools.

## Features

- Generate voiceovers from text using gTTS (Google Text-to-Speech)
- Fetch high-quality stock videos from Pexels API
- Create vertical (9:16) videos optimized for TikTok/Reels
- Add text overlays and transitions
- Mobile-friendly interface
- No login required

## Tech Stack

- Frontend: Next.js 14, React, Tailwind CSS
- Backend: FastAPI (Python)
- Video Processing: MoviePy
- Text-to-Speech: gTTS
- Stock Videos: Pexels API

## Prerequisites

- Node.js 18+
- Python 3.8+
- Pexels API key (free)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd reelsbuilder-clone
```

2. Set up the frontend:
```bash
cd src/frontend
npm install
```

3. Set up the backend:
```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```
PEXELS_API_KEY=your_pexels_api_key
```

## Running the Application

1. Start the backend server:
```bash
cd src/backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

2. Start the frontend development server:
```bash
cd ../frontend
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Enter your motivational script (1-3 sentences)
2. Select a vibe/keyword for the stock videos
3. Click "Generate Video"
4. Preview and download your video

## API Endpoints

- `POST /generate`: Generate a new video
  - Body: `{ script: string, vibe: string }`
  - Returns: `{ success: boolean, video_path: string }`

- `GET /download/{video_path}`: Download the generated video
  - Returns: Video file (MP4)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.