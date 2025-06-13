from flask import Flask, request, jsonify
import json
import base64
import io
from PIL import Image
import pytesseract
import os
from datetime import datetime
import re
from typing import List, Dict, Optional, Tuple
import tiktoken
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai

app = Flask(__name__)

class VirtualTA:
    def __init__(self, course_content_path: str, discourse_posts_path: str, gemini_api_key: str):
        self.course_content_path = course_content_path
        self.discourse_posts_path = discourse_posts_path
        self.gemini_api_key = gemini_api_key
        
        # Load data
        self.course_content = self.load_json_data(course_content_path)
        self.discourse_posts = self.load_json_data(discourse_posts_path)
        
        # Initialize sentence transformer for semantic search
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create embeddings for all content
        self.content_embeddings = self.create_content_embeddings()
        
        # Initialize tokenizer for cost calculations
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Still use tiktoken for cost

        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')

    def load_json_data(self, file_path: str) -> List[Dict]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            return []
    
    def create_content_embeddings(self) -> Dict:
        embeddings = {'course_content': [], 'discourse_posts': []}
        for content in self.course_content:
            text = self.extract_text_from_content(content)
            if text:
                embedding = self.sentence_model.encode(text)
                embeddings['course_content'].append({
                    'text': text,
                    'embedding': embedding,
                    'metadata': content
                })
        for post in self.discourse_posts:
            text = self.extract_text_from_discourse_post(post)
            if text:
                embedding = self.sentence_model.encode(text)
                embeddings['discourse_posts'].append({
                    'text': text,
                    'embedding': embedding,
                    'metadata': post
                })
        return embeddings
    
    def extract_text_from_content(self, content: Dict) -> str:
        text_parts = []
        text_fields = ['title', 'content', 'description', 'text', 'body', 'summary']
        for field in text_fields:
            if field in content and content[field]:
                text_parts.append(str(content[field]))
        return ' '.join(text_parts).strip()
    
    def extract_text_from_discourse_post(self, post: Dict) -> str:
        text_parts = []
        if 'title' in post and post['title']:
            text_parts.append(post['title'])
        if 'raw' in post and post['raw']:
            text_parts.append(post['raw'])
        elif 'cooked' in post and post['cooked']:
            clean_text = re.sub(r'<[^>]+>', '', post['cooked'])
            text_parts.append(clean_text)
        elif 'content' in post and post['content']:
            text_parts.append(post['content'])
        return ' '.join(text_parts).strip()
    
    def extract_text_from_image(self, base64_image: str) -> str:
        try:
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            extracted_text = pytesseract.image_to_string(image)
            return extracted_text.strip()
        except Exception as e:
            print(f"Error extracting text from image: {str(e)}")
            return ""
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[Dict]:
        query_embedding = self.sentence_model.encode(query)
        results = []
        for item in self.content_embeddings['course_content']:
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1),
                item['embedding'].reshape(1, -1)
            )[0][0]
            results.append({
                'text': item['text'],
                'similarity': similarity,
                'type': 'course_content',
                'metadata': item['metadata']
            })
        for item in self.content_embeddings['discourse_posts']:
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1),
                item['embedding'].reshape(1, -1)
            )[0][0]
            results.append({
                'text': item['text'],
                'similarity': similarity,
                'type': 'discourse_post',
                'metadata': item['metadata']
            })
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def generate_answer(self, question: str, context_items: List[Dict]) -> Tuple[str, List[Dict]]:
        context_text = ""
        links = []
        for item in context_items:
            context_text += f"\n--- {item['type'].upper()} ---\n"
            context_text += item['text'][:1000] + "...\n"
            if item['type'] == 'discourse_post' and 'url' in item['metadata']:
                links.append({
                    'url': item['metadata']['url'],
                    'text': item['text'][:100] + "..." if len(item['text']) > 100 else item['text']
                })
        prompt = f"""You are a Teaching Assistant for a Technical Data Science course. Answer the student's question based on the provided course content and discourse discussions.

Context from course materials and discussions:
{context_text}

Student Question: {question}

Provide a clear, helpful answer based on the context provided. If the question involves specific technical details or calculations, be precise and reference the relevant information from the context.

Answer:"""
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.1
                )
            )
            answer = response.text.strip()
            return answer, links[:3]
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return "I apologize, but I'm unable to generate an answer at the moment. Please try again later.", []
    
    def calculate_token_cost(self, text: str, cost_per_million: float = 0.50) -> float:
        tokens = self.tokenizer.encode(text)
        num_tokens = len(tokens)
        cost = (num_tokens / 1_000_000) * cost_per_million
        return cost
    
    def process_question(self, question: str, image_base64: Optional[str] = None) -> Dict:
        image_text = ""
        if image_base64:
            image_text = self.extract_text_from_image(image_base64)
            if image_text:
                question = f"{question}\n\nImage content: {image_text}"
        relevant_content = self.semantic_search(question, top_k=5)
        answer, links = self.generate_answer(question, relevant_content)
        if any(keyword in question.lower() for keyword in ['token', 'cost', 'cents', 'gpt-3.5', 'turbo']):
            if image_text:
                cost = self.calculate_token_cost(image_text)
                answer += f"\n\nNote: If this question is about calculating token costs, the input would cost approximately {cost:.5f} cents (assuming 50 cents per million input tokens)."
        return {
            "answer": answer,
            "links": links
        }

# Initialize the Virtual TA
COURSE_CONTENT_PATH = os.getenv('COURSE_CONTENT_PATH', 'course_content.json')
DISCOURSE_POSTS_PATH = os.getenv('DISCOURSE_POSTS_PATH', 'discourse_posts.json')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

virtual_ta = VirtualTA(COURSE_CONTENT_PATH, DISCOURSE_POSTS_PATH, GEMINI_API_KEY)

@app.route('/api/', methods=['POST'])
def answer_question():
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        question = data['question']
        image_base64 = data.get('image')
        result = virtual_ta.process_question(question, image_base64)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
