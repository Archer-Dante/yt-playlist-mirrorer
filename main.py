import os

import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
from screeninfo import get_monitors
from func_menu import *


monitors = get_monitors()

mw = monitors[0].width
mh = monitors[0].height
w = 600
h = 700

dpg.create_context()
viewport = dpg.create_viewport(title='Software', width=w, height=h,
                               x_pos=(mw // 2 - w // 2 - 500),
                               y_pos=(mh // 2 - h // 2),
                               decorated=False,
                               resizable=False,
                               vsync=True,
                               clear_color=[0, 0, 0]
                               )

# with dpg.window(label="Window1", pos=(0,0)) as menu:
#     button1 = dpg.add_button(label="Press Me!")
#     slider_int = dpg.add_slider_int(label="Slide to the left!", width=100)
#     slider_float = dpg.add_slider_float(label="Slide to the right!", width=100)
#     pass
# button2 = dpg.add_button(label="Don't forget me!", parent=menu)
#


with dpg.font_registry():
    font_path = "DejaVuSansMono.ttf"
    with dpg.font(font_path, 22, tag="ArialFont", default_font=True):
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)


def print_me(sender):
    print(f"Menu Item: {sender}")


with dpg.viewport_menu_bar(tag="menu_line"):
    dpg.bind_font("ArialFont")

    with dpg.menu(label="Файл"):
        dpg.add_menu_item(label="Открыть", callback=print_me)

        with dpg.menu(label="Сохранить как.."):
            dpg.add_menu_item(label="Стандартный кэш", callback=print_me, check=True)
            dpg.add_menu_item(label="Таблица CSV", callback=print_me, check=True)
        with dpg.drawlist(width=140, height=7):
            dpg.draw_line((0, 5), (280, 5), color=(105, 105, 105, 255), thickness=2)
        dpg.add_menu_item(label="Закрыть", callback=close_app, check=True)

    with dpg.menu(label="Справка"):
        dpg.add_menu_item(label="Сообщить о проблеме", callback=callback_open_github_issue)
        dpg.add_menu_item(label="О программе", callback=print_me)



    with dpg.menu(label="Widget Items"):
        dpg.add_checkbox(label="Pick Me", callback=print_me)
        dpg.add_button(label="Press Me", callback=print_me)
        dpg.add_color_picker(label="Color Me", callback=print_me)

    dpg.add_spacer(width=230)  # Разделитель для размещения кнопок справа
    dpg.add_button(label="-", callback=minimize_callback, width=30, height=30, pos=[w-60,0])
    dpg.add_button(label="x", callback=close_app, width=30, height=30, pos=[w-30,0])


###################################################################
# Обработка перетаскивания через бар вместо заголовка окна
###################################################################

def cal_dow(sender, data):
    global title_bar_drag
    if dpg.is_mouse_button_down(0):
        x = data[0]
        y = data[1]
        if -25 <= y <= 100:
            title_bar_drag = True
        else:
            title_bar_drag = False


def cal(sender, data):
    global title_bar_drag
    if title_bar_drag:
        pos = dpg.get_viewport_pos()
        x = data[1]
        y = data[2]
        final_x = pos[0] + x
        final_y = pos[1] + y
        dpg.configure_viewport(viewport, x_pos=final_x, y_pos=final_y)


with dpg.handler_registry():
    dpg.add_mouse_drag_handler(0, callback=cal)
    dpg.add_mouse_move_handler(callback=cal_dow)

###################################################################

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
