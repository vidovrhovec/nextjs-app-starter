import openai
import requests

def extract_section(text: str, section: str) -> str:
    """
    Helper function to extract code between tags.
    """
    start_tag = f"[START {section}]"
    end_tag = f"[END {section}]"
    start = text.find(start_tag)
    end = text.find(end_tag)
    if start == -1 or end == -1:
        return ""
    return text[start + len(start_tag): end].strip()

def generate_website(prompt: str, api_key: str, api_type: str = "openai", api_url: str = None) -> dict:
    """
    Calls the AI API to generate website code based on the prompt.
    Supports 'openai' or 'custom' api_type.
    For 'custom', api_url must be provided.
    Returns a dictionary with keys: 'index.html', 'style.css', and optionally 'script.js'.
    """
    try:
        if api_type == "openai":
            openai.api_key = api_key
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Generate a complete website with HTML, CSS, and optionally JavaScript based on the following description:\n\n{prompt}\n\n"
                       "Output must include only the following sections:\n"
                       "[START INDEX.HTML]\n...HTML code...\n[END INDEX.HTML]\n"
                       "[START STYLE.CSS]\n...CSS code...\n[END STYLE.CSS]\n"
                       "[START SCRIPT.JS]\n...JavaScript code if needed...\n[END SCRIPT.JS]",
                max_tokens=1500,
                temperature=0.7,
            )
            text = response.choices[0].text
        elif api_type == "custom":
            if not api_url:
                raise ValueError("API URL must be provided for custom API type")
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            payload = {
                "model": "text-davinci-003",
                "prompt": f"Generate a complete website with HTML, CSS, and optionally JavaScript based on the following description:\n\n{prompt}\n\n"
                          "Output must include only the following sections:\n"
                          "[START INDEX.HTML]\n...HTML code...\n[END INDEX.HTML]\n"
                          "[START STYLE.CSS]\n...CSS code...\n[END STYLE.CSS]\n"
                          "[START SCRIPT.JS]\n...JavaScript code if needed...\n[END SCRIPT.JS]",
                "max_tokens": 1500,
                "temperature": 0.7,
            }
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            json_resp = response.json()
            # Assuming the response structure is similar to OpenAI's
            text = json_resp.get("choices", [{}])[0].get("text", "")
        else:
            raise ValueError(f"Unsupported api_type: {api_type}")

        website_files = {
            "index.html": extract_section(text, "INDEX.HTML"),
            "style.css": extract_section(text, "STYLE.CSS"),
        }
        script_js = extract_section(text, "SCRIPT.JS")
        if script_js:
            website_files["script.js"] = script_js
        return website_files
    except Exception as e:
        raise RuntimeError(f"Error generating website: {e}")
