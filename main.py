import asyncio
import bs4
import requests
from slugify import slugify
from ast import literal_eval
import aiohttp
import aiofiles

# Firstly, need to download all possible unicodes for emojis and their descriptions.
# Emojis have a range 1F600-1F64F.
response = requests.get('https://www.prosettings.com/emoji-list/')
soup = bs4.BeautifulSoup(response.text)
all_emojis_trs = (tr for tr in soup.find_all('tr') if tr.find('th') is None)
emojis_descriptions = ((literal_eval('0x' + tr.find('a')['href'][1:]), slugify(tr.find_all('td')[3].text)) for tr in
                       all_emojis_trs)

# Let's make the dict for the best experience in the future.
# All emojis have saved with the same url, changes only their codes.
# I will get only a webp format, but you can change link file extensions and file name for gifs, for example.
all_emojis_links: dict = {
    code: {
        'url': f'https://fonts.gstatic.com/s/e/notoemoji/latest/{hex(code)[2:]}/512.webp',
        'file_name': f'{description}.webp',
    }
    for code, description in emojis_descriptions
}


async def load_emoji(url: str, file_name: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            if resp.ok:
                await asyncio.sleep(1)
                async with aiofiles.open(f'emojis/{file_name}', mode='wb') as f:
                    await f.write(await resp.read())
                    print(f'{file_name} downloaded!')


async def load_emojis():
    tasks: list = [
        asyncio.create_task(load_emoji(url=emoji_link['url'], file_name=emoji_link['file_name']))
        for emoji_link in all_emojis_links.values()
    ]
    await asyncio.gather(*tasks)


if __name__ == '__main__':

    # Check if emojis folder exists
    if not os.path.exists('emojis'):
        os.makedirs('emojis')

    # Starts async downloading
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load_emojis())
