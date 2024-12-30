import flet as ft
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from PIL import Image
import io
import os
import json
import grpc

# 환경 변수나 설정 파일에서 API 키를 읽어오는 함수
def load_api_key():
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                return config.get("api_key")
        except json.JSONDecodeError:
            return None
    return None

# API 키를 저장하는 함수
def save_api_key(api_key):
    config_file = "config.json"
    config = {"api_key": api_key}
    with open(config_file, "w") as f:
        json.dump(config, f)

# API 키 초기화
GOOGLE_API_KEY = load_api_key()

if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
          print("API 키 설정 오류:", e)


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
    generation_config=generation_config,
)


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
        if question: # 수정된 질문이 있으면 그대로 사용
            question_text = question
        else:
            # 질문 생성 프롬프트
            question_prompt = f"""
            주어진 문장: "{extracted_text}"

            위 문장에서 사람들이 가장 궁금해할 만한 핵심 질문을 하나 만들어줘.
            질문은 한국어로 작성하고, 간결하게 만들어줘.
            """
            question_response = model.generate_content(question_prompt, stream=False) # 추가
            question_text = question_response.text.strip()


        # 답변 찾기 프롬프트
        answer_prompt = f"""
        질문: "{question_text}"
        Transcript: "{transcript}"

        위 질문에 대한 답을 Transcript에서 찾아서 한국어로 알려줘.
        답변은 Concise하게 작성하고, 만약 답을 찾을 수 없다면 "답변을 찾을 수 없습니다." 라고 출력해줘.
        """
        answer_response = model.generate_content(answer_prompt, stream=False) # 추가
        answer = answer_response.text.strip()

        return question_text, answer
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
        response = model.generate_content(prompt_parts, stream = False) # 추가

        # 결과 추출 및 반환
        text = response.text
        return text.strip()

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 오류: {e}")
        return ""
    except Exception as e:
        print(f"오류 발생: {e}")
        return ""

def main(page: ft.Page):
    page.title = "MyTube Second Brain"
    page.window.width = 600
    page.window.height = 800
    page.window.left = 10
    page.window.top = 10
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    api_key_field = ft.TextField(label="Google API Key", password=True, width=500, value = GOOGLE_API_KEY if GOOGLE_API_KEY else "")
    url_field = ft.TextField(label="YouTube URL", width=500)
    def question_field_on_submit(e):
        re_answer(e)
    question_field = ft.TextField(label="썸네일 질문", width=500)
    question_field.on_submit = question_field_on_submit
    answer_text = ft.Markdown(
            """""",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.COMMON_MARK,
            on_tap_link=lambda e: page.launch_url(e.data),
            width=600,
            height=600,
        )
    
    scrollable_answer = ft.Container(  # Container로 감싸기
        content=ft.Column( # Column으로 감싸기
            [answer_text],
            scroll=ft.ScrollMode.ALWAYS,
        ),
        
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=5,
        padding=10,
        expand=True,  # 추가: Container가 사용 가능한 공간을 모두 차지하도록 설정
    )
    
    extracted_text_data = ""
    transcript_data = ""

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
               page.snack_bar = ft.SnackBar(ft.Text(f"API 키 설정 오류: {e}"), open=True)
               page.update()
           else:
                page.snack_bar = ft.SnackBar(ft.Text("API 키 저장 완료"), open=True)
                page.update()
        else:
             page.snack_bar = ft.SnackBar(ft.Text("API 키를 입력해주세요."), open=True)
             page.update()



    

    def extract_info(e):
        nonlocal extracted_text_data, transcript_data
        url = url_field.value

        video_id = url.split('v=')[1]
        if '&' in video_id:
            video_id = video_id.split('&')[0]

        # 썸네일 URL 생성
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        extracted_text = extract_korean_text_from_image_url(thumbnail_url)
        extracted_text_data = extracted_text
        if extracted_text:
            print(f"추출된 한국어 문장:\n{extracted_text}")
        else:
            print("이미지에서 한국어 문장을 찾을 수 없습니다.")
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
            transcript_data = transcript
            question, answer = generate_question_and_answer(extracted_text, transcript)
            question_field.value = question
            answer_text.value = f"{answer}"
            page.update()  # UI 업데이트
        except Exception as e:
            question_field.value = f"오류 발생: {e}"
            answer_text.value = ""
            page.update()

    def re_answer(e):
          nonlocal extracted_text_data, transcript_data
          question_value = question_field.value
          if question_value:
             try:
                question, answer = generate_question_and_answer(extracted_text_data, transcript_data, question = question_value)
                answer_text.value = f"답변: {answer}"
                page.update()  # UI 업데이트
             except Exception as e:
                 answer_text.value = f"오류 발생: {e}"
                 page.update()

    def summarize_answer(e):
        nonlocal extracted_text_data, transcript_data
        url = url_field.value

        video_id = url.split('v=')[1]
        if '&' in video_id:
            video_id = video_id.split('&')[0]

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
            transcript_data = transcript
                          # 요약 프롬프트
            summary_prompt = f"""
            Transcript: "{transcript_data}"

            Transcript 내용을 바탕으로 markdown 형식 으로 답변을 반환합니다.
            * 다음 유튜브 영상의 주요 내용을 설명해주세요. 요약하지 말고 자세히 알려주세요.
            * 이 유튜브 영상에서 다루는 핵심 주제와 정보는 무엇인가요? 간단히 요약하지 말고 상세히 설명해주세요.
            * 이 유튜브 영상의 내용을 전체적으로 파악하고 싶습니다. 주요 포인트들을 빠짐없이 설명해주세요. 요약은 피해주시고 자세한 내용을 알려주세요.
            * 이 유튜브 영상에서 전달하고자 하는 주요 메시지나 정보는 무엇인가요? 내용을 축소하지 말고 상세히 설명해주세요.
            * 이 유튜브 영상의 내용을 처음부터 끝까지 자세히 설명해주세요. 중요한 정보나 세부사항을 생략하지 말고 모두 포함해주세요.
            """
            summary_response = model.generate_content(summary_prompt, stream=False)
            summary = summary_response.text.strip()
            answer_text.value = f"{summary}"
            page.update()  # UI 업데이트

        except Exception as e:
            question_field.value = f"오류 발생: {e}"
            answer_text.value = ""
            page.update()

    page.add(
        api_key_field,
        ft.ElevatedButton("API 키 저장", on_click=save_key),
        url_field,
        ft.Row(  # Row 위젯으로 버튼들 묶기
            [
             ft.ElevatedButton("정답", on_click=extract_info),
             ft.ElevatedButton("영상정리", on_click=summarize_answer),
            ],
            alignment=ft.MainAxisAlignment.CENTER, # 버튼 중앙 정렬 추가
        ),
        question_field,
        ft.Row(  # Row 위젯으로 버튼들 묶기
            [
             ft.ElevatedButton("다시답변해라", on_click=re_answer),
            ],
            alignment=ft.MainAxisAlignment.CENTER, # 버튼 중앙 정렬 추가
        ),# 요약정리 버튼 추가
        ft.Container(
           content=scrollable_answer,
           expand=True,
        )
    )