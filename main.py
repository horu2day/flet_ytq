import sys
import flet as ft
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from PIL import Image
import io
import os
import json
import grpc
import datetime  # 추가: 파일명에 날짜 추가
import re  # 추가: 정규 표현식 모듈
import yt_dlp
from crawl4ai import AsyncWebCrawler
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import logging

# 키 생성 및 암호화 함수
GOOGLE_API_KEY = None


def generate_key(password: str):
    password = password.encode()
    salt = b"1234567890123456"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt_api_key(api_key, encryption_key):
    f = Fernet(encryption_key)
    encrypted_key = f.encrypt(api_key.encode())
    return encrypted_key.decode()


def decrypt_api_key(encrypted_key, encryption_key):
    f = Fernet(encryption_key)
    try:
        decrypted_key = f.decrypt(encrypted_key.encode())
        return decrypted_key.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

# 암호화된 API 키를 로드하는 함수


def load_api_key(encryption_key):
    # 실행 파일로 번들링된 경우 _MEIPASS 사용, 디버깅 환경에서는 현재 디렉토리 사용
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        config_file = os.path.join(sys._MEIPASS, "config.json")
        logging.info(f"_MEIPASS 사용: {config_file}")  # 로그 추가
    else:
        config_file = "config.json"
        logging.info(f"현재 디렉토리 사용: {config_file}")  # 로그 추가

    logging.info(f"config_file 경로 확인: {config_file}")  # 로그 추가 (파일 경로 확인)

    if os.path.exists(config_file):
        logging.info("config.json 파일 존재 확인")  # 로그 추가 (파일 존재 여부 확인)
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                logging.info(f"encrypted_api_key: {config.get('api_key')}")
                logging.info(f"인증 오류: {encryption_key}")
                encrypted_api_key = config.get("api_key")
                if encrypted_api_key:
                    return decrypt_api_key(encrypted_api_key, encryption_key)
                return None
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError 발생: {e}")  # JSONDecodeError 로그 추가
            return None
    else:
        logging.warning("config.json 파일 찾을 수 없음")  # 파일 없을 때 로그 추가
        return None
    return None


# API 키를 암호화하여 저장하는 함수
def save_api_key(api_key, encryption_key):
    config_file = "config.json"
    encrypted_api_key = encrypt_api_key(api_key, encryption_key)
    config = {"api_key": encrypted_api_key}
    with open(config_file, "w") as f:
        json.dump(config, f)


# 1. 초기 암호화 및 config.json 설정
def setup_config(api_key, password):
    encryption_key = generate_key(password)
    save_api_key(api_key, encryption_key)
    print("config.json 파일이 생성되고 API 키가 암호화되어 저장되었습니다.")


# 2. 프로그램 시작 시 API 키 로드 및 설정
def initialize_api(password):
    encryption_key = generate_key(password)
    GOOGLE_API_KEY = load_api_key(encryption_key)

    if GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            print("API 키가 성공적으로 로드되었습니다.")
        except Exception as e:
            print("API 키 설정 오류:", e)
    else:
        print("API 키를 로드하는데 실패했습니다. config.json 파일을 확인해 주세요.")


# 초기 설정 (최초 1회 실행)
# 주의: 이 부분은 최초 1회 실행 후 주석 처리해야 합니다.
# api_key = "AIzaSyBbPjsLpGnAN0vyIevZY4HcyNvaoR29l20"  # Gemini API 키
# password = input("config.json 생성을 위한 비밀번호를 입력하세요: ")
# setup_config(api_key, password)

# 프로그램 시작 시 API 키 로드 및 설정
password_for_load = "yt2b"
initialize_api(password_for_load)

# def load_api_key():
#     config_file = "config.json"
#     if os.path.exists(config_file):
#         try:
#             with open(config_file, "r") as f:
#                 config = json.load(f)
#                 return config.get("api_key")
#         except json.JSONDecodeError:
#             return None
#     return None
# # API 키를 저장하는 함수


# def save_api_key(api_key):
#     config_file = "config.json"
#     config = {"api_key": api_key}
#     with open(config_file, "w") as f:
#         json.dump(config, f)


