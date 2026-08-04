# Fellowship Landing

위닝 펠로우십 공개 랜딩 페이지입니다.

## 현재 공개 상태

- **호스팅**: GitHub Pages
- **URL**: https://finito-corp.github.io/fellowship-landing/
- **서빙 파일**: 루트 `index.html`
- **동일 사본**: `lime-light.html`은 `index.html`과 바이트 단위로 같아야 합니다.
- **현재 상태**: 위닝 펠로우십 3기 지원 경로 준비중의 **비수집 안내 페이지**입니다.
  - 지원서·사전등록·수요조사·문의 입력란을 만들거나 외부 폼으로 연결하지 않습니다.
  - 이름, 연락처, 계정·결제 정보 등 지원 정보를 받지 않습니다.
  - 실제 3기 지원 CTA는 서버 검증, 최소 데이터 보관 기준, 운영자 모집함이 검증된 뒤에만 별도 release로 연결합니다.

## 배포

- GitHub Pages는 exact `main` SHA를 지정한 `Deploy approved Pages artifact` workflow로 배포합니다.
- 일반 절차: PR 검증 → exact SHA merge → Pages workflow 성공 → public URL 및 `deployment.json` SHA read-back.
- `main`에 push했다고 Production이 자동 전환되었다고 판단하지 않습니다.
- `index.html`과 `lime-light.html`의 불일치, legacy 외부 수집 링크, 또는 비수집 계약 위반은 release blocker입니다.

## 공개 파일 범위

- `index.html`, `lime-light.html`: 현재 공개 랜딩
- `privacy.html`, `terms.html`: 현 비수집 상태를 설명하는 안내 문서
- `invite/`: 과거 초대 아카이브이며 현재 모집 경로에서 링크하지 않습니다.

## 디자인 기준

- 노란색 `#fbbf24` 액센트와 다크 기반의 간결한 화면을 유지합니다.
- 모바일 320px 이상에서 한 줄의 안내와 비수집 상태가 먼저 읽혀야 합니다.
- 실제 모집 랜딩으로 바꾸는 작업은 3기 모집 패킷과 intake runtime contract를 함께 충족해야 합니다.
