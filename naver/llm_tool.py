import subprocess, json

def query_ollama_same_name(name_db, name_naver) -> bool:
    prompt = f"Compare if two names are indicating the same city: '{name_db}' vs '{name_naver}'. Respond by true or false."
    result = subprocess.run(
        ["ollama", "run", "phi", prompt],
        capture_output=True, text=True
    )
    response = result.stdout.find('true') >= 0
    return response

print(query_ollama_same_name("Seoul", "Seoul special city"))