# # API 키 초기화
# GOOGLE_API_KEY = load_api_key()
# if GOOGLE_API_KEY:
#     try:
#         genai.configure(api_key=GOOGLE_API_KEY)
#     except Exception as e:
#         print("API 키 설정 오류:", e)
# Gemini Pro Vision 모델 선택
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    # model_name="gemini-2.0-flash-thinking-exp-01-21",
    generation_config=generation_config,
)
# custom_instruction = ""
# 커스텀 instruction 설정
custom_instruction = """
Begin by enclosing all thoughts within <thinking> tags, exploring multiple angles and approaches.
Break down the solution into clear steps within <step> tags. Start with a 20-step budget, requesting more for complex problems if needed.
Use <count> tags after each step to show the remaining budget. Stop when reaching 0.
Continuously adjust your reasoning based on intermediate results and reflections, adapting your strategy as you progress.
Regularly evaluate progress using <reflection> tags. Be critical and honest about your reasoning process.
Assign a quality score between 0.0 and 1.0 using <reward> tags after each reflection. Use this to guide your approach:

0.8+: Continue current approach
0.5-0.7: Consider minor adjustments
Below 0.5: Seriously consider backtracking and trying a different approach

If unsure or if reward score is low, backtrack and try a different approach, explaining your decision within <thinking> tags.
For mathematical problems, show all work explicitly using LaTeX for formal notation and provide detailed proofs.
Explore multiple solutions individually if possible, comparing approaches in reflections.
Use thoughts as a scratchpad, writing out all calculations and reasoning explicitly.
Synthesize the final answer within <answer> tags, providing a clear, concise summary.
Conclude with a final reflection on the overall solution, discussing effectiveness, challenges, and solutions. Assign a final reward score.
"""

CATEGORY_MAP = """
1. 콘텐츠 유형 기반 분류:
교육 (Education): 강의, 강연, 튜토리얼, 설명 영상 등
엔터테인먼트 (Entertainment): 코미디, 드라마, 뮤직비디오, 영화 리뷰, 게임 영상 등
정보 (Information): 뉴스, 시사, 다큐멘터리, 인터뷰, 리뷰 등
브이로그 (Vlog): 일상 기록, 여행, 챌린지 등
리뷰 (Review): 상품 리뷰, 맛집 리뷰, 영화 리뷰 등
하우투 (How-to): 요리, DIY, 기술, 팁 등
음악 (Music): 뮤직비디오, 커버곡, 연주 영상 등
게임 (Gaming): 게임 플레이, 리뷰, 공략 영상 등
2.주제 또는 테마 기반 분류:
기술 (Technology): IT, 과학, 전자제품, 인공지능 등
뷰티 (Beauty): 메이크업, 스킨케어, 헤어 스타일링 등
패션 (Fashion): 스타일링, 옷 리뷰, 쇼핑 등
음식 (Food): 요리, 맛집, 베이킹, 먹방 등
여행 (Travel): 관광지 소개, 여행 팁, 브이로그 등
건강 및 피트니스 (Health & Fitness): 운동, 다이어트, 건강 정보 등
예술 및 문화 (Art & Culture): 미술, 음악, 영화, 공연, 문학 등
역사 (History): 역사 강의, 다큐멘터리 등
정치 및 사회 (Politics & Society): 뉴스, 시사, 사회 이슈 등
경제 및 금융 (Economics & Finance): 투자, 재테크, 경제 뉴스 등
3.타겟 시청자 기반 분류:
어린이 (Children): 교육용 애니메이션, 동요, 놀이 영상 등
청소년 (Teenagers): 뷰티, 패션, 게임, 학교생활 등
성인 (Adults): 경제, 투자, 건강, 취미 등
특정 관심사 그룹: 특정 스포츠, 게임, 예술 분야에 관심 있는 시청자 대상
감성 및 분위기 기반 분류:
재미 (Fun): 코미디, 유머, 챌린지 등
감동 (Emotional): 드라마, 휴먼 다큐멘터리, 감성 영상 등
힐링 (Relaxing): ASMR, 자연 영상, 명상 영상 등
흥미 (Interesting): 호기심 자극, 지식 영상 등
유익 (Informative): 교육, 튜토리얼, 뉴스 등
4.창작자 스타일 기반 분류:
채널별 분류: 특정 유튜브 채널의 영상 분류 (예: 특정 게임 채널, 특정 요리 채널)
개인 창작자 스타일 분류: 특정 창작자의 영상 스타일 (예: 유머러스한 스타일, 전문적인 스타일)
해시태그 기반 분류:
유튜브 영상에 사용된 해시태그를 기반으로 분류 (예: #ASMR, #DIY, #맛집)
5.혼합형 분류: 위에서 언급한 다양한 기준들을 조합하여 분류 체계를 구성하는 것이 좋습니다. 예를 들어 "교육"이라는 콘텐츠 유형 내에서 "기술"이라는 주제를 선택하고, "성인" 시청자를 대상으로 하는 영상들을 분류하는 방식입니다.
해시태그 활용: 해시태그를 활용하여 사용자 참여를 유도하고, 콘텐츠 분류를 자동화하는 데 활용할 수 있습니다.
사용자 피드백: 사용자 피드백을 수집하여 분류 체계를 개선하는 것이 좋습니다.
"""


