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