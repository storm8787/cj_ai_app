#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# report_prompt_template.py

def get_report_prompt(report_type: str, format_type: str, title: str, keywords: list[str]) -> str:
    keyword_text = "\n".join(f"- {kw}" for kw in keywords)

    # ✅ 공통 지시문 (모든 보고서에 무조건 포함됨)
    common_guideline = f"""📄 제목: {title}

다음은 충주시 내부 보고서 초안임.  
문서는 반드시 다음 기준을 충실히 따를 것:

- 전체는 **항목 중심 구조**로 작성할 것 (1. ~ 2. ~)
- 문장은 **행정문서체**로 작성할 것 (예: '~되었음', '~임', '~필요함')
- 모든 문장은 **개괄식 종결형**으로 작성할 것 (예: '~이 필요', '~으로 판단됨')

"""

    # 계획보고
    if report_type == "계획보고":
        if format_type == "사업계획서형":
            return common_guideline + f"""
1. 추진배경  
2. 사업개요  
 - 사 업 명 :  
 - 사업기간 :  
 - 예 산 액 :  
3. 추진내용  
4. 기대효과  
5. 실무적 필요 및 검토사항

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "예산중심형":
            return common_guideline + f"""
1. 예산 편성 배경  
2. 사업개요  
 - 사 업 명 :  
 - 총 예산액 :  
 - 연차별 예산 계획 :  
3. 예산 활용 계획  
4. 예산 쟁점 및 검토사항  
5. 향후 예산 일정

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "시행일정형":
            return common_guideline + f"""
1. 사업개요  
2. 단계별 추진 일정  
3. 일정별 주요 내용  
4. 일정상 리스크 및 대응  
5. 향후 일정 공유 및 유의사항

📌 주요 키워드:
{keyword_text}
"""

    # 동향보고
    elif report_type == "동향보고":
        if format_type == "주간트렌드형":
            return common_guideline + f"""
1. 요약 개요  
2. 주요 동향 및 수치  
3. 배경 및 원인 분석  
4. 대응 방향 및 협조사항  
5. 향후 모니터링 사항

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "상황분석형":
            return common_guideline + f"""
1. 발생 개요 및 현황  
2. 주요 원인 분석  
3. 수치 기반 경향  
4. 현재 대응 및 검토사항  
5. 향후 대응 계획

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "이슈집중형":
            return common_guideline + f"""
1. 이슈 개요 (일시, 내용)  
2. 주요 경과 및 확산 경로  
3. 부서 대응 내용  
4. 외부 반응 또는 확산 현황  
5. 향후 대응 및 메시지 방향

📌 주요 키워드:
{keyword_text}
"""

    # 성과보고
    elif report_type == "성과보고":
        if format_type == "정량지표형":
            return common_guideline + f"""
1. 사업개요  
 - 사업명 :  
 - 기간 :  
 - 예산 :  
2. 주요 성과지표  
3. 실적 수치 및 비교  
4. 정성효과 및 기여도  
5. 향후 계획

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "협업성과형":
            return common_guideline + f"""
1. 사업개요  
2. 참여부서 및 역할  
3. 공동 추진성과  
4. 협업 효과 및 사례  
5. 향후 협업 확대방안

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "성과홍보형":
            return common_guideline + f"""
1. 사업 개요  
2. 대표 성과 요약  
3. 수치 기반 성과  
4. 부서 기여 및 활용 포인트  
5. 향후 알릴 계획

📌 주요 키워드:
{keyword_text}
"""

    # 상황보고
    elif report_type == "상황보고":
        if format_type == "재난상황형":
            return common_guideline + f"""
1. 발생 개요  
 - 일시 :  
 - 장소 :  
 - 유형 :  
2. 피해 및 영향  
3. 긴급 대응 조치  
4. 후속 조치 및 복구 계획  
5. 유관 부서 협조사항

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "시설이상형":
            return common_guideline + f"""
1. 발생 개요  
2. 주요 증상 및 영향  
3. 대응 경과 및 조치 내용  
4. 원인 파악 결과  
5. 향후 재발방지 방안

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "민원폭증형":
            return common_guideline + f"""
1. 민원 발생 개요  
2. 민원유형별 통계 및 변화  
3. 주요 원인 분석  
4. 부서별 대응 현황  
5. 향후 대응 및 제도 개선 방향

📌 주요 키워드:
{keyword_text}
"""

    # 기타보고
    elif report_type == "기타보고":
        if format_type == "민원회신형":
            return common_guideline + f"""
1. 민원 개요  
 - 접수일 :  
 - 민원유형 :  
2. 민원 내용 요약  
3. 처리 결과  
4. 관련 근거 또는 규정  
5. 향후 안내사항

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "안내문형":
            return common_guideline + f"""
1. 프로그램 개요  
2. 운영일정 및 장소  
3. 신청방법 및 대상  
4. 부서 협조사항  
5. 유의사항 및 참고사항

📌 주요 키워드:
{keyword_text}
"""

        elif format_type == "내부의견서형":
            return common_guideline + f"""
1. 검토 배경 및 필요성  
2. 관련 기준 및 사례  
3. 실무 검토의견  
4. 예상 문제점 및 고려사항  
5. 최종 의견 및 제안사항

📌 주요 키워드:
{keyword_text}
"""

    else:
        return f"[❗] '{report_type} / {format_type}' 유형에 대한 프롬프트가 정의되지 않았습니다."

