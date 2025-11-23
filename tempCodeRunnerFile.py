from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import kv_bot
import traceback
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

# Serve the main frontend
@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
    """
    Main API endpoint to answer questions with conversation context
    
    Expected JSON:
    {
        "user_id": "user_123",
        "question": "what did i ask?",
        "chat_text": "Chat History:\n...",
        "conversation_history": [...],
        "remember": true
    }
    """
    try:
        data = request.get_json(force=True)
        question = data.get('question', '').strip()
        chat_text = data.get('chat_text', '')  # Get visible chat text from frontend
        user_id = data.get('user_id', 'anonymous')
        
        if not question:
            return jsonify({'error': 'Empty question'}), 400

        print(f"\n{'='*60}")
        print(f"📝 Request from user: {user_id}")
        print(f"❓ Question: {question}")
        print(f"📚 Chat context lines: {len(chat_text.split(chr(10))) if chat_text else 0}")
        print(f"{'='*60}")

        # IMPORTANT: Pass chat_text as context parameter to kv_bot
        # This allows kv_bot to see the full conversation history
        answer = kv_bot.answer_question(question, context=chat_text)
        
        print(f"✅ Answer: {answer}\n")

        return jsonify({'answer': answer}), 200

    except Exception as e:
        print(f"❌ Error in /api/ask: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/reset', methods=['POST'])
def reset_memory():
    """
    Reset conversation memory endpoint (for Clear button)
    """
    try:
        data = request.get_json(force=True)
        user_id = data.get('user_id')
        print(f"🗑️ Memory cleared for user: {user_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Conversation history cleared',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        print(f"❌ Error in /api/memory/reset: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """Health check endpoint"""
    return jsonify({
        'status': 'server working', 
        'message': 'Hello from KV Bolarum',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Get server status"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    }), 200

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ========== MAIN ==========

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════╗
    ║   KENVI AI Backend - Flask Server      ║
    ║   Running on: http://0.0.0.0:5000      ║
    ║   IP: 192.168.1.9                      ║
    ║   With Conversation Context Support    ║
    ╚════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5000, ssl_context=None, debug=True, threaded=True)