#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from bs4 import BeautifulSoup
import time
import os

# ✅ 게시판 목록에서 nttNo 수집
def get_nttNo_list_fixed(max_count=4000):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)
    nttNo_list = []
    page = 1
    print("📄 목록 페이지에서 nttNo 수집 시작...")

    while len(nttNo_list) < max_count:
        url = f"https://www.chungju.go.kr/www/selectBbsNttList.do?key=494&bbsNo=6&pageIndex={page}"
        driver.get(url)

        print(f"📄 현재 {page}페이지 처리 중")
        print(f"🔢 현재까지 수집된 nttNo 개수: {len(nttNo_list)}")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list li"))
            )
        except TimeoutException:
            print(f"⚠️ 목록 {page}페이지 로딩 실패")
            break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = soup.select("ul.list li a")

        for link in links:
            href = link.get("href")
            if "nttNo=" in href:
                ntt = href.split("nttNo=")[-1].split("&")[0]
                if ntt not in nttNo_list:
                    nttNo_list.append(ntt)
                    if len(nttNo_list) >= max_count:
                        break

        page += 1
        time.sleep(0.8)

    driver.quit()
    print(f"✅ 수집된 게시글 수: {len(nttNo_list)}개")
    return nttNo_list


# ✅ 각 nttNo별 본문 크롤링
def crawl_articles_from_nttNos(nttNo_list, output_path="data/corpus.txt"):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)

    results = []
    print("🚀 게시글 본문 크롤링 시작")

    for idx, nttNo in enumerate(nttNo_list):
        url = f"https://www.chungju.go.kr/www/selectBbsNttView.do?key=494&bbsNo=6&nttNo={nttNo}"
        driver.get(url)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr.code_SJ td"))
            )
        except (TimeoutException, UnexpectedAlertPresentException):
            try:
                alert = driver.switch_to.alert
                alert.dismiss()
            except:
                pass
            continue

        soup = BeautifulSoup(driver.page_source, "html.parser")
        title_tag = soup.select_one("tr.code_SJ td")
        date_tag = soup.select_one("tr.code_RGSDE td")
        content_tag = soup.select_one("tr.code_CN td.bbs_content")

        if title_tag and content_tag:
            title = title_tag.text.strip()
            date = date_tag.text.strip() if date_tag else "날짜 없음"
            content = content_tag.get_text("\n", strip=True).replace('\xa0', ' ')
            article = f"[제목] {title}\n[날짜] {date}\n[내용]\n{content}\n---\n"
            results.append(article)

        # ✅ 100건마다 중간 저장
        if (idx + 1) % 100 == 0:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(results)
            print(f"💾 {idx+1}건까지 저장 완료")

        time.sleep(0.8)

    driver.quit()
    print(f"\n✅ 총 {len(results)}건 수집 완료")

    # ✅ 최종 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(results)

    print(f"💾 최종 저장 완료 → {output_path}")


# ✅ 실행
if __name__ == "__main__":
    ntt_list = get_nttNo_list_fixed(max_count=4000)
    crawl_articles_from_nttNos(ntt_list, output_path="data/corpus.txt")

