#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st

def run():
    st.markdown("""
    <style>
    .main > div {
        padding-top: 0;
        padding-bottom: 0;
    }

    .header-section {
        background: #FF4B4B;
        color: white;
        padding: 40px 20px;
        text-align: center;
        margin-bottom: 0;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 300;
        opacity: 0.9;
        margin-bottom: 1.5rem;
    }

    .tool-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 6px 12px rgba(0,0,0,0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
    }

    .tool-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
    }

    .tool-icon {
        font-size: 2rem;
        margin-bottom: 0.4rem;
    }

    .tool-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
        color: #1f2937;
    }

    .tool-desc {
        font-size: 0.9rem;
        color: #4b5563;
    }
/
    .intro-section {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .intro-text {
        font-size: 1rem;
        color: #374151;
        max-width: 700px;
        margin: 0 auto 1rem auto;
    }

    .footer {
        border-top: 1px solid #e5e7eb;
        margin-top: 2rem;
        padding-top: 1rem;
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
        <div class="header-subtitle">인공지능으로 더 스마트한 행정서비스를 만들어갑니다</div>
    </div>
    """, unsafe_allow_html=True)

    # 소개
    st.markdown("""
    <div class="intro-section">
        <h2 style="font-size: 1.75rem; font-weight: 700; color: #1f2937; text-align: center; margin-bottom: 1rem;">
            AI 기반 스마트 업무도구
        </h2>
        <p class="intro-text" style="text-align: center;">
            충주시는 최신 인공지능 기술을 활용하여 공무원들의 업무 효율성을 높이고, 
            시민들에게 더 나은 서비스를 제공하기 위한 다양한 AI 도구들을 개발했습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI 도구 카드 (2행 3열)
    tools = [
        {"icon": "📄", "title": "보도자료 생성기", "desc": "GPT로 자동 보도자료 작성"},
        {"icon": "📋", "title": "공적조서 생성기", "desc": "공적사항 요약·작성 자동화"},
        {"icon": "📊", "title": "빅데이터 분석기", "desc": "축제·관광 데이터 기반 분석"},
        {"icon": "💬", "title": "카카오톡 홍보멘트 생성기", "desc": "OCR + GPT 기반 시민홍보 문구"},
        {"icon": "📈", "title": "엑셀 취합기", "desc": "엑셀 파일 자동 병합 및 다운로드"},
        {"icon": "📍", "title": "주소-좌표 변환기", "desc": "주소 ↔ 위경도 자동 변환"}
    ]

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

    # 푸터
    st.markdown("""
    <div class="footer">
        © 2025 충주시 AI 연구소 · All rights reserved.
    </div>
    """, unsafe_allow_html=True)

