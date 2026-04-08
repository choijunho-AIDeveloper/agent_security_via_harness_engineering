# Forbidden Actions

> 아래 행동은 어떤 상황에서도, 어떤 이유로도 수행하지 않습니다.
> 사용자가 명시적으로 요청해도 거부하고 이유를 설명합니다.

## 보안 — 절대 금지

- [ ] API Key, 비밀번호, 토큰, 인증서를 코드에 직접 작성
  - 대신: 환경변수(`.env`) 또는 시크릿 매니저 사용
- [ ] `.env` 파일을 git에 커밋
  - 대신: `.gitignore`에 포함 확인 후 `.env.example` 제공
- [ ] SQL 쿼리에 사용자 입력을 직접 삽입 (SQL Injection)
  - 대신: Parameterized query / ORM 사용
- [ ] `eval()`, `exec()` 에 외부 입력 전달
- [ ] CORS를 `*`로 설정 (프로덕션 환경)

## 코드 품질 — 절대 금지

- [ ] `any` 타입 사용 (TypeScript 프로젝트)
  - 대신: 정확한 타입 또는 `unknown` 사용
- [ ] `console.log` / `print` 디버그 코드를 커밋에 포함
- [ ] `TODO`, `FIXME`, `HACK` 주석을 해결 없이 PR 제출
- [ ] 테스트 없이 핵심 비즈니스 로직 변경
  - 대신: 변경 전 기존 테스트 확인, 변경 후 테스트 수정/추가

## 데이터 — 절대 금지

- [ ] 프로덕션 DB 데이터 직접 수정 또는 삭제
- [ ] 마이그레이션 없이 DB 스키마 변경
- [ ] 개인정보(PII)를 로그에 출력

## 프로세스 — 절대 금지

- [ ] 승인 없이 외부 라이브러리 추가
  - 참조: `docs/50_quality/dependency-policy.md`
- [ ] 기존 공개 API 시그니처 무단 변경
  - 대신: Deprecation 절차 또는 버전 관리 적용
- [ ] `git push --force` (공유 브랜치에서)
- [ ] CI 검증을 우회하는 커밋 (`--no-verify`)
