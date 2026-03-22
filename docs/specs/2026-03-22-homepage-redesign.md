---
title: Winning Fellowship Homepage Redesign
date: 2026-03-22
status: draft
target: university students (대학생)
reference: jejuair.net (fullscreen hero slider, smooth interactions)
---

# Winning Fellowship Homepage Redesign Spec

## Goal
- **있어보이는 것**: Premium, polished feel that impresses on first visit
- **참가 욕구 극대화**: "이 프로그램에 꼭 참가하고 싶다" — 강한 FOMO와 열망 유발
- **타겟**: 대학생 (20대 초반, 모바일 우선)

## Reference
- 제주항공 (jejuair.net): 풀스크린 히어로 슬라이더, 매끄러운 인터랙션
- 기존 fellowship-landing/index.html 콘텐츠 유지 및 강화

## Core Changes

### 1. Fullscreen Hero Slider
- 3~4 슬라이드, 5초 자동 전환
- 전환 효과: fade + subtle zoom-in (제주항공 스타일)
- 텍스트 등장: stagger fade-in (아래→위)
- 하단 인디케이터 도트 (클릭 가능)
- 스크롤 다운 화살표 바운스
- 이미지 미보유 → 텍스트 + 그래디언트 + 모션으로 대체
- 나중에 background-image 교체 가능한 구조

**Slide Content:**
| # | Key Message | Background | CTA |
|---|-------------|------------|-----|
| 1 | "당신의 인생을 스스로 결정하는 힘" | Dark + Gold gradient + blob | 3기 소식 받기 |
| 2 | "도전 · 성장 · 연결" + 1기 핵심 수치 | Purple → Dark gradient | 활동 둘러보기 |
| 3 | 2기 활동 안내 / 시즌 메시지 | Cyan → Dark gradient | 더 알아보기 |

### 2. AI Session Event Banner (Top Strip)
- nav 상단 고정 띠배너 (현재 구현 완료, 강화 방향)
- D-day 자동 계산, 사전조사 CTA
- 골드 글로우 + 보라 그라데이션 배경
- X 닫기 가능, 세션 날짜 지나면 자동 숨김

### 3. Enhanced Interactions (전체 페이지)
- 스크롤 트리거 애니메이션 강화 (Intersection Observer)
- 카드 호버: 부드러운 lift + glow
- 섹션 전환: parallax-like depth 효과
- 숫자 카운트업 애니메이션 (참가자 수 등)
- 부드러운 스크롤 스냅 (optional)

### 4. Existing Sections Enhancement
- About, Timeline, Fellow's Role, Reviews, FAQ, CTA 유지
- 각 섹션 인터랙션 품질 향상
- 타이포그래피 강화 (더 큰, 더 bold한 헤딩)

## Technical
- Stack: HTML + Tailwind CDN + Vanilla JS (현재 구조 유지)
- Font: Pretendard (현재 사용 중)
- Single file: index.html (현재 구조 유지)
- Mobile-first responsive

## Design Tokens
- Colors: 현재 팔레트 유지 (dark #141414, accent #fbbf24, purple, cyan)
- Border radius: 현재 유지 (rounded-xl, rounded-2xl)
- Spacing: Tailwind default

## Team Process
- **Dev Team**: PM/UX Lead + Frontend Developer
- **Consumer Team**: 대학생 페르소나 (20대 초반, 첫 방문자)
- Iterative: Design → Consumer Review → Refine → Implement → Consumer Review
