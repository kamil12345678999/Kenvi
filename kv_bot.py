
from agent import (
    is_normal_question, ai_generate, scrape_staff_details,
    scrape_official_site, web_search, format_results, answer_matches
)

import time

def answer_question(user_question: str, context: str = "") -> str:
    """
    Enhanced answer_question that uses visible chat context if present.
    
    :param user_question: latest question from user
    :param context: all visible chat text from frontend (optional)
    :return: short factual answer or 'Not found'
    """

    # Build the complete query with context if available
    if context and context.strip():
        # Create a full contextual prompt
        full_query = f"""Previous Conversation:
{context.strip()}

Current Question: {user_question.strip()}

Instructions: Answer the current question. If it refers to previous messages (like "what did I ask?"), reference the conversation history above."""
    else:
        full_query = user_question

    print(f"\n{'='*60}")
    print(f"🤖 KV Bot Processing:")
    print(f"   Question: {user_question}")
    print(f"   Context provided: {'Yes' if context else 'No'}")
    print(f"{'='*60}")

    # For questions about conversation history, answer directly from context
    history_keywords = ["what did i ask", "what did i tell", "what did i say", "previous question", "last time", "before"]
    if context and any(keyword in user_question.lower() for keyword in history_keywords):
        print(f"   → Detected conversation history question")
        
        # Let AI extract the answer from conversation context
        history_prompt = f"""Conversation History:
{context.strip()}

Question: {user_question}

Based on the conversation history above, answer what the user previously asked or said. Be specific and direct."""
        
        answer = ai_generate(history_prompt, "Conversation history analyzer and your name is kenvi")
        
        print(f"   ✓ Answer from context: {answer}")
        print(f"{'='*60}\n")
        return answer

    # Step 1: Rephrase query (use full query with context for better understanding)
    search_query = ai_generate(
        f"{full_query}\n\nRewrite this into a short search query about PM Shri Kendriya Vidyalaya Bolarum.",
        "Query rephraser and your name is kenvi"
    )
    
    print(f"   Search query: {search_query}")

    # Step 2: Web search fallback
    results = web_search(search_query)
    formatted = format_results(results)
    
    response_prompt = (
        f"User Query: {full_query}\n\n"
        f"Search Results:\n{formatted}\n\n"
        "You are KENVI, an assistant for PM Shri Kendriya Vidyalaya Bolarum. "
        "Give a short, factual, direct answer in 1–2 lines. If not found, say 'Not found'. principal is Venna A Rote timing are 8:30 to 2:40, best t"
    )
    
    answer = ai_generate(response_prompt, "Short factual responder and your name is kenvi")

    # Step 3: Final check and retry if needed
    if not answer_matches(user_question, answer):
        print(f"   Answer validation failed, retrying...")
        time.sleep(1)
        results = web_search(search_query)
        formatted = format_results(results)
        answer = ai_generate(
            f"Query: {full_query}\nResults:\n{formatted}\n\nAnswer shortly in 1–2 lines if possible.",
            "Short factual responder and your name is kenvi"
        )

    final_answer = answer or "Not found"
    print(f"   ✓ Final answer: {final_answer}")
    print(f"{'='*60}\n")
    
    return final_answer