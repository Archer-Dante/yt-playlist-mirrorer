import dearpygui.dearpygui as dpg
import webbrowser

def close_app():
    dpg.stop_dearpygui()

def minimize_callback():
    dpg.configure_item("Main Window", show=False)

def callback_open_github_issue():
    webbrowser.open("https://github.com/Archer-Dante/yt-playlist-mirrorer/issues")