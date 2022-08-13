import glob
from concurrent.futures import ThreadPoolExecutor
import m3u8
import os
import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 "
    "Safari/537.36"
}


def download_ts(url, key, i):
    r = requests.get(url, headers=headers)
    data = r.content
    data = AESDecrypt(data, key=key)
    with open(f"tmp/{i:0>5d}.ts", "ab") as f:
        f.write(data)
    print(f"\r{i:0>5d}.ts Downloaded ", end=" ")


def get_real_url(url):
    playlist = m3u8.load(uri=url, headers=headers)
    return playlist.playlists[0].absolute_uri


def AESDecrypt(cipher_text, key):
    cipher_text = pad(data_to_pad=cipher_text, block_size=AES.block_size)
    aes = AES.new(key=key, mode=AES.MODE_CBC, iv=key)
    cipher_text = aes.decrypt(cipher_text)
    return cipher_text


def download_m3u8_video(url, save_name, max_workers=10):
    if not os.path.exists("tmp"):
        os.mkdir('tmp')
    real_url = get_real_url(url)
    playlist = m3u8.load(uri=real_url, headers=headers)
    key = requests.get(playlist.keys[-1].uri, headers=headers).content
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for i, seg in enumerate(playlist.segments):
            pool.submit(download_ts, seg.absolute_uri, key, i)
    with open(save_name, 'wb') as fw:
        files = glob.glob('tmp/*.ts')
    for file in files:
        with open(file, 'rb') as fr:
            fw.write(fr.read())
    print(f'\r{file} Merged ! total :{len(files)}', end=" ")
    os.remove(file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    download_m3u8_video('https://vod8.wenshibaowenbei.com/20210628/g4yNLlI7/index.m3u8', ' Enter the house .mp4')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
