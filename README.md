# Project Title

<!--배지-->
![MIT License][license-shield] ![Repository Size][repository-size-shield] 

<!--프로젝트 대문 이미지-->
![Project Title](https://github.com/user-attachments/assets/996adb28-e99e-45d2-8a93-a360641baeda)


<!--목차-->
# Table of Contents
- [[1] About the Project](#1-about-the-project)
  - [Technologies](#technologies)
- [[2] Getting Started](#2-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [[3] Usage](#3-usage)
- [[4] Contact](#6-contact)



# [1] About the Project

- Django 와 React 에 대한 이해도 상승을 계기로 시작하게 되었습니다
- Instagram 의 클론 프로젝트


## Technologies

- [Python](https://www.python.org/downloads/) 3.11.9
- [MySQL](https://mariadb.org/) 8.0.33


# [2] Getting Started


## Prerequisites
*필요 라이브러리 설치*

```bash
pip install -r requirements.txt
```

## Installation

1. Repository 클론
```bash
git clone https://github.com/bearkuang/oristagram.git
```
2. pip packages 설치
```bash
pip install -r requirements.txt
```

## Configuration

- `settings.py`에 자신이 사용할 Database 정보를 입력
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': <your-database-name>',
        'USER': '<your-database-user-name>',
        'PASSWORD': '<your-database-password>',
        'HOST': 'localhost',
        'PORT': '3306',
    },
}
```

- `settings.py`에 자신이 사용할 프론트엔트의 CORS 허용 설정
```bash
CORS_ALLOWED_ORIGINS = [
    <your-frontend-port or domain>,
]
```


# [3] Usage

<h2>피드 생성</h2>

![col-join](https://github.com/user-attachments/assets/32a7efc4-bd6f-4f69-88db-652fe6771e69)

- 아이디와 이메일의 중복 확인
```python
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = create_user(serializer.validated_data)
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        
        errors = {}
        
        # 아이디와 이메일 중복 검사를 한 번에 수행
        if CustomUser.objects.filter(username=username).exists():
            errors['cust_username'] = "이미 가입된 아이디입니다."
        
        if CustomUser.objects.filter(email=email).exists():
            errors['cust_email'] = "이미 가입된 이메일입니다."
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # 이메일 인증 코드 확인
        verification_code = request.data.get('verification_code')
        if not verify_email_code(email, verification_code):
            return Response({"error": "Invalid or expired verification code"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

- 이메일 입력 및 인증번호 검증
- 인증번호 생성과 인증 이메일 내용
```python
def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email):
    code = generate_verification_code()
    subject = '이메일 인증 코드'
    message = f'귀하의 인증 코드는 {code} 입니다. 이 코드는 10분간 유효합니다.'
    from_email = 'ori178205@gmail.com'
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)
    
    # 캐시에 인증 코드 저장 (10분 동안 유효)
    cache_key = f'verification_code_{email}'
    cache.set(cache_key, code, 600)
    
    # 디버그 로그 추가
    print(f"Stored code in cache: {code}")
    print(f"Retrieved code from cache: {cache.get(cache_key)}")

    return code

def verify_email_code(email, code):
    cache_code = cache.get(f'verification_code_{email}')
    return cache_code == code
```
  
<br /><br />


<h2>피드 생성</h2>

![col-create-feed](https://github.com/user-attachments/assets/46fe5116-154f-4cd8-be70-e59aafdf7fb5)

- 업로드 하고자 하는 이미지를 선택, 원하는 비율 및 크기로 자르기, 필터 적용, 내용 및 태그－언급 기능과 쇼핑몰 연결하기

<br /><br />

```python
from PIL import Image as PILImage
from PIL import ImageOps, ImageFilter
from io import BytesIO
from django.core.files.base import ContentFile

def apply_filter(img, filter_name):
    if filter_name == 'grayscale':
        return ImageOps.grayscale(img)
    elif filter_name == 'invert':
        return ImageOps.invert(img)
    elif filter_name == 'sepia':
        return sepia(img)
    elif filter_name == 'blur':
        return img.filter(ImageFilter.BLUR)
    return img

def sepia(img):
    width, height = img.size
    pixels = img.load()
    for py in range(height):
        for px in range(width):
            r, g, b = img.getpixel((px, py))
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            pixels[px, py] = (min(tr,255), min(tg,255), min(tb,255))
    return img
```

- 라이브러리에 없는 필터의 경우 커스텀하여 추가해주었습니다.
  <br /><br />
  

<h2>릴스 생성</h2>

![col-create-reels](https://github.com/user-attachments/assets/21eafadd-f567-4135-8c39-4282c84c9bb6)

```python
import os
import magic
import tempfile
from django.core.exceptions import ValidationError
from moviepy.editor import VideoFileClip

def validate_file_type(value, valid_mime_types):
    # value가 _io.BytesIO 객체일 경우 파일의 MIME 타입을 추출
    file_mime_type = magic.from_buffer(value.read(), mime=True)
    value.seek(0)  # 파일 포인터를 처음으로 되돌립니다.

    if file_mime_type not in valid_mime_types:
        raise ValidationError(f'Unsupported file type: {file_mime_type}')

def validate_video_length(value, max_length):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        for chunk in value.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        video = VideoFileClip(tmp_path)
        duration = video.duration
        video.close()  # 비디오 파일을 닫기
        if duration > max_length:
            raise ValidationError(f'Video length exceeds {max_length} seconds.')
    except Exception as e:
        raise ValidationError('Unable to process video file.')
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except PermissionError:
                pass

def validate_feed_file_type(value):
    validate_file_type(value, ['image/jpeg', 'image/png', 'image/jpg', 'video/mp4', 'video/mpeg'])

def validate_feed_video_length(value):
    validate_video_length(value, 60)

def validate_reels_file_type(value):
    validate_file_type(value, ['video/mp4', 'video/mpeg'])

def validate_reels_video_length(value):
    validate_video_length(value, 90)
```
- 파일 확장자 검증 및 비디오 길이 감지

<br /><br />

<h2>Direct Message</h2>

![col-chat](https://github.com/user-attachments/assets/4c4b3d44-fa56-4c60-b450-729c49fd51fb)

- 다이렉트 메시지 기능

<br /><br />

# [4] Contact
- 📧 ori178205@gmail.com
- 📋 [https://github.com/bearkuang](https://github.com/bearkuang)

<br /><br />

<!--Url for Badges-->
[license-shield]: https://img.shields.io/github/license/dev-ujin/readme-template?labelColor=D8D8D8&color=04B4AE
[repository-size-shield]: https://img.shields.io/github/repo-size/dev-ujin/readme-template?labelColor=D8D8D8&color=BE81F7
[issue-closed-shield]: https://img.shields.io/github/issues-closed/dev-ujin/readme-template?labelColor=D8D8D8&color=FE9A2E

<!--URLS-->
[license-url]: LICENSE.md
[contribution-url]: CONTRIBUTION.md
[readme-eng-url]: ../README.md



