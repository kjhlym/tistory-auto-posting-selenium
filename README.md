# 티스토리 자동 포스팅 Selenium 스크립트

이 스크립트는 Selenium을 사용하여 티스토리에 자동으로 로그인하고 포스팅을 하는 기능을 제공합니다.

## 기능

- 크롬 브라우저 자동 실행
- 카카오 계정을 통한 티스토리 로그인
- 블로그 글 자동 작성 및 임시저장

## 설치 방법

1. 필요한 패키지 설치
```bash
pip install selenium webdriver-manager python-dotenv pyperclip
```

2. .env 파일 설정
```
KAKAO_ID=your_kakao_id
KAKAO_PW=your_kakao_password
```

3. 설정 변경
auto.py 파일에서 다음 변수를 자신의 블로그에 맞게 수정하세요:
```python
tistory_blog_name = 'https://yourblog.tistory.com'
tistory_category_name = '카테고리명'
```

## 사용 방법

```bash
python auto.py
```

## 주의사항

- 티스토리의 UI가 변경되면 일부 기능이 작동하지 않을 수 있습니다.
- 브라우저 창을 임의로 닫지 마세요.
- 비밀번호와 같은 민감한 정보는 .env 파일에 보관하고 GitHub에 업로드하지 마세요.