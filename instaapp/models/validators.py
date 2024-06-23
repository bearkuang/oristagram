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
