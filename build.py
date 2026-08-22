import os
import shutil
import re
from jinja2 import Environment, FileSystemLoader

# Mock classes to safely resolve attribute checks like user.email or profile.weight
class SafeMock:
    def __getattr__(self, name):
        if name == 'bmi':
            return 0.0
        return ""
    def __str__(self):
        return ""
    def __getitem__(self, key):
        return ""

def build():
    dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    static_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    
    # 1. Clean and recreate dist directory
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    print(f"Created clean dist directory: {dist_dir}")

    # 2. Copy static files to dist/static
    static_dest = os.path.join(dist_dir, "static")
    shutil.copytree(static_src, static_dest)
    print("Copied static assets to dist/static")

    # 3. Read GEMINI_API_KEY from .env
    gemini_key = ""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip()
                    break
    print(f"Gemini API Key read: {'Configured' if gemini_key else 'Not Configured'}")

    # 4. Setup Jinja environment
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    # Mock url_for helper
    def mock_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', '').lstrip('/')
            return f"static/{filename}"
        elif endpoint == 'home':
            return "index.html"
        elif endpoint == 'logout':
            return "index.html"
        else:
            return f"{endpoint}.html"
            
    env.globals['url_for'] = mock_url_for
    env.globals['get_flashed_messages'] = lambda **kwargs: []

    # 5. Compile templates
    template_files = [f for f in os.listdir(templates_dir) if f.endswith(".html") and f != "session.html"]
    
    for t_file in template_files:
        template = env.get_template(t_file)
        
        # Render template with SafeMock objects
        rendered = template.render(
            fullname="<span id='nav-user-fullname'>User</span>",
            user=SafeMock(),
            profile=SafeMock(),
            latest_bmi=SafeMock(),
            latest_progress=SafeMock(),
            progress=SafeMock(),
            bmi_value=None,
            category=None,
            height=None,
            weight=None,
            bmi_history=[],
            question=None,
            response=None
        )
        
        # 6. Post-processing client-side integrations
        # Inject core database and auth script tags in <head>
        script_injections = (
            '\n    <script src="static/js/database.js"></script>'
            '\n    <script src="static/js/auth-check.js"></script>'
            '\n    <script src="static/js/pages-init.js"></script>\n'
        )
        if "</head>" in rendered:
            rendered = rendered.replace("</head>", f"{script_injections}</head>")
            
        # Re-route the AI Chat request directly to Gemini API client-side in the browser
        if t_file == "ai.html" and gemini_key:
            # Replace fetch block in script
            old_fetch_pattern = r'fetch\(\s*["\']\{\{\s*url_for\(\s*[\'"]ai[\'"]\s*\)\s*\}\}["\']\s*,\s*\{\s*method:\s*["\']POST["\']\s*,\s*headers:\s*\{\s*["\']Content-Type["\']:\s*["\']application/json["\']\s*\}\s*,\s*body:\s*JSON\.stringify\(\{\s*question:\s*question\s*\}\)\s*\}\)'
            
            client_side_api_call = """const profile = HV_DB.getProfile(localStorage.getItem('hv_user_id')) || {};
            const userContext = `User Profile Information:\\n- Age: ${profile.age || 'N/A'} years old\\n- Gender: ${profile.gender || 'N/A'}\\n- Height: ${profile.height || 'N/A'} cm\\n- Weight: ${profile.weight || 'N/A'} kg\\n- Goal: ${profile.goal || 'N/A'}\\n\\n`;
            const fullPrompt = `You are a professional, motivating health and fitness coach at HealthVerse. Your role is to guide users with evidence-based wellness, nutrition, and workout advice. Be encouraging, concise, and clear. Emphasize safety. Do not provide official medical diagnoses, and instruct users to consult a physician if they ask complex medical questions.\\n\\n` + userContext + `User's Question: ${question}\\nAI Coach:`;

            fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=GEMINI_KEY_PLACEHOLDER`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: fullPrompt
                        }]
                    }]
                })
            })""".replace("GEMINI_KEY_PLACEHOLDER", gemini_key)
            rendered = re.sub(old_fetch_pattern, client_side_api_call, rendered)
            
            # Update response parsing logic in ai.html script block to resolve the candidates response correctly
            old_response_then = (
                r'\.then\(data\s*=>\s*\{\s*'
                r'// Hide typing indicator\s*'
                r'typingIndicator\.style\.display\s*=\s*["\']none["\'];\s*'
                r'userInput\.disabled\s*=\s*false;\s*'
                r'sendBtn\.disabled\s*=\s*false;\s*'
                r'userInput\.focus\(\);\s*'
                r'if\s*\(data\.success\s*&&\s*data\.response\)\s*\{\s*'
                r'appendMessage\(data\.response,\s*false\);\s*'
                r'\}\s*else\s*\{\s*'
                r'appendMessage\(["\']Sorry,\s*I\s*encountered\s*an\s*error\.\s*Please\s*try\s*again\s*later\.["\'],\s*false\);\s*'
                r'\}\s*\}\)'
            )
            
            client_side_then_block = """.then(data => {
                typingIndicator.style.display = 'none';
                userInput.disabled = false;
                sendBtn.disabled = false;
                userInput.focus();
                try {
                    const aiText = data.candidates[0].content.parts[0].text;
                    appendMessage(aiText, false);
                } catch (err) {
                    console.error('Error parsing Gemini API response:', err, data);
                    appendMessage('Sorry, I encountered an error parsing the response from the AI Coach.', false);
                }
            })"""
            rendered = re.sub(old_response_then, client_side_then_block, rendered)

        # 7. Write rendered output
        out_path = os.path.join(dist_dir, t_file)
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(rendered)
        print(f"Compiled: {t_file}")

    print("\nStatic build complete! Output is located in dist/")

if __name__ == "__main__":
    build()
