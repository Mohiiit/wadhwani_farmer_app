import os
from google.cloud import translate_v2
from schema import schemas

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"./token.json"

# function to translate the text in the "target" language
async def translate_text(text, target):
    translate_client = translate_v2.Client()
    output = translate_client.translate(text, target_language=target)
    return output


# function to join the data of farmer in order to save multiple api calls
async def join_farmer_data(farmer: schemas.FarmerExport, lang: str):
    joined_data = str(
        farmer.farmer_name
        + ","
        + farmer.state_name
        + ","
        + farmer.district_name
        + ","
        + farmer.village_name
    )
    output = await translate_text(joined_data, lang)
    output = output["translatedText"]
    translated_data = output.split(",")
    return translated_data
