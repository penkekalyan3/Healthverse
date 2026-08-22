import requests
from config import Config

def get_ai_response(question, user_profile=None):
    """Sends question to Gemini API via HTTP POST with user context and returns the response text.
    Bypasses SDK dependencies to support older Python versions like 3.8.0.
    """
    if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY.strip() == "":
        return (
            "🤖 (Demo Mode) Hello! I am your HealthVerse AI coach. "
            "To unlock real AI responses, please configure your GEMINI_API_KEY in the config.py or .env file.\n\n"
            "Here is some general advice:\n"
            "• Stay active: Aim for at least 150 minutes of moderate aerobic activity per week.\n"
            "• Stay hydrated: Drink 2-3 Liters of water daily.\n"
            "• Sleep well: Strive for 7-9 hours of restful sleep every night."
        )
        
    try:
        # Construct context prompt
        system_instruction = (
            "You are a professional, motivating health and fitness coach at HealthVerse. "
            "Your role is to guide users with evidence-based wellness, nutrition, and workout advice. "
            "Be encouraging, concise, and clear. Emphasize safety. "
            "Do not provide official medical diagnoses, and instruct users to consult a physician if they ask complex medical questions.\n\n"
        )
        
        user_context = ""
        if user_profile:
            user_context = (
                "User Profile Information:\n"
                f"- Age: {user_profile.get('age', 'N/A')} years old\n"
                f"- Gender: {user_profile.get('gender', 'N/A')}\n"
                f"- Height: {user_profile.get('height', 'N/A')} cm\n"
                f"- Weight: {user_profile.get('weight', 'N/A')} kg\n"
                f"- Goal: {user_profile.get('goal', 'N/A')}\n\n"
            )
            
        full_prompt = f"{system_instruction}{user_context}User's Question: {question}\nAI Coach:"
        
        # Prepare direct API call using gemini-3.5-flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={Config.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ]
        }
        
        # Call the Google Gemini endpoint
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            res_data = response.json()
            try:
                ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
                return ai_text
            except (KeyError, IndexError) as parse_error:
                return f"Error parsing response from Gemini API: {str(parse_error)}"
        else:
            return f"Error from Gemini API (HTTP {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"Error contacting AI Coach: {str(e)}"
