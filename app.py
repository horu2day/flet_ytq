import flet as ft
from auth.authapp import AuthApp
from main import main as youtube_app
import logging
import urllib.parse
from utils import setup_logging

setup_logging()


def main(page: ft.Page):
    page.title = "유튜브 중독자"

    # OAuth 콜백 처리
    def handle_route(route):
        print(f"handle_route: {route}")  # 로그 추가
        params = urllib.parse.parse_qs(page.route)
        code = params.get("/code", [None])[0]  # 콜백에서 code 추출
        origin = params.get("origin", [None])[0]  # 원래 페이지 URL 추출

        print(f"Parsed parameters: {params}")  # 추가
        print(f"Extracted code: {code}, origin: {origin}")  # 추가

        if code:
            print(f"handle_route: code={code}, origin={origin}")  # 로그 추가
            # OAuth 콜백 처리 함수 호출
            auth_app.handle_oauth_callback(code, origin)
        else:
            print("Authentication failed (no code)")  # 추가
            page.add(ft.Text("handle_route 인증 실패"))
            page.update()
            #page.view = auth_app.build(page)  # 기본 인증 화면 표시
        page.update()

    def auth_callback(auth_token):
        try:
            if auth_token:
                page.clean()
                youtube_app(page)
            else:
                page.add(ft.Text("auth_callback 인증 실패"))
                page.update()
        except Exception as e:
            logging.error(f"Error in auth_callback: {str(e)}")
            page.add(ft.Text(f"오류가 발생했습니다: {str(e)}"))
            page.update()

    auth_app = AuthApp(auth_callback)
    auth_app.build(page)
    # 초기 라우트 설정 및 라우트 변경 핸들러 등록
    page.on_route_change = handle_route
    page.go(page.route)  # 초기 라우트 실행


if __name__ == "__main__":
    try:
        ft.app(target=main, view=ft.WEB_BROWSER, port=8000, host="0.0.0.0")  # 웹 모드로 실행, 0.0.0.0에서 수신 대기
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        raise