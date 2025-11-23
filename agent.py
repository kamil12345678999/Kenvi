import ollama
from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
import re
import gc
import time


# 🧠 AI generator
def ai_generate(prompt, system_msg):
    result = ollama.generate(model="gpt-oss:120b-cloud", prompt=prompt, system=system_msg+"  (if they ask for school timings it is from 8:30 to 2:40)")
    return result["response"].strip()


# 🧩 Classify question type
def is_normal_question(user_question):
    classify_prompt = (
        f"Classify the user question:\n\n'{user_question}'\n\n"
        "If it's just a greeting, small talk, or casual (like 'hi', 'how are you', 'who are you'), reply ONLY 'NORMAL'. "
        "If it needs factual or web-based info (like 'who is the principal of KV Bolarum'), reply ONLY 'SEARCH'."
    )
    result = ai_generate(classify_prompt, "Question type classifier")
    return False


# 🌐 DuckDuckGo Search
def web_search(query):
    with DDGS() as ddgs:
        results = []
        for r in ddgs.text(query, max_results=5):
            results.append(f"Title: {r.get('title','')}\nURL: {r.get('href','')}\nSnippet: {r.get('body','')}\n")
        return results


def format_results(results):
    if not results:
        return "No search results found."
    return "\n".join(results)


# 🈳 Translate Hindi → English
def translate_to_english(text):
    if re.search(r"[\u0900-\u097F]", text):  # detect Hindi (Devanagari script)
        prompt = f"Translate this Hindi or mixed text to clear English:\n\n{text}"
        return ai_generate(prompt, "Hindi to English translator")
    return text


# 🏫 Parse KV Bolarum staff details page
def scrape_staff_details(base_url="https://bolarum.kvs.ac.in/en/staff-details/"):
    try:
        print(f"🌐 Checking staff details page: {base_url}")
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.find("table")
        if not table:
            return "Staff details table not found on official site."

        rows = table.find_all("tr")
        staff_list = []
        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 2:
                staff_list.append(" | ".join(cols))

        text = "\n".join(staff_list)
        return text if text.strip() else "No staff details found on official site."
    except Exception as e:
        return f"Error accessing staff details: {e}"


# 🏫 Fallback — scrape homepage
def scrape_official_site(user_question, base_url="https://bolarum.kvs.ac.in/"):
    try:
        print(f"🌐 Checking official site homepage: {base_url}")
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        text = soup.get_text(" ", strip=True)
        text_lower = text.lower()

        keywords = [
            w for w in re.findall(r"\b\w+\b", user_question.lower())
            if w not in {"who", "what", "is", "the", "a", "of", "in", "for", "school",
                         "pm", "shri", "kendriya", "vidyalaya", "bolarum"}
        ]

        for word in keywords:
            if word in text_lower:
                idx = text_lower.find(word)
                snippet = text[idx:idx + 600]
                translated = translate_to_english(snippet)
                return f"{translated}"
        return "No relevant info found on official site homepage."
    except Exception as e:
        return f"Error accessing site homepage: {e}"


# ✅ AI checks if answer matches question
def answer_matches(question, answer):
    check_prompt = (
        f"Question: {question}\nAnswer: {answer}\n\n"
        "You are a factual checker. "
        "If the answer correctly responds to the question, reply only 'YES'. "
        "If it doesn’t, reply only 'NO'."
    )
    result = ai_generate(check_prompt, "Answer validation AI")
    return result.upper().startswith("YES")


def main():
    print("📘 PM Shri Kendriya Vidyalaya Bolarum Info Assistant")
    print("----------------------------------------------------")
    user_question = input("Enter your question: ")

    # Step 0: detect normal vs search
    print("\n🤖 Checking question type...")
    if is_normal_question(user_question):
        normal_response = ai_generate(
            f"User said: {user_question}\n\nRespond naturally like a helpful assistant of Kendriya Vidyalaya Bolarum. Keep it short.",
            "Friendly school assistant and your name is kenvi"
        )
        print("\n💬 Answer:")
        print(normal_response)
        return

    # Step 1: rephrase for search
    query_prompt = f"{user_question}\n\nRewrite this into a short search query about PM Shri Kendriya Vidyalaya Bolarum."
    search_query = ai_generate(query_prompt, "Query rephraser")
    print(f"\n🧩 Generated Query: {search_query}")

    # Step 2: check staff page first
    print("\n🔍 Attempt 1: Searching staff details page...")
    staff_data = scrape_staff_details()

    if "Error" not in staff_data and "No staff" not in staff_data:
        # AI tries to find answer within staff data
        prompt = (
            f"Question: {user_question}\nStaff Details:\n{staff_data}\n\n"
            "From this staff list, identify the exact answer to the question if possible. "
            "Answer directly in one short line with the name and role only."
        )
        staff_answer = ai_generate(prompt, "Staff info extractor and your name is kenvi")
        print("\n🏫 Checking answer relevance...")
        if answer_matches(user_question, staff_answer):
            print("\n🏫 Final Answer:")
            print(f"{staff_answer}")
            return
        else:
            print("⚠️ Found info doesn’t match. Trying homepage...")

    # Step 3: fallback to homepage
    print("\n🔍 Attempt 2: Searching official site homepage...")
    site_data = scrape_official_site(user_question)
    answer = ai_generate(f"[{site_data}]  this is that data make it easy to understand and revelent to this {user_question}, and your name is kenvi","if they ask for school timings it is from 8:30 to 2:40")

    if "No relevant info" not in site_data and "Error" not in site_data:
        if answer_matches(user_question, site_data):
            print("\n🏫 Final Answer:")
            print(answer)
            return

    # Step 4: normal web search fallback
    print("\n🔍 Attempt 3: Normal web search...")
    results = web_search(search_query)
    formatted = format_results(results)

    response_prompt = (
        f"User Query: {user_question}\n\nSearch Results:\n{formatted}\n\n"
        "You are an assistant for PM Shri Kendriya Vidyalaya Bolarum. "
        "Give a short, factual, direct answer in 1–2 lines. If not found, say 'Not found'."
    )
    answer = ai_generate(response_prompt, "Short factual responder and your name is kenvi")

    print("\n🤖 Validating answer relevance...")
    if not answer_matches(user_question, answer):
        print("⚠️ Answer didn’t match — retrying once more...")
        time.sleep(2)
        results = web_search(search_query)
        formatted = format_results(results)
        answer = ai_generate(
            f"User Query: {user_question}\nResults:\n{formatted}\n\n"
            "Answer shortly in 1–2 lines if possible.",
            "Short factual responder and your name is kenvi"
        )

    print("\n🏫 Final Answer:")
    print(answer if answer else "Not found after retries.")
    gc.collect()


if __name__ == "__main__":
    main()
