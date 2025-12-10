import requests
import base64
import re
import argparse

parser = argparse.ArgumentParser(description="Extract favorited GIF URLs from Discord account settings")
parser.add_argument("--token", type=str, required=True, help="Discord account authorization token")
parser.add_argument("--output", type=str, default="favorited_gifs.txt", help="Output file path for saving GIF URLs")
args = parser.parse_args()


TOKEN = args.token
output_file = args.output


req_url = "https://discord.com/api/v9/users/@me/settings-proto/2"
headers = {
    "accept": "*/*",
    "accept-language": "en-US",
    "authorization": TOKEN,
    "content-type": "application/json",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-debug-options": "bugReporterEnabled",
    "x-discord-locale": "en-US",
    "x-discord-timezone": "America/Los_Angeles"
}

response = requests.get(req_url, headers=headers)
response.raise_for_status()
gifs_base64: str = response.json().get("settings", "")


b64 = gifs_base64.strip()
if len(b64) % 4:
    b64 += "=" * (4 - (len(b64) % 4))

raw = base64.b64decode(b64)
cleaned = re.compile(rb"[\x00-\x1F]+").sub(b" ", raw)
raw_urls = re.compile(rb"https?://(?:[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]|\\[xu][0-9A-Fa-f]{1,4})+").findall(cleaned)

urls = []
for u in raw_urls:
    text = u.decode("unicode_escape", errors="ignore")
    text = text.replace("\\/", "/")
    text = text.rstrip(".,;)]}<>\"' ")
    urls.append(text)

gifs = list(dict.fromkeys(urls))

normalized_urls = set()
for url in gifs:
    if "media.discordapp.net" in url:
        url = url.replace("media.discordapp.net", "cdn.discordapp.com")
        url = url.split("?")[0]
    elif "images-ext-1.discordapp.net" in url:
        continue
    else:
        normalized_urls.add(url)


with open(output_file, "w", encoding="utf-8") as f:
    f.write('\n'.join(normalized_urls))

print(f"extracted {len(gifs)} total gif urls and normalized down to {len(normalized_urls)} urls saved to {output_file}\nThis tool was made by Sleepy (https://eepy.io/) and is licensed under the OSLv1.3 found at https://sleepie.dev/licenses/sleepys_open_source_license_v1.3.md")

