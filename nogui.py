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


from yt_dlp import YoutubeDL
import re

# Настройки для yt-dlp
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',                   # Выбираем лучшее качество видео + аудио
    'outtmpl': 'downloads/%(title)s [%(id)s].%(ext)s',      # Шаблон имени файла
    'merge_output_format': 'mp4',                           # Формат выходного файла
    'quiet': False,                                         # Отключить лишний вывод
    'no_warnings': True,                                    # Отключить предупреждения
    'noplaylist': True,                                     # Отключает скачивание плейлиста, даже если он представлен в ссылке
    'extract_flat': True,                                   # Отключает работу с видео, только вытаскивание данных
}


def check_playlist(video_url):
    with YoutubeDL(ydl_opts) as ydl:
        if video_url.find("list=") and (video_url.find('youtube.com') or video_url.find('youtu.be')):
            print(f'Обнаружен плейлист, вытаскиваем его заголовок')
            pl_url = 'https://www.youtube.com/playlist?' + video_url[video_url.find('list='):video_url.find('list=') + 39]
            print(f'Непосредственный адрес плейлиста: {pl_url}')
            pl_info = ydl.extract_info(pl_url, download=False)  # Получение названия плейлиста
            print(f'Название плейлиста: {pl_info.get("title")}')
            print(ydl_opts)
            # избавляемся от спец-символов, с которыми папки нельзя создать
            sanitized_title = re.sub(r'[<>:"/\\|?*]', ' ', pl_info.get("title"))
            ydl_opts['outtmpl']['default'] = ydl_opts['outtmpl']['default'].replace("/", "/" + sanitized_title + "/",1)
            ydl_opts['extract_flat'] = False # возврат работы с видео
            # print(f'Измененная строка: {ydl_opts["outtmpl"]}')
            print(ydl_opts)


def download_video(video_url):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)  # получаем информацию о видео
        video_id = info.get('id')
        video_title = info.get('title')
        print(f"Скачивание: {video_title} [{video_id}]")

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
                ydl.download([video_url])  # Скачиваем видео
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

        print(f"\nЗагрузка завершена: {video_title} [{video_id}].{ydl_opts['merge_output_format']}")


if __name__ == "__main__":
    # url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    # url = "https://www.youtube.com/watch?app=desktop&v=KO0wNQdiivs&list=PLuuJ7EJSjEfMETY8txzRpXHPH08Eg7kA6&sttick=0"
    # url = "https://www.youtube.com/watch?v=lopgTEXgDYY&list=PLc52h9BK94Hn8cMAIvZOOvHKZVkP3cN1T"
    # url = "https://www.youtube.com/watch?v=ygTZZpVkmKg"

    with open('download.txt', 'r', encoding='utf-8') as file:
        download_data = file.readlines()

    for url in download_data:
        check_playlist(url)
        download_video(url)




















