import os
from google.cloud import translate_v2

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'/Users/mohitdhattarwal/Desktop/wadhwani_farmer_app/token.json'

translate_client = translate_v2.Client()
text = 'do something'
target = 'hi'
output = translate_client.translate(
	text,
	target_language=target)
print(output)