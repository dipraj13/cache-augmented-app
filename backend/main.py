from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from groq import Groq
from PyPDF2 import PdfReader
from cache_handler import CacheHandler

app = Flask(__name__)
CORS(app)
load_dotenv()
API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=API_KEY)
cache = CacheHandler()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
    try:
        pdf_reader = PdfReader(file)
        text = " ".join(page.extract_text() for page in pdf_reader.pages)
        if not text.strip():
            return jsonify({"error": "No text found in PDF"}), 400
            
        cache.add_document(text)
        return jsonify({"message": f"PDF processed! {len(pdf_reader.pages)} pages added to document cache"})
        
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/generate', methods=['POST'])
def generate_response():
    data = request.json
    prompt = data.get('prompt')
    
    # Check cache first
    if prompt in cache.conversation_cache:
        return jsonify({"response": cache.conversation_cache[prompt], "source": "cache"})
    
    # Get document context using improved logic
    document_context = cache.get_document_context(prompt)
    print(document_context)
    # Build messages
    messages = [{"role": "user", "content": prompt}]
    
    if document_context:
        print("here")
        system_msg = "Answer using this document content. If asked for a summary, provide a concise overview:"
        messages.insert(0, {
            "role": "system", 
            "content": f"{system_msg}\n{document_context[:5000]}"
        })
    
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.5
        )
        response = completion.choices[0].message.content
        
        # Cache response
        cache.conversation_cache[prompt] = response
        
        return jsonify({
            "response": response,
            "source": "llm+docs" if document_context else "llm"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)