import flet as ft
from flet import RoundedRectangleBorder
from flet import BorderSide
from fletcarousel import BasicHorizontalCarousel, AutoCycle

import requests
import argparse
import time, threading

from screeninfo import get_monitors
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

global language, driver, imageURL, appURL, STRAPI_ID, seconds, current_route
STRAPI_URL = "http://localhost:1337/"
STRAPI_URL = "https://c873-2001-4b98-dc2-41-216-3eff-febb-9597.eu.ngrok.io/"
STRAPI_ID = 2 # (0:ANIMAL, 0:VQA, 1:ETRO) index of the current project
language="EN"
driver = None
TIMEOUT = 120
seconds = TIMEOUT


def main(page: ft.Page):    # check if no mouse click from the user
    def update_timer():
        global seconds
        print("[+] Starting timer:", seconds)
        while True:
            while seconds:
                time.sleep(1)
                seconds -= 1
            if(seconds==0):
                print("[+] Timer expired")
                closeDemo(None)
                if(current_route!="/"): # IF NOT ALREADY IN /
                    page.go('/')
                seconds=TIMEOUT
                
    def listenMouse(e):
        global seconds
        seconds= TIMEOUT
        print("[!] Reset timer", seconds)
        
    th = threading.Thread(target=update_timer, args=(), daemon=True)
    th.start()
    
    """
    Set of main GUI elements that requiered to be dynamic
    """
    txt_title = ft.Text(value="", color="#2250c6", size=40, font_family="Rhetorik", width=800)
    txt_topic = ft.Text(value="",color="#65C0B5", size=14, font_family="Plain")
    txt_explain1 = ft.Text(value="", color="#1A202C", font_family="Plain", size=14, width=600)
    txt_start_demo = ft.Text(value="", color="#ffffff", size=28, font_family="Plain")
    txt_title2 = ft.Text(value="", color="#ffffff", size=40, font_family="Rhetorik", width=600)
    txt_topic2 = ft.Text(value="", color="#65C0B5", size=14, font_family="Plain")
    txt_explain2 = ft.Text(width=600,value="", color="#ffffff", font_family="Plain", size=14)
    txt_learnmore = ft.ElevatedButton(
                        text="",
                        icon=ft.icons.LINK_ROUNDED,
                        icon_color="#ffffff",
                        on_click=lambda _: more(_),
                        style=
                        ft.ButtonStyle(
                            color="#ffffff",
                            padding=10,
                            bgcolor={ft.MaterialState.DEFAULT: "#2153d1", ft.MaterialState.HOVERED: ft.colors.BLUE},
                            side={
                                ft.MaterialState.DEFAULT: BorderSide(1, ft.colors.BLUE),
                                ft.MaterialState.HOVERED: BorderSide(2, ft.colors.BLUE),
                            },
                            overlay_color=ft.colors.TRANSPARENT,
                            elevation={"pressed": 0, "": 1},
                            animation_duration=500,
                            shape={
                                ft.MaterialState.DEFAULT: RoundedRectangleBorder(radius=50),
                            },
                        ),
                    )
    
    """
    Set of main functions
    """    
    def changeText():
        """Change the text language based on a given input string (EN, NL or FR)
        """
        global language, imageURL, appURL, STRAPI_URL
        url = STRAPI_URL + "demos/"
        
        print("[+] Getting data from STRAPI")
        if(language=="EN"):
            url = STRAPI_URL + "api/demos?locale=en"
        elif(language=="NL"):
            url = STRAPI_URL + "api/demos?locale=nl"
        elif(language=="FR"):
            url = STRAPI_URL + "api/demos?locale=fr-FR"

        try:
            response = requests.get(url) # Call the STRAPI API        
            response_json = response.json()

            # TEXT
            txt_title.value = response_json["data"][STRAPI_ID]["attributes"]["title"]
            txt_topic.value = response_json["data"][STRAPI_ID]["attributes"]["topic"]
            txt_explain1.value = response_json["data"][STRAPI_ID]["attributes"]["explanation_short"]
            txt_start_demo.value = response_json["data"][STRAPI_ID]["attributes"]["button_demo_start"]
            txt_title2.value = response_json["data"][STRAPI_ID]["attributes"]["title"]
            txt_topic2.value = response_json["data"][STRAPI_ID]["attributes"]["topic"]
            txt_explain2.value = response_json["data"][STRAPI_ID]["attributes"]["explanation"]
            txt_learnmore.text = response_json["data"][STRAPI_ID]["attributes"]["learn_more"]
            # APP URL
            appURL = response_json["data"][STRAPI_ID]["attributes"]["appURL"]
            # IMAGE
            url_img = STRAPI_URL + "api/demos?populate=*"
            response = requests.get(url_img) # Call the STRAPI API
            response_json = response.json()
            imageURL = STRAPI_URL[:-1] + response_json["data"][STRAPI_ID]["attributes"]["image"]["data"]["attributes"]["formats"]["medium"]["url"]
        except:
            print("[!] Error - CMS is offline")

    def loadLang():
        """Base on the value of the global var 'language', it load the set of text in the correct language
        """
        changeText()
    
    def more(e):
        """Display the About page (About FARI)

        Args:
            e (error): Should not occur, trust me
        """
        global language, seconds
        seconds= TIMEOUT
        closeDemo(e)
        page.go('/more')
        pass
    
    def home(e):
        """Display the Home page (Main page with the a explaination of the demo)

        Args:
            e (error): Should not occur, trust me
        """
        global language, seconds
        seconds= TIMEOUT
        language=e
        loadLang()
        page.go("/home")   

    def demo(e):
        """Display the Demo page (Back page: Close and top bar & Front page: The Selenium demo) 

        Args:
            e (error): Should not occur, trust me
        """
        global driver, appURL, seconds
        seconds=420
        page.go("/demo")
        options = Options()
        URL = "--app=" + appURL
        options.add_argument(URL)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("silent-debugger-extension-api")
        options.add_argument("no-default-browser-check")
        options.add_argument("disable-windows10-custom-titlebar")
        options.add_argument("disable-auto-maximize-for-tests")
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 980)
        driver.set_window_position(0, 120, windowHandle='current')
        
    def closeDemo(e):
        """Close the Front demo page (Selenium)

        Args:
            e (error): Should not occur, trust me
        """
        global driver
        try:
            driver.close()
            driver = None
        except:
            print("[!] - Error while closing demo")
        page.go("/home")


    def back(e):
        global language, seconds
        seconds= TIMEOUT
        closeDemo(e)
        page.go("/home")
    
    def view_pop(view):
        """Change the current view

        Args:
            view (Flet view): New view
        """
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    
    #===============================================================================
    # UIX & GUI DEFINITION
    #===============================================================================  
    def route_change(route):
        """Display the correct page based on the route choose by the user ("/", "/demo", "/how", "/about")

        Args:
            route (string): The URL of the desired page
        """  
        global imageURL, current_route      
        current_route = route
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                bgcolor= "#2250c6",
                controls=
                [   
                    ft.Container(
                            margin=(250),
                            alignment=ft.alignment.center,
                            content=       
                                ft.Column(
                                    spacing=(100),
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Row(
                                            [
                                                ft.Text(value="Choose your language to continue", color="#ffffff", size=30, font_family="Rhetorik")
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                        ),
                                        ft.Row(
                                            spacing=(120),
                                            controls=
                                            [
                                                ft.OutlinedButton(
                                                    width=280,
                                                    content=ft.Container(
                                                    border_radius=50,
                                                    content=ft.Row(
                                                        spacing=(20),
                                                        controls=
                                                        [
                                                            ft.Image(
                                                                src=f"/img/gb.png",
                                                                fit=ft.ImageFit.FIT_HEIGHT,
                                                                height=50,
                                                                width=50,
                                                                border_radius=25,
                                                            ),
                                                            ft.Text(value="English", color="#ffffff", size=20, font_family="Plain")
                                                        ],
                                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                                    ),),
                                                    style=
                                                    ft.ButtonStyle(
                                                        padding=20,
                                                        bgcolor={ft.MaterialState.DEFAULT: "#2153d1", ft.MaterialState.HOVERED: ft.colors.BLUE},
                                                        side={
                                                            ft.MaterialState.DEFAULT: BorderSide(1, ft.colors.BLUE),
                                                            ft.MaterialState.HOVERED: BorderSide(2, ft.colors.BLUE),
                                                        },
                                                        overlay_color=ft.colors.TRANSPARENT,
                                                        elevation={"pressed": 0, "": 1},
                                                        animation_duration=500,
                                                        shape={
                                                            ft.MaterialState.DEFAULT: RoundedRectangleBorder(radius=50),
                                                        },
                                                    ),
                                                    data = "EN",
                                                    on_click=lambda e: home(e.control.data),
                                                ),
                                                ft.OutlinedButton(
                                                    width=280,
                                                    content=ft.Container(
                                                    border_radius=50,
                                                    content=ft.Row(
                                                        spacing=(20),
                                                        controls=
                                                        [
                                                            ft.Image(
                                                                src=f"/img/nl.png",
                                                                fit=ft.ImageFit.FIT_HEIGHT,
                                                                height=50,
                                                                width=50,
                                                                border_radius=25,
                                                            ),
                                                            ft.Text(value="Nederlands", color="#ffffff", size=20, font_family="Plain")
                                                        ],
                                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                                    ),),
                                                    style=
                                                    ft.ButtonStyle(
                                                        padding=20,
                                                        bgcolor={ft.MaterialState.DEFAULT: "#2153d1", ft.MaterialState.HOVERED: ft.colors.BLUE},
                                                        side={
                                                            ft.MaterialState.DEFAULT: BorderSide(1, ft.colors.BLUE),
                                                            ft.MaterialState.HOVERED: BorderSide(2, ft.colors.BLUE),
                                                        },
                                                        overlay_color=ft.colors.TRANSPARENT,
                                                        elevation={"pressed": 0, "": 1},
                                                        animation_duration=500,
                                                        shape={
                                                            ft.MaterialState.DEFAULT: RoundedRectangleBorder(radius=50),
                                                        },
                                                    ),
                                                    data = "NL",
                                                    on_click=lambda e: home(e.control.data),
                                                ),
                                                ft.OutlinedButton(
                                                    width=280,
                                                    content=ft.Container(
                                                    border_radius=50,
                                                    content=ft.Row(
                                                        spacing=(20),
                                                        controls=
                                                        [
                                                            ft.Image(
                                                                src=f"/img/fr.png",
                                                                fit=ft.ImageFit.FIT_HEIGHT,
                                                                height=50,
                                                                width=50,
                                                                border_radius=25,
                                                            ),
                                                            ft.Text(value="Français", color="#ffffff", size=20, font_family="Plain")
                                                        ],
                                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                                    ),),
                                                    style=
                                                    ft.ButtonStyle(
                                                        padding=20,
                                                        bgcolor={ft.MaterialState.DEFAULT: "#2153d1", ft.MaterialState.HOVERED: ft.colors.BLUE},
                                                        side={
                                                            ft.MaterialState.DEFAULT: BorderSide(1, ft.colors.BLUE),
                                                            ft.MaterialState.HOVERED: BorderSide(2, ft.colors.BLUE),
                                                        },
                                                        overlay_color=ft.colors.TRANSPARENT,
                                                        elevation={"pressed": 0, "": 1},
                                                        animation_duration=500,
                                                        shape={
                                                            ft.MaterialState.DEFAULT: RoundedRectangleBorder(radius=50),
                                                        },
                                                    ),
                                                    data = "FR",
                                                    on_click=lambda e: home(e.control.data),
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                        ),
                                    ],
                                )
                            
                    )
                ],
            )
        )
        
        if page.route == "/home":
            page.views.append(
                ft.View(
                    "/home",
                    bgcolor="#FFFFFF",
                    controls=
                    [
                        ft.Row(
                            controls=[
                                ft.TextButton(icon=ft.icons.ARROW_BACK, icon_color="#2250c6", on_click=lambda _: page.go("/")),
                                ft.TextButton(
                                    text=language, 
                                    icon=ft.icons.LANGUAGE, 
                                    on_hover=listenMouse,
                                    icon_color="#575757", 
                                    on_click=lambda _: page.go("/"),
                                    style=ft.ButtonStyle(
                                        color="#575757",
                                        shape=ft.RoundedRectangleBorder(radius=20),
                                        padding=10,
                                        bgcolor={ft.MaterialState.HOVERED: "#e4e4e4", ft.MaterialState.DEFAULT: "#e4e4e4"},
                                    ),
                                ),     
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Container(
                            margin=(130),
                            alignment=ft.alignment.center,
                            on_hover=listenMouse,
                            content=
                            ft.Row(
                                spacing=(40),
                                controls=[
                                ft.Column(
                                    spacing=(20),
                                    controls=[
                                        txt_title,
                                        txt_topic,
                                        txt_explain1,
                                        txt_learnmore,
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                ft.ElevatedButton(
                                    content=
                                    ft.Container(
                                        border_radius=50,
                                        content=ft.Row(
                                            spacing=(20),
                                            controls=
                                            [
                                                txt_start_demo,
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                        ),
                                    ),
                                    style=ft.ButtonStyle(
                                        shape=ft.CircleBorder(), 
                                        padding=180,
                                        bgcolor={ft.MaterialState.DEFAULT: "#2250c6", ft.MaterialState.HOVERED: ft.colors.BLUE},
                                        side={
                                            ft.MaterialState.DEFAULT: BorderSide(1, "#2250c6"),
                                            ft.MaterialState.HOVERED: BorderSide(4, ft.colors.BLUE),
                                        },
                                    ),
                                    on_click=demo
                                ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            )
                        ), 
                        ft.Container(
                            height=100,
                            on_hover=listenMouse,
                        ),
                        ft.Container(
                            alignment=ft.alignment.bottom_center,
                            border={
                                ft.MaterialState.DEFAULT: BorderSide(1, ft.colors.BLUE_GREY),
                                ft.MaterialState.HOVERED: BorderSide(2, ft.colors.BLUE_GREY),
                            },
                            on_hover=listenMouse,
                            content=
                            ft.Column(
                                controls=[
                                    ft.Divider(height=9, thickness=1, color="#C6C6C6"),
                                    ft.Container(
                                        height=20,
                                    ),
                                    ft.Row(
                                        spacing=(40),
                                        controls=[
                                            BasicHorizontalCarousel(
                                                page=page,
                                                items_count=5,
                                                #auto_cycle=AutoCycle(duration=1),
                                                items=[
                                                    ft.Container(
                                                        height=50,
                                                        width=300,
                                                        content=
                                                        ft.Image(
                                                            src=f"/img/pp.svg",
                                                            fit=ft.ImageFit.FIT_HEIGHT,
                                                            color="#c5c5c5",
                                                            height=50,
                                                        ),
                                                    ),
                                                    ft.Container(
                                                        height=50,
                                                        width=300,
                                                        content=
                                                        ft.Image(
                                                            src=f"/img/solvay.svg",
                                                            fit=ft.ImageFit.FIT_HEIGHT,
                                                            color="#c5c5c5",
                                                            height=50,
                                                        ),
                                                    ),
                                                    ft.Container(
                                                        height=50,
                                                        width=300,
                                                        content=
                                                        ft.Image(
                                                            src=f"/img/mlg.svg",
                                                            fit=ft.ImageFit.FIT_HEIGHT,
                                                            color="#c5c5c5",
                                                            height=50,
                                                        ),
                                                    ),
                                                    ft.Container(
                                                        height=50,
                                                        width=300,
                                                        content=
                                                        ft.Image(
                                                            src=f"/img/smit.svg",
                                                            fit=ft.ImageFit.FIT_HEIGHT,
                                                            color="#c5c5c5",
                                                            height=50,
                                                        ),
                                                    ),
                                                    ft.Container(
                                                        height=50,
                                                        width=300,
                                                        content=
                                                        ft.Image(
                                                            src=f"/img/lsts.svg",
                                                            fit=ft.ImageFit.FIT_HEIGHT,
                                                            color="#c5c5c5",
                                                            height=50,
                                                        ),
                                                    ),
                                                    ft.Container(
                                                        height=50,
                                                        width=300,
                                                        content=
                                                        ft.Image(
                                                            src=f"/img/air.svg",
                                                            fit=ft.ImageFit.FIT_HEIGHT,
                                                            color="#c5c5c5",
                                                            height=50,
                                                        ),
                                                    ),
                                                    ft.Container(
                                                        height=50,
                                                        width=300,
                                                        content=
                                                        ft.Image(
                                                            src=f"/img/brubotics.svg",
                                                            fit=ft.ImageFit.FIT_HEIGHT,
                                                            color="#c5c5c5",
                                                            height=50,
                                                        ),
                                                    ),
                                                    ft.Container(
                                                        height=50,
                                                        width=300,
                                                        content=
                                                        ft.Image(
                                                            src=f"/img/etro.svg",
                                                            fit=ft.ImageFit.FIT_HEIGHT,
                                                            color="#c5c5c5",
                                                            height=50,
                                                        ),
                                                    ),

                                                ],
                                                buttons=[
                                                    ft.TextButton(
                                                        icon=ft.icons.NAVIGATE_BEFORE,
                                                        icon_color="#2250c6"
                                                    ),
                                                    ft.TextButton(
                                                        icon=ft.icons.NAVIGATE_NEXT,
                                                        icon_color="#2250c6"
                                                    )
                                                ],
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                items_alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        
                                    )
                                    
                                ]
                            ),
                        )
                    ],
                )
            )
        if page.route == "/more":
            seconds = 300
            page.views.append(
                ft.View(
                    "/more",
                    bgcolor= "#2250c6",
                    controls=
                    [
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    icon=ft.icons.ARROW_BACK, 
                                    icon_color="#ffffff", 
                                    on_click=lambda _: page.go("/home"),
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=20),
                                        padding=10,
                                    ),
                                ),    
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Container(
                            margin=(130),
                            alignment=ft.alignment.center,
                            on_hover=listenMouse,
                            content=
                            ft.Row(
                                spacing=(70),
                                controls=[
                                ft.Column(
                                    spacing=(20),
                                    controls=[
                                        txt_title2,
                                        txt_topic2,
                                        txt_explain2,    
                                    ],
                                    
                                ),
                                ft.Image(
                                    src=imageURL,
                                    fit=ft.ImageFit.COVER,
                                    width=700,
                                ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            )
                        ),
                        
                    ],
                )
            )
        
        if page.route == "/demo":
            page.views.append(
                ft.View(
                    "/demo",
                    bgcolor="#2250c6",
                    controls=
                    [
                        ft.Row(
                            height=100,
                            controls=[
                                ft.TextButton(icon=ft.icons.ARROW_BACK, icon_color="#ffffff", on_click=lambda _: back(_)),
                                ft.Image(
                                    src=f"/img/logo_w.png",
                                    fit=ft.ImageFit.FIT_HEIGHT,
                                    color="#ffffff",
                                    height=50,
                                ),
                                txt_learnmore,   
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        
                    ]
                )
            )
            
        page.update()

    #===============================================================================
    # MAIN CODE & GLOBAL VAR
    #===============================================================================    
    page.title = "FARI - Welcome screen"
    page.fonts = {
        "Plain": "/fonts/Plain-Regular.otf",
        "Rhetorik": "/fonts/RhetorikSerifTrial-Regular.ttf"
    }
    
    m = get_monitors()
    h = m[0].height
    w = m[0].width
        
    page.window_width = w       
    page.window_height = h
    page.window_resizable = False

    page.update()  
    
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Running demo welcome page')
    parser.add_argument('--id', required=True, help='the Scrapi API ID of the demo')
    args = parser.parse_args()
    STRAPI_ID = int(args.id)

    ft.app(target=main, port=8550, assets_dir="assets")
    