import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="config/.env")

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"

with open('config/template.txt', 'r', encoding='utf-8') as f:
    template = f.read()

with open('config/meeting.txt', 'r', encoding='utf-8') as f:
    meeting = f.read()

with open('config/template_preference.txt', 'r', encoding='utf-8') as f:
    template_perference = f.read()

with open('config/template_mindmap.txt', 'r', encoding='utf-8') as f:
    template_mindmap = f.read()