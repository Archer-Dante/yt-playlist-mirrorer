# from pytubefix import YouTube
#
# import requests
# from pytubefix import Playlist
# import wx
#
# video_url = 'https://www.youtube.com/watch?v=TxtPRxcUUlY'
# yt = YouTube(
#     video_url,
#     use_oauth=True,
#     allow_oauth_cache=True
# )
#
# # Попробуй выбрать другой поток, например, первый доступный
# stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
#
# # Скачивание видео
# if stream:
#     stream.download()
#     print("Видео успешно скачано!")
# else:
#     print("Не удалось найти доступные потоки.")


import asyncio
import subprocess
import time
from pytubefix import YouTube
from pytubefix import Playlist
import wx
from tqdm import tqdm
from moviepy.editor import *
import re
import ffpb


async def get_video_data(video_link):
    # URL видео
    video_url: str = video_link
    yt = YouTube(
        video_url,
        use_oauth=True,
        allow_oauth_cache=True
    )

    # Выбор потока
    # stream = yt.streams.filter(file_extension='mp4', progressive=True).order_by("resolution").desc().first()

    video_file = yt.streams.filter(file_extension='mp4', only_video=True).order_by("resolution").last()
    audio_file = yt.streams.filter(only_audio=True).last()

    print(f'\n"Video:", {video_file}')
    time.sleep(0.1)
    await proceed_download(yt, video_file, "видео")
    time.sleep(0.1)
    print(f'\n"Audio:" {audio_file}')
    time.sleep(0.1)
    await proceed_download(yt, audio_file, "аудио")

    # print(f'\n{yt.title}')

    return yt.title, yt.video_id


async def proceed_download(yt, download_object, file_type: str):

    # Коллбэк-функция для отслеживания прогресса
    def on_progress(stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining

        # Обновление прогресс-бара
        progress_bar.update(bytes_downloaded - progress_bar.n)

    # Подключение коллбэка
    yt.register_on_progress_callback(on_progress)
    # final_filename = f"{yt.title} ({yt.video_id}).{'mp4' if file_type == 'видео' else 'webm'}"

    # Скачивание видео с прогресс-баром
    if download_object:
        #{'temp_video.mp4' if file_type=='видео' else 'temp_audio.webm'}
        with tqdm(total=download_object.filesize, unit='B', unit_scale=True, desc=f"Загрузка {file_type}") as progress_bar:
            download_object.download(filename=f"{yt.video_id}{'.mp4' if file_type=='видео' else '.webm'}")
        print(f"\n{file_type[0].upper()+file_type[1::]} успешно скачано!")
    else:
        print(f"\nНе удалось найти доступные потоки для {file_type}.")


async def combine_video_audio(v_title, v_id):

    video_file = f'{v_id}.mp4'
    audio_file = f'{v_id}.webm'
    final_filename = re.sub(r'[<>:"/\\|?*]', ' ', v_title)
    final_filename = f'{final_filename}.mp4'

    command = [
        'ffmpeg',
        # '-init_hw_device', 'vulkan=vk:0',
        # '-hwaccel', 'vulkan',
        # '-hwaccel_output_format', 'vulkan',
        # '-c:v', 'h264_nvenc',
        '-hwaccel', 'cuda',
        '-i', video_file,  # Входной видео файл
        '-i', audio_file,   # Входной аудио файл
        '-c:v', 'copy',     # Копирование видеопотока
        '-c:a', 'aac',      # Кодек для аудио
        '-strict', 'experimental',  # Разрешение на использование экспериментальных кодеков,
        final_filename         # Выходной файл
    ]
    command2 = [
        f'-hwaccel cuda -i {video_file} -i {audio_file} -c:v copy, -c:a aac, -strict experimental {final_filename}'
    ]
    # Выполняем команду и дожидаемся её завершения
    # ffpb.main(argv=command, stream=final_filename)
    # await asyncio.to_thread(ffpb.main, argv=command, stream=sys.stdout)
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Кодирование завершено успешно.")
        print(result.stdout.decode())  # Выводим стандартный вывод
    except subprocess.CalledProcessError as e:
        print("Ошибка при кодировании:")
        print(e.stderr.decode())  # Выводим стандартный вывод ошибок
    os.remove(video_file)
    os.remove(audio_file)
    # os.rename("temp_result.mp4", final_filename )


async def main():
    videos: list = [
        'https://www.youtube.com/watch?v=2EkZjppztyo',
        'https://www.youtube.com/watch?v=jWorjBDcty4'
    ]

    for video in videos:
        v_title, v_id = await get_video_data(video)
        await combine_video_audio(v_title, v_id)


if __name__ == "__main__":
    asyncio.run(main())
















# from pytubefix import YouTube
# from tqdm import tqdm
# import os
# from moviepy.editor import VideoFileClip, AudioFileClip
#
#
# def download_video_and_audio(video_link):
#     # URL видео
#     video_url: str = video_link
#     yt = YouTube(
#         video_url,
#         use_oauth=True,
#         allow_oauth_cache=True
#     )
#
#     print(f'\n{yt.title}')
#
#     # Вывод доступных потоков для проверки
#     print("\nДоступные потоки:")
#     for stream in yt.streams.filter(file_extension='mp4'):
#         print(f"{stream.resolution} - {stream.mime_type} - {stream.filesize // (1024 * 1024)} MB")
#
#     # Выбор потока с максимальным качеством (видео только)
#     video_stream = yt.streams.filter(file_extension='mp4', only_video=True).order_by('resolution').desc().first()
#     audio_stream = yt.streams.filter(only_audio=True).first()
#
#     if video_stream and audio_stream:
#         print(f"Скачивание видео в разрешении {video_stream.resolution} и аудио...")
#
#         # Скачивание видео
#         video_filename = f"{yt.title}_video.mp4"
#         audio_filename = f"{yt.title}_audio.mp4"
#
#         video_stream.download(filename=video_filename)
#         audio_stream.download(filename=audio_filename)
#
#         print("Скачивание завершено!")
#
#         # Объединение видео и аудио
#         combine_video_audio(video_filename, audio_filename)
#
#     else:
#         print("Не удалось найти доступные потоки.")
#
#
# def combine_video_audio(video_file, audio_file):
#     # Объединение видео и аудио с помощью moviepy
#     final_filename = video_file.replace('_video.mp4', '_final.mp4')
#
#     video_clip = VideoFileClip(video_file)
#     audio_clip = AudioFileClip(audio_file)
#
#     final_clip = video_clip.set_audio(audio_clip)
#     final_clip.write_videofile(final_filename, codec='libx264', audio_codec='aac')
#
#     # Очистка временных файлов
#     video_clip.close()
#     audio_clip.close()
#     final_clip.close()
#
#     # Удаление временных файлов
#     os.remove(video_file)
#     os.remove(audio_file)
#
#
# videos: list = [
#     "https://www.youtube.com/watch?v=jWorjBDcty4",
#     'https://www.youtube.com/watch?v=2EkZjppztyo'
# ]
#
# for video in videos:
#     download_video_and_audio(video)




