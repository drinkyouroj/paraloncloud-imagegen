# ParalonCloud Image Generation & Editing Tool

A creative tool that generates images, applies style transfers, and performs image-to-image transformations using distributed GPU resources via ParalonCloud's OpenAI-compatible API.

## Features

- ✨ **Image Generation**: Create stunning images from text descriptions using DALL-E models
- ✏️ **Image Editing**: Edit existing images by describing desired changes
- 🔄 **Image Variations**: Generate creative variations of existing images
- 🎨 **Style Transfer**: Apply artistic styles from one image to another

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

## Setup

### 1. Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory:
```bash
PARALONCLOUD_API_KEY=your_api_key_here
PARALONCLOUD_API_BASE=https://api.paraloncloud.com/v1
```

3. Start the backend server:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Generate Image
- **POST** `/api/generate`
- **Body**: `multipart/form-data`
  - `prompt` (string, required): Image description
  - `model` (string, default: "dall-e-3"): Model to use
  - `size` (string, default: "1024x1024"): Image size
  - `quality` (string, default: "standard"): Image quality (for DALL-E 3)
  - `n` (int, default: 1): Number of images

### Edit Image
- **POST** `/api/edit`
- **Body**: `multipart/form-data`
  - `image` (file, required): Image to edit
  - `prompt` (string, required): Edit description
  - `mask` (file, optional): Mask image
  - `model` (string, default: "dall-e-2"): Model to use
  - `size` (string, default: "1024x1024"): Output size
  - `n` (int, default: 1): Number of variations

### Create Variation
- **POST** `/api/variation`
- **Body**: `multipart/form-data`
  - `image` (file, required): Source image
  - `model` (string, default: "dall-e-2"): Model to use
  - `size` (string, default: "1024x1024"): Output size
  - `n` (int, default: 1): Number of variations

### Style Transfer
- **POST** `/api/style-transfer`
- **Body**: `multipart/form-data`
  - `base_image` (file, required): Base image
  - `style_image` (file, required): Style reference image
  - `alpha` (float, default: 0.5): Blending factor (0.0 to 1.0)

## Project Structure

```
paraloncloud/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── paralon_client.py    # ParalonCloud API client
│   └── image_processor.py   # Image processing utilities
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── components/      # React components
│   │   └── index.js         # React entry point
│   └── package.json
├── uploads/                 # Uploaded images (auto-created)
├── generated/               # Generated images (auto-created)
├── requirements.txt
├── .gitignore
└── README.md
```

## Usage

1. Start both the backend and frontend servers
2. Open your browser to `http://localhost:3000`
3. Select a tab (Generate, Edit, Variations, or Style Transfer)
4. Fill in the required fields and submit
5. View your generated or processed images

## Notes

- Make sure your `.env` file contains a valid `PARALONCLOUD_API_KEY`
- The API base URL defaults to `https://api.paraloncloud.com/v1` but can be customized
- Generated images are saved locally in the `generated/` directory
- Uploaded images are temporarily stored in the `uploads/` directory

## License

MIT