def generate_question_and_answer(extracted_text, transcript, question=None):
    """
    추출된 문장에서 질문을 만들고, transcript에서 답을 찾아 Concise하게 답변합니다.
    markdown 형식 으로 답변을 반환합니다.
    Args:
      extracted_text: 추출된 문장
      transcript: 답변을 찾을 transcript 내용
      question: 수정된 질문 (선택적)

    Returns:
      생성된 질문, 답, 또는 None (질문 생성 실패 시)
    """
    try:
        if question:  # 수정된 질문이 있으면 그대로 사용
            question_text = question
        else:
            # 질문 생성 프롬프트
            question_prompt = f"""
            주어진 문장: "{extracted_text}"

            위 문장에서 사람들이 가장 궁금해할 만한 핵심 질문을 하나 만들어줘.
            질문은 한국어로 작성하고, 간결하게 만들어줘.
            """
            question_response = model.generate_content(
                question_prompt, stream=False)  # 추가

            question_text = question_response.text.strip()

        # 답변 찾기 프롬프트
        answer_prompt = f"""
        질문: "{question_text}"
        Transcript: "{transcript}"

        위 질문에 대한 답을 Transcript에서 찾아서 한국어로 알려줘.
        답변은 Concise하게 작성하고, 만약 답을 찾을 수 없다면 "답변을 찾을 수 없습니다." 라고 출력해줘.
        """
        answer_response = model.generate_content(
            answer_prompt, stream=False)  # 추가
        answer = answer_response.text.strip()

        # Markdown 형식으로 결과 반환
        markdown_result = f"## 질문\n{question_text}\n\n## 답변\n{answer}"
        return markdown_result, question_text, answer

        # return question_text, answer
    except grpc.RpcError as e:
        print(f"gRPC 오류 발생: {e}")
        return None, None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None


def extract_korean_text_from_image_url(image_url):
    """
    이미지 URL에서 한국어 문장을 추출합니다.

    Args:
        image_url: 이미지 URL

    Returns:
        추출된 한국어 문장 (문장이 없으면 빈 문자열)
    """
    try:
        # 이미지 다운로드
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # 오류 발생 시 예외 발생

        # 이미지 로드
        image = Image.open(io.BytesIO(response.content))

        # Gemini Pro Vision 모델에 이미지와 프롬프트 전달
        prompt_parts = [
            "이 이미지에서 한국어 문장을 추출해줘. 만약 한국어 문장이 없다면 아무것도 출력하지 마.",
            image
        ]
        response = model.generate_content(prompt_parts, stream=False)  # 추가

        # 결과 추출 및 반환
        text = response.text
        return text.strip()

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 오류: {e}")
        return ""
    except Exception as e:
        print(f"오류 발생: {e}")
        return ""

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 오류: {e}")
        return "", None
    except Exception as e:
        print(f"오류 발생: {e}")
        return "", None


def get_channel_and_title(video_url):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'simulate': True,
            'force_generic_extractor': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            if info_dict and 'channel' in info_dict and 'title' in info_dict:
                channel_name = info_dict['channel']
                title = info_dict['title']
                return channel_name, title
            else:
                return None, None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None


def sanitize_filename(filename):
    """파일 이름에 사용할 수 없는 문자 제거"""
    invalid_chars = r'[\/:*?"<>|]'
    return "".join(c if c not in invalid_chars else "_" for c in filename)


def extract_answer_from_xml(xml_string):

    match = re.search(r'<answer>(.*?)</answer>', xml_string, re.DOTALL)
    if match:
        return match.group(1).strip()

    return xml_string


def extract_properties_and_values(content, url):
    """
    Gemini API를 사용하여 글에서 적절한 Properties와 값을 추출합니다.
    Args:
        content (str): 파일 내용
        api_key (str): Gemini API 키
    Returns:
         str: 추출된 Properties와 값 (YAML 형식)
    """

    prompt = f"""
    Please analyze the following markdown content and extract the properties and values, this could include summary, key takeaways, description etc.
    Return the answer in below format
    설명: value1
    URL: value2
    {content}
    """
    response = model.generate_content(prompt, stream=False)
    properties_text = response.text.strip()
    return properties_text


