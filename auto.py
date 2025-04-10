from time import sleep
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import platform
import subprocess
import pyperclip
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import os

C_END = "\033[0m"
C_BOLD = "\033[1m"
C_INVERSE = "\033[7m"
C_BLACK = "\033[30m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_PURPLE = "\033[35m"
C_CYAN = "\033[36m"
C_WHITE = "\033[37m"
C_BGBLACK = "\033[40m"
C_BGRED = "\033[41m"
C_BGGREEN = "\033[42m"
C_BGYELLOW = "\033[43m"
C_BGBLUE = "\033[44m"
C_BGPURPLE = "\033[45m"
C_BGCYAN = "\033[46m"
C_BGWHITE = "\033[47m"

osName = platform.system()  # window 인지 mac 인지 알아내기 위한

LOADING_WAIT_TIME = 10
PAUSE_TIME = 5
# .env 파일에서 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

# 카카오 로그인 정보
KAKAO_ID = os.getenv('KAKAO_ID')
KAKAO_PW = os.getenv('KAKAO_PW')

if not KAKAO_ID or not KAKAO_PW:
    raise Exception("환경 변수 KAKAO_ID 또는 KAKAO_PW가 설정되지 않았습니다.")


tistory_blog_name = 'https://cathodicpro.tistory.com'

tistory_category_name = '분양정보'

def init_driver():
    if osName not in "Windows":
        try:
            subprocess.Popen([
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --remote-debugging-port=9224 --user-data-dir="~/Desktop/crawling/chromeTemp24"'],
                shell=True, stdout=subprocess.PIPE)  # 디버거 모드(로그인 정보 기타 정보 저장)
        except FileNotFoundError:
            subprocess.Popen([
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --remote-debugging-port=9224 --user-data-dir="~/Desktop/crawling/chromeTemp24"'],
                shell=True, stdout=subprocess.PIPE)
    else:
        try:
            chrome_proc = subprocess.Popen(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9224 '
                             r'--user-data-dir="C:\chromeTemp24"')  # 디버거 크롬 구동
        except FileNotFoundError:
            chrome_proc = subprocess.Popen(
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9224 '
                r'--user-data-dir="C:\chromeTemp24"')
    
    # 크롬이 완전히 시작될 때까지 기다림
    print('Chrome 브라우저를 시작하는 중입니다. 잠시 기다려주세요...')
    sleep(10)
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9224")
    
    # service = ChromeService('C:\\Users\\ree31\\.wdm\\drivers\\chromedriver\\win64\\120.0.6099.71\\chromedriver.exe')
    service = ChromeService(executable_path=ChromeDriverManager().install())
    
    try:
        _driver = webdriver.Chrome(service=service, options=options)
        _driver.implicitly_wait(LOADING_WAIT_TIME)
        return _driver
    except Exception as e:
        print(f"Chrome 드라이버 초기화 중 오류 발생: {e}")
        print("프로그램을 종료합니다.")
        exit(1)


def tistory_login(_driver):
    try:
        print('\n티스토리 로그인 시도 중...')
        _driver.get('https://www.tistory.com/auth/login')
        sleep(LOADING_WAIT_TIME)
        
        # 현재 URL이 로그인 완료된 상태인지 확인
        current_url = _driver.current_url
        page_title = _driver.title
        print(f"현재 URL: {current_url}")
        print(f"페이지 타이틀: {page_title}")
        
        # 디버깅 - 페이지 상태 확인
        print("\n--- 로그인 페이지 디버깅 정보 ---")
        try:
            links = _driver.find_elements(By.TAG_NAME, "a")
            print(f"페이지 내 링크 수: {len(links)}")
            for i, link in enumerate(links[:10]):  # 처음 10개만 출력
                link_href = link.get_attribute("href") or "없음"
                link_class = link.get_attribute("class") or "없음"
                link_text = link.text or "없음"
                print(f"링크 {i+1}: HREF={link_href}, CLASS={link_class}, TEXT={link_text}")
                
            # 로그인 관련 모든 요소 찾기
            login_elements = _driver.find_elements(By.XPATH, "//*[contains(@class, 'login') or contains(@id, 'login') or contains(text(), '로그인') or contains(text(), 'Login')]")
            print(f"\n로그인 관련 요소 수: {len(login_elements)}")
            for i, el in enumerate(login_elements[:10]):
                el_tag = el.tag_name
                el_id = el.get_attribute("id") or "없음"
                el_class = el.get_attribute("class") or "없음"
                el_text = el.text or "없음"
                print(f"로그인 요소 {i+1}: TAG={el_tag}, ID={el_id}, CLASS={el_class}, TEXT={el_text}")
        except Exception as e:
            print(f"디버깅 정보 수집 실패: {e}")
        
        print("--- 디버깅 정보 끝 ---\n")
        
        # 이미 로그인된 상태라면 다시 로그인 안함
        if '/auth/login' not in current_url:
            print('이미 로그인 되어있습니다.')
            return True
            
        # 직접 카카오 로그인 페이지로 이동 (티스토리 로그인 페이지 우회)
        print("직접 카카오 로그인 페이지로 이동합니다...")
        _driver.get('https://accounts.kakao.com/login/?continue=https%3A%2F%2Faccounts.kakao.com%2Fweblogin%2Faccount%2Finfo')
        sleep(LOADING_WAIT_TIME)
        
        # 카카오 로그인 시도
        try:
            print("카카오 아이디/비밀번호 입력 시도...")
            
            # 아이디 입력
            try:
                kakao_id_input = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='email' or @id='id_email_2' or @id='loginId' or @id='id']"))
                )
                kakao_id_input.clear()
                kakao_id_input.send_keys(os.getenv('KAKAO_ID'))
                print("카카오 아이디 입력 완료")
            except Exception as e:
                print(f"카카오 아이디 입력 실패: {e}")
                # JavaScript로 시도
                try:
                    _driver.execute_script(f"document.querySelector('input[name=\"email\"], input#id_email_2, input#loginId, input#id').value = '{os.getenv('KAKAO_ID')}';")
                    print("JavaScript를 사용하여 아이디 입력 완료")
                except Exception as js_e:
                    print(f"JavaScript 아이디 입력 실패: {js_e}")
                    raise Exception("카카오 아이디 입력 실패")
            
            # 비밀번호 입력
            try:
                kakao_pw_input = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='password' or @id='id_password_3' or @id='password' or @id='pw']"))
                )
                kakao_pw_input.clear()
                kakao_pw_input.send_keys(os.getenv('KAKAO_PW'))
                print("카카오 비밀번호 입력 완료")
            except Exception as e:
                print(f"카카오 비밀번호 입력 실패: {e}")
                # JavaScript로 시도
                try:
                    _driver.execute_script(f"document.querySelector('input[name=\"password\"], input#id_password_3, input#password, input#pw').value = '{os.getenv('KAKAO_PW')}';")
                    print("JavaScript를 사용하여 비밀번호 입력 완료")
                except Exception as js_e:
                    print(f"JavaScript 비밀번호 입력 실패: {js_e}")
                    raise Exception("카카오 비밀번호 입력 실패")
            
            # 로그인 버튼 클릭
            try:
                login_btn = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(@class, 'submit') or contains(@class, 'login') or contains(text(), '로그인')]"))
                )
                login_btn.click()
                print("로그인 버튼 클릭 완료")
            except Exception as e:
                print(f"로그인 버튼 클릭 실패: {e}")
                # JavaScript로 시도
                try:
                    _driver.execute_script("document.querySelector('button[type=\"submit\"], button.submit, button.login, button:contains(\"로그인\")').click();")
                    print("JavaScript를 사용하여 로그인 버튼 클릭 완료")
                except Exception as js_e:
                    print(f"JavaScript 로그인 버튼 클릭 실패: {js_e}")
                    
                    # form submit 시도
                    try:
                        _driver.execute_script("document.querySelector('form').submit();")
                        print("JavaScript form submit 완료")
                    except Exception as form_e:
                        print(f"JavaScript form submit 실패: {form_e}")
                        raise Exception("카카오 로그인 버튼 클릭 실패")
            
            # 로그인 완료 대기
            print("로그인 완료 대기 중...")
            sleep(10)  # 로그인 처리 대기
            
            # 티스토리 페이지로 이동
            print("티스토리 페이지로 이동...")
            _driver.get('https://www.tistory.com')
            sleep(LOADING_WAIT_TIME)
            
            # 로그인 성공 확인
            current_url = _driver.current_url
            if '/auth/login' not in current_url:
                print("로그인 성공 확인!")
                return True
            else:
                print("로그인 실패: 여전히 로그인 페이지에 있습니다.")
                raise Exception("카카오 로그인 실패")
                
        except Exception as e:
            print(f"카카오 로그인 중 오류 발생: {e}")
            raise Exception(f"로그인 실패: {e}")
                
    except Exception as e:
        print(f'로그인 중 오류 발생: {e}')
        raise


