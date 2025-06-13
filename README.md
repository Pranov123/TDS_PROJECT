# Virtual Teaching Assistant API

A smart API that automatically answers student questions based on course content and Discourse forum posts for the Technical Data Science (TDS) course.

## 🚀 Features

- **Intelligent Question Answering**: Uses semantic search and GPT to provide accurate answers
- **Image Support**: Can process questions with image attachments using OCR
- **Course Content Integration**: Searches through TDS course materials
- **Discourse Integration**: Leverages community discussions and solutions
- **Cost Calculations**: Handles token counting and pricing questions
- **RESTful API**: Simple JSON-based API interface

## 📋 Prerequisites

- Python 3.9+
- OpenAI API key
- Course content files:
  - `tds_corrected_data.json` (scraped course content)
  - `tds_discourse_data.json` (scraped Discourse posts)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Pranov123/tds_project.git
cd tds_project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
export GEMINI_API_KEY="AIzaSyDMyPi-LgeRip-TIrofvzSw0yowdK1oAFM"
export COURSE_CONTENT_PATH="tds_corrected_data.json"
export DISCOURSE_POSTS_PATH="tds_discourse_data.json"
```

### 4. Add Your Data Files
Place your scraped JSON files in the project root:
- `tds_corrected_data.json`
- `tds_discourse_data.json`

### 5. Run the API
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 🐳 Docker Deployment

### Build and Run
```bash
# Build the Docker image with your repo name
docker build -t tds_project .

# Run the container with Gemini API key environment variable
docker run -p 5000:5000 \
  -e GEMINI_API_KEY="AIzaSyDMyPi-LgeRip-TIrofvzSw0yowdK1oAFM" \
  -v $(pwd)/tds_corrected_data.json:/app/data/tds_corrected_data.json \
  -v $(pwd)/tds_discourse_data.json:/app/data/tds_discourse_data.json \
  tds_project

```

## ☁️ Deploy to Cloud

### Railway (Recommended)
1. Fork this repository
2. Connect to [Railway](https://railway.app)
3. Add environment variables:
   - `OPENAI_API_KEY`
4. Upload your JSON files to the deployment
5. Your API will be available at: `https://your-app.railway.app`

### Other Platforms
- **Heroku**: Use the included `Procfile`
- **Google Cloud Run**: Deploy using the Dockerfile
- **DigitalOcean App Platform**: Use the Docker configuration

## 📡 API Documentation

### Endpoint
```
POST /api/
```

### Request Format
```json
{
  "question": "Your question here",
  "image": "base64-encoded-image (optional)"
}
```

### Response Format
```json
{
  "answer": "Detailed answer to your question",
  "links": [
    {
      "url": "https://discourse.example.com/topic/123",
      "text": "Relevant discussion excerpt"
    }
  ]
}
```

### Example Usage

#### Text Question
```bash
curl "https://your-api-url.com/api/" \
  -H "Content-Type: application/json" \
  -d '{"question": "Should I use gpt-4o-mini or gpt-3.5-turbo for the assignment?"}'
```

#### Question with Image
```bash
curl "https://your-api-url.com/api/" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"How many cents would this cost?\", \"image\": \"$(base64 -w0 question-image.png)\"}"
```

## 🧪 Testing and Evaluation

### Run Promptfoo Evaluation
1. **Update the API URL** in `project-tds-virtual-ta-promptfoo.yaml`:
   ```yaml
   providers:
     - id: http
       config:
         url: 'https://YOUR-ACTUAL-API-URL.com/api/'  # ← Update this!
   ```

2. **Run the evaluation:**
   ```bash
   # Make script executable
   chmod +x run_evaluation.sh
   
   # Run evaluation
   ./run_evaluation.sh
   ```

   Or run directly:
   ```bash
   npx -y promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml
   ```

3. **View results:**
   ```bash
   npx promptfoo view
   ```

### Test Cases Include
- GPT model selection questions
- Token cost calculations
- Technical implementation help
- Assignment clarifications
- Troubleshooting support
- Image-based questions

## 📁 Project Structure
```
virtual-ta-api/
├── app.py                                    # Main API server
├── requirements.txt                          # Python dependencies
├── Dockerfile                               # Docker configuration
├── README.md                               # This file
├── .env.example                            # Environment variables template
├── .gitignore                              # Git ignore rules
├── data/                                   # Data directory
│   ├── tds_corrected_data.json            # Course content (you provide)
│   └── tds_discourse_data.json            # Discourse posts (you provide)
├── evaluation/
│   ├── project-tds-virtual-ta-promptfoo.yaml  # Evaluation config
│   ├── run_evaluation.sh                      # Evaluation runner
│   └── generate_sample_data.py                # Sample data generator
└── docs/                                   # Documentation
    └── evaluation_guide.md                # Detailed evaluation guide
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `COURSE_CONTENT_PATH` | Path to course content JSON | No (default: `tds_corrected_data.json`) |
| `DISCOURSE_POSTS_PATH` | Path to discourse posts JSON | No (default: `tds_discourse_data.json`) |

### Data File Formats

#### Course Content (`tds_corrected_data.json`)
```json
[
  {
    "title": "Lesson title",
    "content": "Lesson content text",
    "module": "Module name",
    "week": 1,
    "type": "lecture_note"
  }
]
```

#### Discourse Posts (`tds_discourse_data.json`)
```json
[
  {
    "id": 123456,
    "title": "Post title",
    "url": "https://discourse.example.com/t/topic/123",
    "raw": "Post content",
    "created_at": "2025-01-01T00:00:00Z",
    "author": "username"
  }
]
```

## 🎯 API Endpoint URL Configuration

**⚠️ IMPORTANT**: You need to update the API URL in the evaluation config after deployment:

1. **After deploying your API**, note your deployment URL (e.g., `https://your-app.railway.app`)
2. **Update** `project-tds-virtual-ta-promptfoo.yaml`:
   ```yaml
   providers:
     - id: http
       config:
         url: 'https://your-app.railway.app/api/'  # ← Your actual URL here
   ```

### Common Deployment URLs:
- **Railway**: `https://your-app-name.railway.app`
- **Heroku**: `https://your-app-name.herokuapp.com`
- **Google Cloud Run**: `https://your-service-hash-region.run.app`
- **Local Development**: `http://localhost:5000`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **API Issues**: Check the `/health` endpoint for API status
- **Evaluation Problems**: Review the [Evaluation Guide](docs/evaluation_guide.md)
- **Deployment Help**: Check your platform's documentation
- **Questions**: Open an issue in this repository

## 🏆 Performance Benchmarks

The API is designed to:
- Respond within 10 seconds for most queries
- Handle concurrent requests efficiently
- Provide accurate answers based on course content
- Include relevant Discourse links when available

Run the evaluation suite to measure performance on your deployment!
