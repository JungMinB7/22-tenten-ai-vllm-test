#### 400 ERROR ####
# 잘못된 유튜브 URL 형식
class InvalidYouTubeUrlError(Exception):
    pass

# 유튜브 동영상에 자막이 없는 경우
class SubtitlesNotFoundError(Exception):
    pass

# 지원하지 않는 언어(한국어/영어가 아닌 자막)인 경우
class UnsupportedSubtitleLanguageError(Exception):
    pass

# 비공개 동영상인 경우
class VideoPrivateError(Exception):
    pass

# 존재하지 않는 동영상인 경우
class VideoNotFoundError(Exception):
    pass


class InvalidQueryParameterError(Exception):
    """
    요청 파라미터가 API 명세에 맞지 않을 때 발생합니다.
    - 예: 전달받은 게시글이 5개 미만인 경우
    """
    pass


#### 500 ERROR ####
class InternalServerError(Exception):
    """
    서버 내부에서 예기치 못한 오류가 발생했을 때 사용합니다.
    - 예: AI 모델 호출 실패, 로직 버그 등
    """
    pass