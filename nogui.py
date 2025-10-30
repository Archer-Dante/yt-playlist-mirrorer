# import asyncio
# import os.path
# import shutil
# import subprocess
# import time
# from pytubefix import YouTube
# from pytubefix import Playlist
# # from pytubefix.helpers import reset_cache
# # import wx
# from tqdm import tqdm
# from moviepy.editor import *
# import re
# import yt_dlp
#
#
# debug = True
#
#
# async def get_video_data(video_link):
#     if debug: print(f'get into get_video_data_func')
#     video_url: str = video_link
#     yt = YouTube(
#         video_url,
#         # use_oauth=False,
#         # use_po_token=True,
#         # allow_oauth_cache=True
#         use_oauth=True,
#         allow_oauth_cache=True
#     )
#
#     if debug: print(f'get YT object by url: yt = Youtube()')
#     biggest_size_progressive = 0
#     biggest_size_non_progressive = 0
#     progressive_is_better: bool = False
#     # if debug:
#     #     for stream in yt.streams:
#     #         print(f'{stream.resolution} - {stream.mime_type}')
#     for stream in yt.streams.filter(file_extension='mp4', progressive=True):
#         if stream.filesize > biggest_size_progressive:
#             biggest_size_progressive = stream.filesize
#     for stream in yt.streams.filter(file_extension='mp4', progressive=False):
#         if stream.filesize > biggest_size_non_progressive:
#             biggest_size_non_progressive = stream.filesize
#
#     if biggest_size_non_progressive > biggest_size_progressive:
#         print(f"\nВероятно это видео было стримом.Запускаю раздельное скачивание...")
#         print(f"{biggest_size_non_progressive // (1024 * 1024)} MB > {biggest_size_progressive // (1024 * 1024)} MB")
#         progressive_is_better = False
#         if debug:
#             for stream in yt.streams.filter(file_extension='mp4', progressive=False):
#                 print(f"[Доступные потоки для скачивания в progressive=False]:")
#                 print(f"{stream.resolution} - {stream.mime_type} - {stream.filesize // (1024 * 1024)} MB")
#     else:
#         print(f"\nУ данного видео есть лучшее качество в комбинированном виде. Дополнительная обработка не требуется.")
#         print(f"{biggest_size_non_progressive // (1024 * 1024)} MB <= {biggest_size_progressive // (1024 * 1024)} MB")
#         progressive_is_better = True
#         if debug:
#             for stream in yt.streams.filter(file_extension='mp4', progressive=True):
#                 print(f"[Доступные потоки для скачивания в progressive=True]:")
#                 print(f"{stream.resolution} - {stream.mime_type} - {stream.filesize // (1024 * 1024)} MB")
#
#     if progressive_is_better:
#         video_file = yt.streams.filter(file_extension='mp4', progressive=True).order_by("resolution").last()
#         # print(f'\n"Video:", {video_file}')
#         time.sleep(0.05)
#         await proceed_download(yt, video_file, "video")
#
#         return yt.title, yt.video_id, progressive_is_better
#     else:
#         video_file = yt.streams.filter(file_extension='mp4', only_video=True).order_by("resolution").last()
#         audio_file = yt.streams.filter(only_audio=True).last()
#
#         # print(f'\n"Video:", {video_file}')
#         # time.sleep(0.05)
#         await proceed_download(yt, video_file, "video")
#         # time.sleep(0.05)
#         # print(f'\n"Audio:" {audio_file}')
#         # time.sleep(0.05)
#         await proceed_download(yt, audio_file, "audio")
#
#         return yt.title, yt.video_id, progressive_is_better
#
#
# async def proceed_download(yt, download_object, file_type: str):
#
#     # Коллбэк-функция для отслеживания прогресса
#     def on_progress(stream, chunk, bytes_remaining):
#         total_size = stream.filesize
#         bytes_downloaded = total_size - bytes_remaining
#
#         # Обновление прогресс-бара
#         progress_bar.update(bytes_downloaded - progress_bar.n)
#
#     # Подключение коллбэка
#     yt.register_on_progress_callback(on_progress)
#     # final_filename = f"{yt.title} ({yt.video_id}).{'mp4' if file_type == 'видео' else 'webm'}"
#
#     # Скачивание видео с прогресс-баром
#     if download_object:
#         #{'temp_video.mp4' if file_type=='видео' else 'temp_audio.webm'}
#         with tqdm(total=download_object.filesize, unit='B', unit_scale=True, desc=f"Загрузка {file_type}") as progress_bar:
#             download_object.download(filename=f"{yt.video_id}{'.mp4' if file_type=='video' else '.webm'}")
#         time.sleep(0.05)
#         print(f"{file_type[0].upper()+file_type[1::]} успешно скачано!")
#     else:
#         time.sleep(0.05)
#         print(f"Не удалось найти доступные потоки для {file_type}.")
#
#
# async def combine_video_audio(v_title, v_id):
#
#     video_file = f'{v_id}.mp4'
#     audio_file = f'{v_id}.webm'
#     # final_filename = f"{re.sub(r'[<>:"/\\|?*]', ' ', v_title)}.mp4" # python 3.12
#     sanitized_title = re.sub(r'[<>:"/\\|?*]', ' ', v_title)
#     final_filename = f"{sanitized_title}.mp4"
#     if debug: print(f"Итоговое название файла: {final_filename}")
#
#     command = [
#         'ffmpeg',
#         # '-init_hw_device', 'vulkan=vk:0',
#         # '-hwaccel', 'vulkan',
#         # '-hwaccel_output_format', 'vulkan',
#         # '-c:v', 'h264_nvenc',
#         '-hwaccel', 'cuda',
#         '-y',
#         '-i', video_file,  # Входной видео файл
#         '-i', audio_file,   # Входной аудио файл
#         '-c:v', 'copy',     # Копирование видеопотока
#         '-c:a', 'aac',      # Кодек для аудио
#         '-strict', 'experimental',  # Разрешение на использование экспериментальных кодеков,
#         final_filename         # Выходной файл
#     ]
#
#     await kill_ffmpeg() # на случай, если есть зависшие процессы ffmpeg
#     print(f"Идёт кодирование для ({final_filename})...")
#     try:
#         result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         print("Кодирование завершено успешно.")
#         print(result.stdout.decode())  # Выводим стандартный вывод
#     except subprocess.CalledProcessError as e:
#         print("Ошибка при кодировании:")
#         print(e.stderr.decode())  # Выводим стандартный вывод ошибок
#
#     if os.path.exists(video_file): os.remove(video_file)
#     if os.path.exists(audio_file): os.remove(audio_file)
#     # await just_rename("temp_result.mp4", final_filename)
#     print(f"Видео успешно собрано из аудио и видео потоков.")
#
#
# async def just_rename(from_filename, to_filename):
#     if os.path.exists(to_filename): os.remove(to_filename)
#     os.rename(from_filename, to_filename)
#
#
# async def kill_ffmpeg():
#     try:
#         # Завершает все процессы ffmpeg
#         result = subprocess.call(['taskkill', '/F', '/IM', 'ffmpeg.exe'])
#         if result == 0:
#             print("Все процессы ffmpeg были успешно завершены.")
#         else:
#             print(f"Не удалось завершить процессы ffmpeg. Код ошибки: {result}")
#     except Exception as e:
#         print(f"Ошибка при завершении процессов: {e}")
#
#
#
# with open('download.txt', 'r', encoding='utf-8') as file:
#     # Читаем все строки из файла
#     download_data = file.readlines()
#
# async def main():
#     print(f'\n')
#     # videos: list = [
#     #     #'https://www.youtube.com/watch?v=2EkZjppztyo',
#     #     #'https://www.youtube.com/watch?v=jWorjBDcty4',
#     #     'https://www.youtube.com/watch?v=dRIA9l29Uwg'
#     # ]
#     videos: list = download_data
#
#     for video in videos:
#         v_title, v_id, should_combine = await get_video_data(video)
#         if debug: print(f"should_combine: {should_combine}")
#         sanitized_title = re.sub(r'[<>:"/\\|?*]', ' ', v_title)
#         if should_combine:
#             # await just_rename(f"{v_id}.mp4", f"{re.sub(r'[<>:"/\\|?*]', ' ', v_title)}.mp4") # python 3.12
#             await just_rename(f"{v_id}.mp4", f"{sanitized_title}.mp4")
#         else:
#             await combine_video_audio(v_title, v_id)
#         destination = "downloads"
#         os.makedirs(os.path.dirname(destination), exist_ok=True)
#         shutil.move(f"{sanitized_title}.mp4", f"{destination}/{sanitized_title}.mp4")
#
#
#
# # if __name__ == "__main__":
# #     asyncio.run(main())
#
#
# asyncio.run(main())
import requests
from yt_dlp import YoutubeDL
import re
import sqlite3




