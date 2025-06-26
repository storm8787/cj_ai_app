#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st

def run():
    # 페이지 내부 스타일 적용
    st.markdown("""
    <style>
    .main > div {
        padding-top: 0;
        padding-bottom: 0;
    }

    .header-section {
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white;
        padding: 80px 20px;
        text-align: center;
        margin-bottom: 0;
    }

    .header-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .header-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.95;
        margin-bottom: 2rem;
    }

    .tool-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem auto;
    }

    .tool-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .tool-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 32px rgba(0,0,0,0.12);
    }

    .tool-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .tool-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.4rem;
        color: #1f2937;
    }

    .tool-desc {
        font-size: 0.95rem;
        color: #4b5563;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 3rem;
        color: #1f2937;
    }

    .stats {
        display: flex;
        justify-content: space-around;
        margin-top: 2rem;
        flex-wrap: wrap;
    }

    .stat-box {
        text-align: center;
        padding: 1rem;
        flex: 1 1 200px;
    }

    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1e3a8a;
    }

    .stat-label {
        color: #6b7280;
        font-size: 0.9rem;
    }

    .footer {
        border-top: 1px solid #e5e7eb;
        padding-top: 2rem;
        margin-top: 4rem;
        text-align: center;
        font-size: 0.85rem;
        color: #9ca3af;
    }
    </style>
    """, unsafe_allow_html=True)

    # 헤더
    st.markdown("""
    <div class="header-section">
        <div class="header-title">충주시 AI 연구소</div>
        <div class="header-subtitle">AI로 더 똑똑한 행정서비스를 만들어갑니다</div>
    </div>
    """, unsafe_allow_html=True)

    # 소개
    st.markdown("""
    <p style='text-align: center; font-size:1.1rem; color:#374151; max-width:800px; margin:2rem auto 3rem auto;'>
        충주시는 최신 인공지능 기술을 바탕으로 공무원의 업무 효율성을 높이고, 시민에게 보다 나은 행정 서비스를 제공하기 위해 다양한 스마트 도구를 개발·운영하고 있습니다.
    </p>
    """, unsafe_allow_html=True)
        # AI 도구 카드
    tools = [
        {"icon": "📄", "title": "보도자료 생성기", "desc": "GPT로 자동 보도자료 작성"},
        {"icon": "📋", "title": "공적조서 생성기", "desc": "공적사항 요약·작성 자동화"},
        {"icon": "📊", "title": "빅데이터 분석기", "desc": "축제·관광 데이터 기반 분석"},
        {"icon": "💬", "title": "카카오톡 홍보멘트 생성기", "desc": "OCR + GPT 기반 시민홍보 문구"},
        {"icon": "📈", "title": "엑셀 취합기", "desc": "엑셀 파일 자동 병합 및 다운로드"},
        {"icon": "📍", "title": "주소-좌표 변환기", "desc": "주소 ↔ 위경도 자동 변환"}
    ]

    # 2행 3열 그리드 카드 레이아웃
    for i in range(0, len(tools), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(tools):
                tool = tools[i + j]
                with cols[j]:
                    st.markdown(f"""
                    <div class="tool-card">
                        <div class="tool-icon">{tool['icon']}</div>
                        <div class="tool-title">{tool['title']}</div>
                        <div class="tool-desc">{tool['desc']}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # 통계
    st.markdown('<div class="section-title">AI 도구 활용 현황</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="stats">
        <div class="stat-box">
            <div class="stat-number">6</div>
            <div class="stat-label">도입된 AI 도구</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">1,240+</div>
            <div class="stat-label">월간 사용량</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">85%</div>
            <div class="stat-label">업무 효율성 향상</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">24/7</div>
            <div class="stat-label">지속 운영</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 푸터
    st.markdown("""
    <div class="footer">
        © 2025 충주시 AI 연구소 · All rights reserved.
    </div>
    """, unsafe_allow_html=True)

