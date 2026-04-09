# Fellowship Landing - CLAUDE.md

위닝 펠로우십 랜딩 페이지 프로젝트.

## 배포

- **호스팅**: GitHub Pages
- **URL**: https://finito-corp.github.io/fellowship-landing/
- **배포 방식**: `main` 브랜치 push → 자동 배포 (1~2분 소요)
- **서빙 파일**: `index.html` (루트)

## 주요 파일

- **메인**: `index.html` (배포 대상) + `lime-light.html` (동일 내용 유지)
- 구버전: `gold.html`, `neon.html`, `lime.html` — 참고용
- **편집 후**: `index.html`과 `lime-light.html` 양쪽 모두 동일하게 유지할 것

## 디자인 시스템

- **액센트 컬러**: 노란색(#fbbf24) 단일 사용 — 파란색은 브랜드 색이지만 웹에서는 제외
- **레이아웃**: 다크/라이트 교차 섹션
- **밝은 섹션**: `bg-surface` 통일
- **히어로**: 다크 배경 + 수치 카드(`border-accent/20 bg-accent/5`)
- **섹션 순서**: Hero(DARK) → About(LIGHT) → Career(DARK) → Global(LIGHT) → Life(DARK) → Your Own(LIGHT) → Fellow's Role(LIGHT) → CTA(DARK)

## 디자인 선호도

- 단색 액센트 통일 (색이 섞이면 이질감)
- 밝은 배경은 `bg-surface`로 통일
- 히어로는 다크 배경 (경계감 있는 첫인상)

## Google Form 주의사항

- Google Forms API(addFormQuestion)는 질문을 **맨 위(position 0)**에 삽입함
- 따라서 원하는 순서대로 나오게 하려면 **역순으로 추가**해야 함
- 예: Q1→Q2→Q3 순서를 원하면, Q3→Q2→Q1 순서로 addFormQuestion 호출

## TODO

- [ ] 3기 지원하기 버튼에 실제 지원 링크 연결
- [ ] 인스타그램 보기 버튼에 실제 인스타 링크 연결
- [ ] 문의하기 버튼 링크 연결
- [ ] 최종 확정 후 `lime-light.html` → `index.html`로 복사