def generate_frontmatter(content, url):
    """
    주어진 형식으로 프런트매터를 생성하고, 옵시디언에서 지원하는 모든 Properties를 추출하여 추가합니다.
    Args:
        content (str): 파일 내용
        api_key (str): Gemini API 키
    Returns:
        str: 생성된 프런트매터 문자열
    """

    properties_text = extract_properties_and_values(content, url)

    prompt = f"""
    주어진 텍스트를 분석하여 다음 정보를 추출하고 지정된 형식으로 출력합니다.

    1.  **키워드:** 텍스트에서 핵심 내용을 나타내는 단어들을 추출합니다. 키워드는 공백 없이 하나의 단어로 구성되어야 하며, 복수 키워드도 하나의 단어로 처리합니다. 핵심 내용이 복합 단어일 경우, 단어들을 붙여서 하나의 키워드로 만듭니다.
    2.  **대분류, 중분류, 소분류:** 제공된 분류 기준{CATEGORY_MAP}에 따라 텍스트에 가장 적합한 혼합형으로 분류를 지정합니다.
    3.  **근거:** 영상에서 주장하는 근거 문장 또는 링크을 추출합니다.
    4.  **한 줄 요약:** 텍스트의 핵심 내용을 한 문장으로 요약합니다.
    5. **출력 형식:** 아래 형식에 맞게 출력합니다.
    **출력 형식:**
    ---
    tags:
    -  [키워드1]
    -  [키워드2]
    -  [키워드3]
    -  [키워드4]
    분류체계1: [분류체계1중 하나의 값]
    분류체계2: [분류체계2중 하나의 값]
    분류체계3: [분류체계3중 하나의 값]
    근거: [주장에 대한 근거]
    Description: [한 줄 요약]
    ---
    **출력 예시:**
    ---
    tags:
    - 갈색지방
    - 냉기노출
    - 신진대사
    - 건강한지방
    콘텐츠 유형분류: 강연
    주제_테마분류: 건강
    감성분류: 힐링
    근거: 갈색 지방은 건강한 지방 저장소이며 미토콘드리아가 풍부하여 갈색을 띱니다. 추운 온도에서 몸을 따뜻하게 유지하고 신진대사를 위한 난로 역할을 합니다.
    Description: 갈색 지방은 건강한 지방으로 냉기 노출을 통해 활성화되며, 신진대사 증가, 혈중 지질 개선 등 건강에 긍정적인 효과를 가져온다.
    website:{url}
    ---
    {properties_text}
    {content}
    """
    response = model.generate_content(
        prompt, stream=False)
    frontmatter_text = response.text.strip()
    return frontmatter_text


def save_markdown_file(content, video_url, filename_prefix="output"):
    """마크다운 파일을 저장하고 파일 경로를 반환합니다."""
    channel_name, video_title = get_channel_and_title(video_url)

    if not channel_name or not video_title:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.md"
        #  프론트 매터 생성
        frontmatter = generate_frontmatter(content, video_url)
        print(filename)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(frontmatter)
            f.write("\n")
            f.write(content)

        return filename

    sanitized_channel_name = sanitize_filename(channel_name)
    sanitized_video_title = sanitize_filename(video_title)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"{sanitized_video_title}_{timestamp}.md"

    path = os.path.join(".", sanitized_channel_name)

    if not os.path.exists(path):  # 채널 이름 폴더가 없으면 생성
        os.makedirs(path, exist_ok=True)

    os.makedirs(path, exist_ok=True)

    full_path = os.path.join(path, filename)

    # 프론트 매터 생성

    frontmatter = generate_frontmatter(content, video_url)
    frontmatter = frontmatter.lstrip('\n')
    frontmatter = frontmatter.strip('```').lstrip('\n')
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write("\n")
        f.write(content)

    return full_path