def tistory_write(_driver, keyword):
    title = '임시로 정한 title 입니다. 나중에 변경해주세요!!'
    body_html = f'{keyword}'
    
    # 게시글 작성 페이지로 이동
    manage_url = f'{tistory_blog_name}/manage/post'
    print(f'페이지 이동: {manage_url}')
    _driver.get(manage_url)
    sleep(LOADING_WAIT_TIME)
    
    # 현재 URL과 타이틀 확인
    current_url = _driver.current_url
    page_title = _driver.title
    print(f'현재 URL: {current_url}')
    print(f'페이지 타이틀: {page_title}')
    
    # 관리자 페이지인지 확인 - 관리자 페이지 URL이 변경되었을 수 있으므로 체크 조건 완화
    if not ('tistory.com' in current_url and ('manage' in current_url or 'newpost' in current_url)):
        print("오류: 티스토리 관리자 페이지가 아닙니다.")
        print("로그인 상태를 확인하고 다시 시도해주세요.")
        raise Exception("티스토리 관리자 페이지로 이동할 수 없습니다.")
    
    # 이미작성하고 있는 글이 있었을때 나오는 alert 팝업 처리
    try:
        obj = _driver.switch_to.alert
        msg = obj.text
        print(f'\nalert message = {msg}')
        print('alert dismiss')
        obj.dismiss()
        sleep(PAUSE_TIME)
    except:
        print('no alert')
    
    # 페이지가 완전히 로드될 때까지 대기
    try:
        print("Tistory 글쓰기 페이지 로딩 중...")
        WebDriverWait(_driver, LOADING_WAIT_TIME).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 디버깅: 페이지의 모든 버튼과 ID 속성 출력
        print("\n--- 페이지 디버깅 정보 ---")
        buttons = _driver.find_elements(By.TAG_NAME, "button")
        print(f"페이지 내 버튼 수: {len(buttons)}")
        for i, btn in enumerate(buttons[:10]):  # 처음 10개만 출력
            btn_id = btn.get_attribute("id") or "없음"
            btn_class = btn.get_attribute("class") or "없음"
            btn_text = btn.text or "없음"
            print(f"버튼 {i+1}: ID={btn_id}, CLASS={btn_class}, TEXT={btn_text}")
        
        # HTML 모드 전환 관련 모든 요소 찾기
        html_elements = _driver.find_elements(By.XPATH, "//*[contains(@id, 'html') or contains(@class, 'html') or contains(text(), 'HTML')]")
        print(f"\nHTML 관련 요소 수: {len(html_elements)}")
        for i, el in enumerate(html_elements[:10]):
            el_tag = el.tag_name
            el_id = el.get_attribute("id") or "없음"
            el_class = el.get_attribute("class") or "없음"
            el_text = el.text or "없음"
            print(f"HTML 요소 {i+1}: TAG={el_tag}, ID={el_id}, CLASS={el_class}, TEXT={el_text}")
        
        print("--- 디버깅 정보 끝 ---\n")
        
    except Exception as e:
        print(f"페이지 로드 대기 중 오류: {e}")
        print("현재 페이지 URL:", _driver.current_url)
        print("페이지 소스:", _driver.page_source[:500] + "..." if len(_driver.page_source) > 500 else _driver.page_source)
        raise Exception("Tistory 글쓰기 페이지를 로드할 수 없습니다.")
    
    try:
        # 에디터 UI 요소 찾기 시도
        try:
            print("에디터 모드 버튼 찾는 중...")
            # 새로운 티스토리 인터페이스에서는 다른 선택자가 필요할 수 있음
            editor_mode_elements = _driver.find_elements(By.XPATH, "//*[contains(@class, 'mode') or contains(@id, 'mode')]")
            if editor_mode_elements:
                print(f"모드 관련 요소 {len(editor_mode_elements)}개 발견")
                for i, el in enumerate(editor_mode_elements[:5]):
                    print(f"모드 요소 {i+1}: ID={el.get_attribute('id') or '없음'}, CLASS={el.get_attribute('class') or '없음'}, TEXT={el.text or '없음'}")
            
            # 먼저 기존 방식 시도
            try:
                editor_mode_btn = WebDriverWait(_driver, 5).until(
                    EC.presence_of_element_located((By.ID, "editor-mode-layer-btn-open"))
                )
                print("기존 에디터 모드 버튼을 찾았습니다.")
            except:
                print("기존 에디터 모드 버튼을 찾을 수 없습니다. 새로운 방식 시도...")
                # 티스토리 새 인터페이스에서 HTML 모드 전환 버튼 찾기 (클래스명이나 다른 속성으로 시도)
                editor_mode_btn = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'html') or contains(text(), 'HTML') or contains(@id, 'html')]"))
                )
                print(f"새 인터페이스의 HTML 버튼을 찾았습니다: ID={editor_mode_btn.get_attribute('id')}, CLASS={editor_mode_btn.get_attribute('class')}, TEXT={editor_mode_btn.text}")
                
        except Exception as e:
            print(f"에디터 모드 버튼을 찾을 수 없습니다: {e}")
            print("티스토리 UI가 변경되었거나 로그인이 필요할 수 있습니다.")
            
            # 로그인 버튼이 있는지 확인
            try:
                login_btn = _driver.find_element(By.CSS_SELECTOR, ".btn_login, .link_login, .btn-login")
                print("로그인 버튼이 발견됨. 로그인이 필요합니다.")
                raise Exception("티스토리에 로그인이 필요합니다.")
            except:
                pass
            
            # 대체 방법: 직접 제목과 내용 입력 시도
            print("에디터 모드 전환을 건너뛰고 직접 글쓰기를 시도합니다.")
            try:
                # 제목 입력 필드 찾기
                title_fields = _driver.find_elements(By.XPATH, "//input[contains(@id, 'title') or contains(@name, 'title') or contains(@class, 'title')]")
                if title_fields:
                    print(f"제목 필드 {len(title_fields)}개 발견")
                    title_input = title_fields[0]
                    title_input.clear()
                    title_input.send_keys(title)
                    print("제목 입력 성공")
                    
                    # 내용 입력 필드 찾기 (다양한 선택자 시도)
                    content_fields = _driver.find_elements(By.XPATH, "//textarea[contains(@id, 'content') or contains(@class, 'content')] | //div[contains(@class, 'editor') or contains(@class, 'content')]")
                    if content_fields:
                        print(f"내용 필드 {len(content_fields)}개 발견")
                        content_input = content_fields[0]
                        content_input.clear()
                        content_input.send_keys(body_html)
                        print("내용 입력 성공")
                        
                        # 저장 버튼 찾기
                        save_btns = _driver.find_elements(By.XPATH, "//button[contains(@class, 'save') or contains(@class, 'draft') or contains(text(), '저장') or contains(text(), '임시')]")
                        if save_btns:
                            print(f"저장 버튼 {len(save_btns)}개 발견")
                            save_btns[0].click()
                            print("임시 저장 성공")
                            sleep(PAUSE_TIME)
                            return  # 성공적으로 처리됨
                
                # 여기까지 오면 실패한 것
                print("대체 방법도 실패했습니다.")
                raise Exception("티스토리 에디터를 찾을 수 없어 글을 작성할 수 없습니다.")
            except Exception as e:
                print(f"대체 방법 실패: {e}")
                raise Exception("티스토리 에디터를 찾을 수 없습니다.")
        
        # 여기서부터는 기존 HTML 모드 변환 방식 시도
        try:
            print("HTML 모드로 전환 시도...")
            editor_mode_btn.click()
            sleep(PAUSE_TIME)
            
            try:
                html_mode_btn = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                    EC.presence_of_element_located((By.ID, "editor-mode-html"))
                )
                html_mode_btn.click()
                sleep(PAUSE_TIME)
                
                # 알림창 처리 시도
                try:
                    _driver.switch_to.alert.accept()  # html 모드 변환시 alert 처리
                    sleep(PAUSE_TIME)
                    print("HTML 모드 전환 성공")
                except:
                    print("알림창이 없거나 처리에 실패했지만 계속 진행합니다.")
            except:
                print("HTML 모드 버튼을 찾을 수 없거나 클릭할 수 없습니다.")
                # 에러를 발생시키지 않고 계속 진행
        except:
            print("HTML 모드 전환에 실패했지만 계속 진행합니다.")
        
        # 카테고리 선택
        try:
            print("카테고리 선택 시도...")
            category_btn = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                EC.presence_of_element_located((By.ID, "category-btn"))
            )
            category_btn.click()
            sleep(PAUSE_TIME)
            
            category_item = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, f"//span[normalize-space()='{tistory_category_name}']"))
            )
            category_item.click()
            sleep(PAUSE_TIME)
            print("카테고리 선택 성공")
        except Exception as e:
            print(f"카테고리 선택 실패: {e}")
            print("카테고리 선택을 건너뛰고 계속 진행합니다.")
        
        # 제목 입력 시도
        try:
            print("제목 입력 시도...")
            title_fields = _driver.find_elements(By.XPATH, "//input[contains(@id, 'title') or contains(@name, 'title') or contains(@class, 'title')]")
            if title_fields:
                title_input = title_fields[0]
                title_input.clear()
                title_input.send_keys(title)
                print("제목 입력 성공")
            else:
                # 기존 방식 시도
                title_input = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                    EC.presence_of_element_located((By.ID, "post-title-inp"))
                )
                title_input.click()
                pyperclip.copy(title)
                ActionChains(_driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                print("기존 방식으로 제목 입력 성공")
        except Exception as e:
            print(f"제목 입력 실패: {e}")
            print("제목 입력을 건너뛰고 계속 진행합니다.")
        
        # 글쓰기 시도
        try:
            print("본문 입력 시도...")
            # 새로운 에디터 인터페이스에서 content 편집 영역 찾기 시도
            content_areas = _driver.find_elements(By.XPATH, "//div[contains(@class, 'CodeMirror') or contains(@class, 'editor') or contains(@class, 'content')]")
            if content_areas:
                content_area = content_areas[0]
                content_area.click()
                pyperclip.copy(body_html)
                ActionChains(_driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                print("새 인터페이스로 본문 입력 성공")
            else:
                # 기존 방식 시도
                codemirror = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "CodeMirror-lines"))
                )
                codemirror.click()
                pyperclip.copy(body_html)
                ActionChains(_driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                print("기존 방식으로 본문 입력 성공")
        except Exception as e:
            print(f"본문 입력 실패: {e}")
            print("본문 입력을 건너뛰고 계속 진행합니다.")
        
        # 임시저장 시도
        try:
            print("임시저장 시도...")
            # 다양한 방법으로 저장 버튼 찾기
            save_btns = _driver.find_elements(By.XPATH, "//button[contains(@class, 'save') or contains(@class, 'draft') or contains(text(), '저장') or contains(text(), '임시')]")
            if save_btns:
                save_btns[0].click()
                print("새 인터페이스로 임시저장 성공")
            else:
                # 기존 방식 시도
                draft_btn = WebDriverWait(_driver, LOADING_WAIT_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "btn-draft"))
                )
                draft_btn.click()
                print("기존 방식으로 임시저장 성공")
            
            print('\n티스토리 글이 임시 저장되었습니다. 최종 발행은 따로 진행 부탁드려요')
            sleep(PAUSE_TIME)
        except Exception as e:
            print(f"임시저장 실패: {e}")
            raise Exception("임시저장 버튼을 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"글 작성 중 오류 발생: {e}")
        print("현재 URL:", _driver.current_url)
        raise


def main():
    driver = None
    try:
        print("\nSTART...")
        
        keyword = '김범수 꿈일까'
        
        # chrome driver init
        driver = init_driver()
        
        # tistory login
        tistory_login(driver)
        
        # tistory write
        tistory_write(driver, keyword)
        
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        print("\nEND!!!")


if __name__ == '__main__':
    main()