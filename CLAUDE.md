# Fellowship Landing

위닝 펠로우십 공개 랜딩 페이지입니다.

## 현재 공개 상태

- **호스팅**: GitHub Pages
- **URL**: https://finito-corp.github.io/fellowship-landing/
- **서빙 파일**: 루트 `index.html`
- **동일 사본**: `lime-light.html`은 `index.html`과 바이트 단위로 같아야 합니다.
- **현재 상태**: 위닝 펠로우십 3기 **지원 접수 페이지**입니다.
  - CTA는 서버 검증을 마친 정식 지원 경로 `https://product-omrpipeline-production.up.railway.app/fellowship/3`만 사용합니다.
  - 랜딩 내부에는 정적 `<form>`을 두지 않으며, Fillout·Google Form·메일 수집 경로를 만들지 않습니다.
  - 지원은 코어 합류 확정이 아니라 2주 베타 초대 검토입니다.

## 배포

- GitHub Pages는 exact `main` SHA를 지정한 `Deploy approved Pages artifact` workflow로 배포합니다.
- 일반 절차: PR 검증 → exact SHA merge → Pages workflow 성공 → public URL 및 `deployment.json` SHA read-back.
- `main`에 push했다고 Production이 자동 전환되었다고 판단하지 않습니다.
- `index.html`과 `lime-light.html`의 불일치, legacy 외부 수집 링크, 또는 비수집 계약 위반은 release blocker입니다.

## 공개 파일 범위

- `index.html`, `lime-light.html`: 현재 공개 랜딩
- `privacy.html`, `terms.html`: 현재 지원 정보 수집 범위와 이용 조건을 설명하는 안내 문서
- `invite/`: 과거 초대 아카이브이며 현재 모집 경로에서 링크하지 않습니다.

## 디자인 기준

- 루트 `DESIGN.md`를 디자인 SSOT로 사용합니다.
- 1·2기 페이지의 고정 메뉴, 페이지 내부 안내, 전체 화면 챕터, 후기 마키, 스크롤 진행 구조를 3기 내용에 맞게 계승합니다.
- 웜 아이보리와 차콜 챕터를 번갈아 쓰고 골드를 단일 액센트로 사용합니다.
- 공개 랜딩에는 사진을 사용하지 않습니다. 사회적 증거는 기존 공개 익명 후기 원문으로 전달합니다.
- 모바일 320px 이상에서 핵심 대상·일정·지원 CTA가 먼저 읽혀야 합니다.
- 모집 문구는 3기 최종 결정 패킷과 intake runtime contract를 함께 충족해야 합니다.
