import os
from google.cloud import translate_v2

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"./token.json"


async def translate_text(text, target):
    translate_client = translate_v2.Client()
    output = translate_client.translate(text, target_language=target)
    return output