# def erase_db_on_run():
#     import os
#     os.remove("data.db") if os.path.exists("data.db") else None
#
#
# erase_db_on_run()


cls_red = "\033[31m"
cls_green = "\033[32m"
cls_blue = "\033[34m"
cls_pink = "\033[35m"
cls_reset = "\033[0m"

# Настройки для yt-dlp
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',  # Выбираем лучшее качество видео + аудио
    'outtmpl': 'downloads/%(title)s [%(id)s][%(uploader_id)s].%(ext)s',  # Шаблон имени файла
    'merge_output_format': 'mp4',  # Формат выходного файла
    'quiet': False,  # Отключить лишний вывод
    'no_warnings': True,  # Отключить предупреждения
    'noplaylist': False,  # Отключает скачивание плейлиста, даже если он представлен в ссылке
    'extract_flat': True,  # Сокращает количество данных до минимума, равноценно process=False
    'just_sync': True,  # КАСТОМ - Проводить синхронизацию без скачивания
    'download_playlist': True,
}


def sql_magic(**kwargs):
    pl_id = kwargs.get('pl_id')
    pl_title = kwargs.get('pl_title')
    v_id = kwargs.get('v_id')
    v_title = kwargs.get('v_title')
    v_duration = kwargs.get('v_duration')
    v_author = kwargs.get('v_author')
    v_desc = kwargs.get('v_desc')
    v_thumb = kwargs.get('image')

    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS `playlist_{pl_id}` (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pl_id TEXT,
        pl_title TEXT,
        v_id TEXT UNIQUE NOT NULL,
        v_title TEXT NOT NULL,
        v_duration INTEGER,
        v_author TEXT,
        v_desc TEXT,
        v_thumb BLOB
    )
    """)

    cursor.execute(f"SELECT 1 FROM `playlist_{pl_id}` WHERE v_id = ?", [v_id])
    if cursor.fetchone():
        print(f"{cls_blue}#{kwargs.get('entry')}{cls_reset} Такое видео {cls_red}[{v_id}]{cls_reset} уже есть в плейлисте {cls_blue}[{pl_title}]{cls_reset}")
        pass
    else:
        cursor.execute(
            f"INSERT INTO `playlist_{pl_id}` (pl_id, pl_title, v_id, v_title, v_duration, v_author, v_desc, v_thumb) VALUES (?,?,?,?,?,?,?,?)",
            (pl_id, pl_title, v_id, v_title, v_duration, v_author, v_desc, v_thumb))
        print(f"{cls_blue}#{kwargs.get('entry')}{cls_reset} Видео {cls_green}[{v_id} | {v_title}]{cls_reset} успешно добавлен в Базу Данных для плейлиста {cls_blue}[{pl_title}]{cls_reset}!")

    connection.commit()
    connection.close()


def get_thumb_data(info):
    video_thumb = {
        "max_res": '',
        # "format": '',
        "link": ''
    }
    thumbnails = info.get("thumbnails")
    for preview in thumbnails:
        # res = preview.get("resolution")
        # if res is None: continue
        # print(res)
        # # перемножение Ширины и Высоты
        # pixels = eval(res.replace('x', '*')) if len(res) < 10 else None
        # # отсекает невалидные значения пикселей и непрямой формат ссылок или иные форматы
        # if pixels is not None and preview.get('url').endswith(".jpg"):
        #     last_pixels = video_thumb['max_res']
        #     if last_pixels == "" or int(last_pixels) < int(pixels):
        #         video_thumb['max_res'] = pixels
        #         video_thumb['link'] = preview.get('url')
        #         video_thumb['format'] = 'jpg'
        #         print(f'Новое максимальное разрешение: {video_thumb["max_res"]} - [{preview.get("resolution")}]')
        #         print(video_thumb)

        pixels = preview.get("width") * preview.get("height")

        last_pixels = video_thumb['max_res']
        if last_pixels == "" or int(last_pixels) < int(pixels):
            video_thumb['max_res'] = pixels
            video_thumb['link'] = preview.get('url')  # [0:preview.get('url').find("?")]
            # print(f'Новое максимальное разрешение: {video_thumb["max_res"]} - [{preview.get("width")}x{preview.get("height")}]')

    # print(video_thumb)
    img_binary = requests.get(video_thumb['link']).content
    return img_binary


def download_video(video_url):
    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(video_url, download=False)  # получаем информацию о видео
        with open('debug.txt', 'a', encoding='utf-8') as file:
            file.write(str(info) + "\n")

        video_id = info.get('id')
        video_title: str = ""
        playlist_title: str = ""
        video_uploader = info.get('uploader_id')

        # когда из видео, которое находится в плейлисте
        # блок отвечающий за заполнение данных о плейлисте для видео, у которых есть референс на плейлист (является частью плейлиста)
        # с обычными видео такого не будет в принципе
        if video_url.find('&list=') > 0 and ydl_opts['download_playlist'] == True:
            print("Установлено скачивание плейлиста.")
            print("Плейлист обнаружен в ссылке.")
            playlist_id = video_url[video_url.find("list=") + 5::]
            playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'
            playlist_info = ydl.extract_info(playlist_url.replace("\n",""), download=True, process=True)
            playlist_title = playlist_info.get('title')
            # подмена url, так как ydl плохо работает с ссылками &list и не применяет параметра
            video_url = playlist_url
            for i, entry in enumerate(playlist_info.get("entries")):
                # print("ТУТ!", entry)
                if entry.get('uploader_id') is None and entry.get('channel_id') is None:
                    print(f"{cls_blue}#{i}{cls_reset} Видео {cls_red}[{entry.get('id')}]{cls_reset} больше недоступно или удалено {cls_blue}[{playlist_title}]{cls_reset}")
                    continue
                sql_magic(**{
                    "pl_id": playlist_id.replace("\n",""),
                    "pl_title": playlist_title.replace("\n",""),
                    "v_id": entry.get('id').replace("\n",""),
                    "v_title": entry.get('title').replace("\n",""),
                    "v_desc": entry.get('title').replace("\n",""),
                    "v_author": entry.get('uploader_id').replace("\n","") if entry.get('uploader_id') else entry.get('channel_id').replace("\n",""),
                    "v_duration": entry.get('duration'),
                    "image": get_thumb_data(entry),
                    "entry": i
                })

            sanitized_title = re.sub(r'[<>:"/\\|?*]', ' ', playlist_title)
            ydl_opts['outtmpl']['default'] = ydl_opts['outtmpl']['default'].replace("/", "/" + sanitized_title + "/%(playlist_autonumber)s. ", 1)
            if ydl_opts['just_sync']:
                # get_thumb_data(info)
                # sql_magic(**{"pl_id": "value1", "pl_title": playlist_title, "param3": "value3"})
                pass

        # # когда со страницы плейлиста
        # if video_url.find('?list') > 0:
        #     playlist_title = info.get('title')
        #     video_title = info.get('entries')[0].get('title')
        #
        #     sanitized_title = re.sub(r'[<>:"/\\|?*]', ' ', playlist_title)
        #     ydl_opts['outtmpl']['default'] = ydl_opts['outtmpl']['default'].replace("/", "/" + sanitized_title + "/%(playlist_autonumber)s. ", 1)
        #     if ydl_opts['just_sync']:
        #         print("\nСИНХРОНИЗАЦИЯ ВКЛЮЧЕНА")
        #         # get_thumb_data(info)
        #         # sql_magic(**{"pl_id": "value1", "pl_title": playlist_title, "param3": "value3"})
        #
        # # print(f"Скачивание: {video_title} [{video_id}]")

        def progress_hook(d):
            if d['status'] == 'downloading':
                filename = d['filename']
                downloaded_bytes = d.get('_downloaded_bytes_str', 'N/A')
                total_bytes = d.get('_total_bytes_str', 'N/A')
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                print(f"\r{filename}: {percent} [{downloaded_bytes}/{total_bytes}] @ {speed} ETA: {eta}", end="")

        ydl_opts['progress_hooks'] = [progress_hook]

        def process_download(current_try):
            try:
                print("Запуск скачивания...")
                ydl.download([video_url])
            except Exception as e:
                if str(e).find("HTTPSConnectionPool") or str(e).find("Read timed out"):
                    print(f'\nОшибка!')
                    current_try += 1
                    if current_try <= max_tries:
                        print(f'\nПопытка загрузки {current_try} из {max_tries}')
                        process_download(current_try)
                    else:
                        print(f'Ошибка: Достигнуто максимальное количество попыток скачивания.')
                else:
                    print(f'Непредвиденная ошибка: {e}')

        current_try = 1
        max_tries = 5
        process_download(current_try)

        print(f"\nЗагрузка завершена: {video_title} [{video_id}][{video_uploader}].{ydl_opts['merge_output_format']}")


if __name__ == "__main__":
    # сброс дебаг инфы
    with open('log.txt', 'w', encoding='utf-8') as file1:
        pass
    # парс ссылок из файла
    with open('download.txt', 'r', encoding='utf-8') as file2:
        download_data = file2.readlines()

    for url in download_data:
        # check_playlist(url)
        download_video(url)