def main(page: ft.Page):
    pw = "yt2b"
    page.title = "Youtube 내용이 궁금해!"
    page.window.width = 860
    page.window.height = 1080
    page.window.left = 10
    page.window.top = 10
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # api_key_field = ft.TextField(label="Google API Key", password=True,
    #                              width=300, value=pw if pw else "")
    # url_field = ft.TextField(label="YouTube URL", width=450)
    url_field = ft.TextField(label="YouTube URL", width=450)

    def question_field_on_submit(e):
        re_answer(e)
    question_field = ft.TextField(label="궁금해???", width=450)
    question_field.on_submit = question_field_on_submit
    answer_text = ft.Text(
        """""",
        selectable=True,
    )
    scrollable_answer = ft.Container(  # Container로 감싸기
        content=ft.Column(  # Column으로 감싸기
            [answer_text],
            scroll=ft.ScrollMode.ALWAYS,
            height=600
        ),

        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=5,
        padding=10,
        expand=True,  # 추가: Container가 사용 가능한 공간을 모두 차지하도록 설정
    )

    extracted_text_data = ""
    transcript_data = ""

    thumbnail_display = ft.Image(
        src="https://picsum.photos/200/200?5",
            width=320,
        height=180,
        fit=ft.ImageFit.SCALE_DOWN,
        repeat=ft.ImageRepeat.NO_REPEAT,
        border_radius=ft.border_radius.all(10),
    )  # 이미지 초기화

    api_key_field = ft.TextField(
        label="Google API Key", value=pw, password=True, width=300)

    def save_key(e):
        global GOOGLE_API_KEY
        key = api_key_field.value
        if key:
            save_api_key(key)
            GOOGLE_API_KEY = key
            try:
                genai.configure(api_key=GOOGLE_API_KEY)
            except Exception as e:
                print("API 키 설정 오류:", e)
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"API 키 설정 오류: {e}"), open=True)
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("API 키 저장 완료"), open=True)
                page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("API 키를 입력해주세요."), open=True)
            page.update()

    def close_dlg(e):
        settings_dlg.open = False
        page.update()

    settings_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("설정"),
        content=ft.Column([api_key_field,
                           ft.ElevatedButton("API 키 저장", on_click=save_key)],
                          tight=True),
        actions=[
            ft.TextButton("닫기", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_dlg_settings(e):
        page.dialog = settings_dlg
        settings_dlg.open = True  # 다이얼로그를 열어주는 코드 추가
        page.update()

    def extract_info(e):
        nonlocal extracted_text_data, transcript_data, thumbnail_display
        url = url_field.value

        video_id = url.split('v=')[1]
        if '&' in video_id:
            video_id = video_id.split('&')[0]

        # 썸네일 URL 생성
        thumbnail_url = f"https://img.youtube.com/vi/{
            video_id}/mqdefault.jpg"
        extracted_text = extract_korean_text_from_image_url(thumbnail_url)
        extracted_text_data = extracted_text
        if extracted_text:
            print(f"추출된 한국어 문장:\n{extracted_text}")
        else:
            print("이미지에서 한국어 문장을 찾을 수 없습니다.")

        thumbnail_display.src = thumbnail_url
        thumbnail_display.update()  # 이미지 업데이트
        try:

            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=['ko', 'en'])
            transcript_data = transcript
            answer_text.value = "스크립트 추출완료: "
            page.update()  # UI 업데이트

            markdown_result, question, answer = generate_question_and_answer(
                extracted_text, transcript)
            answer_text.value = "generate_question_and_answer함수완료 "
            page.update()  # UI 업데이트

            # 수정: markdown 결과 받기
            if markdown_result:
                filename = save_markdown_file(
                    markdown_result, url, "question_answer")  # 추가: 마크다운 파일 저장
                answer_text.value = "save_markdown_file함수완료 "
                page.update()  # UI 업데이트

                answer_text.value = markdown_result  # 수정: 마크다운 결과 출력
                page.overlay.append(
                    ft.SnackBar(
                        ft.Text(f"마크다운 파일 저장 완료: {filename}"), open=True))
            else:
                answer_text.value = "질문/답변 생성 실패"

            question_field.value = question
            answer_text.value = f"{answer}"
            page.update()  # UI 업데이트
        except Exception as e:
            question_field.value = f"오류: {e}"
            # answer_text.value = ""
            # page.update()

    def re_answer(e):
        nonlocal extracted_text_data, transcript_data
        question_value = question_field.value
        url = url_field.value
        if question_value:
            try:
                markdown_result, _, answer = generate_question_and_answer(
                    extracted_text_data, transcript_data, question=question_value)
                if markdown_result:
                    filename = save_markdown_file(
                        markdown_result, url, "re_question_answer")  # 추가: 마크다운 파일 저장
                    answer_text.value = answer  # 수정: 마크다운 결과 출력
                    page.overlay.append(ft.SnackBar(
                        ft.Text(f"마크다운 파일 저장 완료: {filename}"), open=True))
                else:
                    answer_text.value = "질문/답변 생성 실패"
                page.update()  # UI 업데이트
            except Exception as e:
                answer_text.value = f"오류 발생: {e}"
                page.update()

    def summarize_answer(e):
        nonlocal extracted_text_data, transcript_data
        url = url_field.value

        makemarkdownforurl(url)

    def makemarkdownforurl(url):
        video_id = url.split('v=')[1]
        if '&' in video_id:
            video_id = video_id.split('&')[0]

        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=['ko', 'en'])
            transcript_data = transcript
            # 요약 프롬프트
            original_text = f"""
            Transcript: "{transcript_data}"
            Transcript 내용을 바탕으로 markdown 형식으로 답변을 반환합니다.
            1. Carefully review the YouTube script from beginning to end.
            2. Based on the script, create a list of questions to fully understand the topic discussed in the video. Follow these guidelines when generating questions:
                - Start with general questions to understand the basic context (e.g., "What is the main topic of the video?").
                - Include specific questions to explore key details (e.g., "How does this topic impact [specific area]?" or "What are the main examples provided?").
                - Develop in-depth questions to gain deeper insights (e.g., "Why is this topic significant in today's context?" or "What challenges are associated with this issue?").
            3. Make sure the questions are clear, concise, and organized to encourage thorough answers.
            4. Translate all responses into Korean to provide a localized understanding of the content.
            5. 위에서 만든 질문은 생략하고, 정리된 답변만 markdown 형식으로 출력 해라.
            """

            summary_prompt = f"{custom_instruction}\n\n 원본프롬프트: {
                original_text}\n\n"

            summary_response = model.generate_content(
                summary_prompt, stream=False)

            summary_text = extract_answer_from_xml(
                summary_response.text.strip())

            # summary_text = summary_response.text.strip()

            filename = save_markdown_file(
                summary_text, url, "summary")  # 추가: 마크다운 파일 저장
            answer_text.value = summary_text  # 수정: 마크다운 결과 출력
            page.overlay.append(ft.SnackBar(
                # 추가: 스낵바 표시
                ft.Text(f"마크다운 파일 저장 완료: {filename}"), open=True))

            page.update()
        except Exception as e:
            question_field.value = f"오류 발생: {e}"
            answer_text.value = ""
            page.update()

    async def create_youtubook(e):
        channel_url = url_field.value
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=channel_url,
            )
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(result.markdown)
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            # 정규 표현식을 사용하여 '/watch?v=...' 패턴 찾기
            pattern = r"/watch\?v=[a-zA-Z0-9_-]+"
            matches = re.findall(pattern, result.markdown)

            # 찾은 패턴을 사용하여 전체 URL 생성
            base_url = "https://www.youtube.com"
            youtube_urls = [f"{base_url}{match}" for match in matches]

            # 중복 제거 및 순서 유지
            unique_urls = []
            seen = set()
            for url in youtube_urls:
                if url not in seen:
                    unique_urls.append(url)
                    seen.add(url)

            # 결과 출력
            print("YouTube URLs:")
            for url in unique_urls:
                makemarkdownforurl(url)

    top_widgets = ft.Column([  # Column 위젯으로 묶기
        # api_key_field,
        # ft.ElevatedButton("API 키 저장", on_click=save_key),
        url_field,
        ft.Row(
            [
                ft.ElevatedButton("추출하기", on_click=extract_info),
                ft.ElevatedButton("요약정리", on_click=summarize_answer),
                ft.ElevatedButton("Youtubook", on_click=create_youtubook),
            ],

            alignment=ft.MainAxisAlignment.CENTER,
        ),
        question_field,
        ft.Row(
            [
                ft.ElevatedButton("재답변", on_click=re_answer),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    ])

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.YOUTUBE_SEARCHED_FOR_ROUNDED),
        leading_width=40,
        title=ft.Text("Youtube 내용이 궁금해!"),
        center_title=False,
        bgcolor=ft.Colors.GREY_100,
        actions=[
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="설정", on_click=open_dlg_settings),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(
                        text="종료",
                        on_click=lambda _: page.window_close(),
                    ),
                ]
            ),
        ],
    )

    page.add(  # page.appbar 밖에 있어야 합니다.
        ft.Column([
            ft.Row([
                top_widgets,
                thumbnail_display]
            ),  # 썸네일 이미지 추가
            ft.Container(
                content=scrollable_answer,
                expand=True,
            ),
        ])
    )


if __name__ == "__main__":
    ft.app(target=main)
