import flet as ft
from auth.authapp import AuthApp
from main import main as youtube_app
import webbrowser
import threading
import time
import logging
from utils import get_resource_path, find_free_port, setup_logging

# Setup logging
setup_logging()

def main(page: ft.Page):
    def auth_callback(auth_token):
        try:
            if auth_token:
                page.clean()  # 페이지 초기화
                youtube_app(page)  # 유튜브 앱 실행
            else:
                page.add(ft.Text("인증 실패"))  # 인증 실패시 에러 메시지 출력
        except Exception as e:
            logging.error(f"Error in auth_callback: {str(e)}")
            page.add(ft.Text(f"오류가 발생했습니다: {str(e)}"))
    
    auth_app = AuthApp(auth_callback)
    auth_app.build(page)

def open_browser(port):
    try:
        time.sleep(1.5)  # Wait for server to start
        webbrowser.open(f'http://localhost:{port}')
    except Exception as e:
        logging.error(f"Error opening browser: {str(e)}")

def start_app():
    port = find_free_port()
    # Start browser thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    try:
        ft.app(
            target=main,
            view=ft.AppView.WEB_BROWSER,
            port=port,
            web_renderer=ft.WebRenderer.HTML,
            assets_dir=get_resource_path("assets")
        )
    except Exception as e:
        logging.error(f"Error starting app: {str(e)}")
        raise

if __name__ == "__main__":
    start_app()


##########################################################################################
# import flet as ft
# from auth.authapp import AuthApp
# from main import main as youtube_app

# def main(page: ft.Page):
#     def auth_callback(auth_token):
#         if auth_token:
#             page.clean()  # 페이지 초기화
#             youtube_app(page)  # 유튜브 앱 실행
#         else:
#             page.add(ft.Text("인증 실패"))  # 인증 실패시 에러 메시지 출력
    
#     auth_app = AuthApp(auth_callback)
#     auth_app.build(page)

# def handler(event, context):
#      # Vercel 환경에서 실행되는 경우
#     page = ft.Page()
#     main(page) # page 를 직접 넘겨주고, ft.app()를 호출하지 않음.

#     return {
#         'statusCode': 200,
#         'body': "Flet app initialized"
#     }
# if __name__ == "__main__":
#     # 개발 환경에서 실행되는 경우
#      ft.app(target=main, view=ft.WEB_BROWSER)