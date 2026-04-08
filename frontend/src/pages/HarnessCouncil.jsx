import { useState, useCallback, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import HarnessPreview from '../components/HarnessPreview';
import FileTreePanel from '../components/FileTreePanel';
import MarkdownViewer from '../components/MarkdownViewer';
import { api } from '../api';
import './HarnessCouncil.css';

const STAGE_LABELS = {
  stage1: 'Stage 1 — 설계안 제출',
  stage2: 'Stage 2 — 동료 평가',
  stage3: 'Stage 3 — Chairman 합성',
};

// ============================================================
// Phase 1: Generation
// ============================================================

function GenerationPhase({ onComplete }) {
  const [mode, setMode] = useState('council'); // 'council' | 'template'
  const [form, setForm] = useState({ description: '', path: '', intent: 'init' });
  const [status, setStatus] = useState('idle');
  const [currentStage, setCurrentStage] = useState(null);
  const [stageData, setStageData] = useState({});
  const [dryRunData, setDryRunData] = useState(null);
  const [templateData, setTemplateData] = useState(null);
  const [isApplying, setIsApplying] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [pathStatus, setPathStatus] = useState(null); // null | 'checking' | {ok, resolved}
  const pathDebounceRef = useRef(null);

  const isRunning = status === 'scanning' || status === 'running';

  // Debounced path validation
  useEffect(() => {
    const raw = form.path.trim();
    if (!raw) { setPathStatus(null); return; }
    setPathStatus('checking');
    clearTimeout(pathDebounceRef.current);
    pathDebounceRef.current = setTimeout(async () => {
      try {
        const result = await api.validatePath(raw);
        setPathStatus({ ok: result.exists && result.is_dir, resolved: result.resolved, exists: result.exists, is_dir: result.is_dir });
      } catch {
        setPathStatus({ ok: false, resolved: null, exists: false, is_dir: false });
      }
    }, 600);
    return () => clearTimeout(pathDebounceRef.current);
  }, [form.path]);

  // ── Council flow ──
  const handleCouncilRun = async (e) => {
    e.preventDefault();
    if (!form.description.trim() || !form.path.trim()) return;
    setStatus('scanning');
    setStageData({});
    setDryRunData(null);
    setErrorMsg('');

    try {
      await api.previewHarness(form.description, form.path, form.intent, (type, event) => {
        switch (type) {
          case 'scan_complete':  setStatus('running'); setCurrentStage('stage1'); break;
          case 'stage1_complete': setStageData((p) => ({ ...p, stage1: event.data })); break;
          case 'stage2_start':   setCurrentStage('stage2'); break;
          case 'stage2_complete': setStageData((p) => ({ ...p, stage2: event.data, metadata: event.metadata })); break;
          case 'stage3_start':   setCurrentStage('stage3'); break;
          case 'stage3_complete': setStageData((p) => ({ ...p, stage3: event.data })); break;
          case 'dryrun_complete': setDryRunData(event.data); break;
          case 'complete':        setStatus('done'); setCurrentStage(null); break;
          case 'error':           setErrorMsg(event.message); setStatus('error'); break;
        }
      });
    } catch (err) {
      setErrorMsg(err.message); setStatus('error');
    }
  };

  const handleCouncilApply = async ({ guides, sensors }) => {
    setIsApplying(true);
    try {
      const claudeMdOp = guides.find((g) => g.path === 'CLAUDE.md');
      const result = await api.applyHarness(
        form.path,
        guides.filter((g) => g.path !== 'CLAUDE.md'),
        sensors,
        claudeMdOp?.content || null,
      );
      if (!result.failed?.length || result.success?.length > 0) {
        onComplete({ targetPath: form.path, source: 'council', applyResult: result });
      }
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsApplying(false);
    }
  };

  // ── Template flow ──
  const handleTemplateLoad = async () => {
    if (!form.path.trim()) return;
    setStatus('loading-template');
    setErrorMsg('');
    try {
      const data = await api.previewTemplate(form.path);
      setTemplateData(data);
      setStatus('template-ready');
    } catch (err) {
      setErrorMsg(err.message); setStatus('error');
    }
  };

  const handleTemplateApply = async ({ guides, sensors }) => {
    setIsApplying(true);
    try {
      const selectedPaths = guides.map((g) => g.path);
      const hasSensors = sensors && (
        Object.values(sensors.settings_json?.hooks || {}).some((a) => a.length > 0) ||
        (sensors.hook_scripts || []).length > 0
      );
      const result = await api.applyTemplate(form.path, selectedPaths, hasSensors);
      if (!result.failed?.length || result.success?.length > 0) {
        onComplete({ targetPath: form.path, source: 'template', applyResult: result });
      }
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsApplying(false);
    }
  };

  // Shared right-panel content
  const renderRight = () => {
    // Council preview
    if (mode === 'council' && dryRunData) {
      return (
        <HarnessPreview
          guidePreviews={dryRunData.guides_preview}
          sensors={dryRunData.sensors}
          onApply={handleCouncilApply}
          isApplying={isApplying}
        />
      );
    }
    // Template preview
    if (mode === 'template' && templateData) {
      return (
        <div style={{ height: '100%', overflow: 'auto' }}>
          <div style={{ padding: '20px 24px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: 18 }}>템플릿 미리보기</h3>
              <p style={{ margin: '4px 0 0', fontSize: 13, color: '#888' }}>
                총 <strong>{templateData.total_files}개</strong> 파일 — 적용할 항목을 선택하세요
              </p>
            </div>
          </div>
          <HarnessPreview
            guidePreviews={templateData.guides_preview}
            sensors={templateData.sensors}
            onApply={handleTemplateApply}
            isApplying={isApplying}
          />
        </div>
      );
    }
    // Empty states
    if (mode === 'template') {
      return (
        <div className="gen-empty">
          <div className="gen-empty-icon">📦</div>
          <h2>기본 하네스 템플릿</h2>
          <p>
            하네스 엔지니어링 원칙 기반<br />
            <strong>29개 문서 + 2개 훅</strong>을 즉시 생성합니다
          </p>
          <TemplateFeatureList />
          <button
            className="submit-btn"
            style={{ maxWidth: 220, marginTop: 8 }}
            onClick={handleTemplateLoad}
            disabled={!pathStatus?.ok || status === 'loading-template'}
          >
            {status === 'loading-template' ? '로딩 중...' : pathStatus?.ok ? '미리보기 로드' : '경로를 먼저 입력하세요'}
          </button>
        </div>
      );
    }
    // Council empty
    return (
      <div className="gen-empty">
        <div className="gen-empty-icon">🤖</div>
        <h2>AI Council 생성</h2>
        <p>
          3개의 LLM이 독립적으로 하네스를 설계하고<br />
          서로 평가한 뒤 Chairman이 최종 합성합니다
        </p>
        <div className="gen-flow-steps">
          <div className="gen-step">📝 Stage 1 — 독립 설계안 제출</div>
          <div className="gen-step-arrow">↓</div>
          <div className="gen-step">⚖️ Stage 2 — 익명 동료 평가</div>
          <div className="gen-step-arrow">↓</div>
          <div className="gen-step">🏛️ Stage 3 — Chairman 합성</div>
          <div className="gen-step-arrow">↓</div>
          <div className="gen-step gen-step--result">✅ 파일 적용 → 커스터마이징 루프</div>
        </div>
      </div>
    );
  };

  return (
    <div className="harness-council">
      {/* Left */}
      <div className="left-panel">
        <div className="panel-title">
          <h1>LLM Council</h1>
          <p>Harness Generator</p>
        </div>

        {/* Mode toggle */}
        <div className="mode-toggle">
          <button
            className={`mode-btn ${mode === 'council' ? 'mode-btn--active' : ''}`}
            onClick={() => { setMode('council'); setTemplateData(null); setStatus('idle'); }}
            disabled={isRunning}
          >
            🤖 AI Council
            <span>프로젝트 맞춤 생성</span>
          </button>
          <button
            className={`mode-btn ${mode === 'template' ? 'mode-btn--active' : ''}`}
            onClick={() => { setMode('template'); setDryRunData(null); setStatus('idle'); }}
            disabled={isRunning}
          >
            📦 기본 템플릿
            <span>즉시 로드 (LLM 없음)</span>
          </button>
        </div>

        {/* Shared: path */}
        <div className="form-group">
          <label>대상 디렉토리 경로</label>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="/home/user/my-project 또는 ~/my-project"
              value={form.path}
              onChange={(e) => setForm((f) => ({ ...f, path: e.target.value }))}
              disabled={isRunning}
              style={pathStatus && pathStatus !== 'checking'
                ? { borderColor: pathStatus.ok ? '#28a745' : '#dc3545', paddingRight: 28 }
                : { paddingRight: 28 }}
            />
            {pathStatus === 'checking' && (
              <span style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', fontSize: 13, color: '#aaa' }}>…</span>
            )}
            {pathStatus && pathStatus !== 'checking' && (
              <span style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', fontSize: 14 }}>
                {pathStatus.ok ? '✅' : '❌'}
              </span>
            )}
          </div>
          {pathStatus && pathStatus !== 'checking' && (
            <div style={{ fontSize: 11, marginTop: 3 }}>
              {pathStatus.ok ? (
                <span style={{ color: '#28a745' }}>
                  {pathStatus.resolved !== form.path.trim() ? `→ ${pathStatus.resolved}` : '디렉토리 확인됨'}
                </span>
              ) : (
                <span style={{ color: '#dc3545' }}>
                  {!pathStatus.exists ? '경로를 찾을 수 없습니다' : '디렉토리가 아닙니다'}
                  {pathStatus.resolved && ` (${pathStatus.resolved})`}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Council form */}
        {mode === 'council' && (
          <form className="harness-form" onSubmit={handleCouncilRun}>
            <div className="form-group">
              <label>프로젝트 설명</label>
              <textarea
                rows={5}
                placeholder="React + FastAPI SaaS 대시보드. 팀 5명, TypeScript 사용..."
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                disabled={isRunning}
              />
            </div>
            <button
              type="submit"
              className="submit-btn"
              disabled={isRunning || !form.description.trim() || !form.path.trim() || !pathStatus?.ok}
            >
              {isRunning
                ? `${STAGE_LABELS[currentStage] || '처리 중'}...`
                : 'AI Council 생성 시작'}
            </button>
          </form>
        )}

        {/* Stage progress */}
        {mode === 'council' && Object.keys(stageData).length > 0 && (
          <StageProgressBlock currentStage={currentStage} stageData={stageData} />
        )}

        {errorMsg && <div className="error-banner">오류: {errorMsg}</div>}
      </div>

      {/* Right */}
      <div className="right-panel">{renderRight()}</div>
    </div>
  );
}

// ============================================================
// Phase 2: Customization
// ============================================================

function CustomizationPhase({ targetPath, source, onReset }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [reloadTrigger, setReloadTrigger] = useState(0);
  // Customization panel state
  const [custOpen, setCustOpen] = useState(false);
  const [custRequest, setCustRequest] = useState('');
  const [custStatus, setCustStatus] = useState('idle'); // idle | running | preview | applying | done
  const [custStage, setCustStage] = useState(null);
  const [custStageData, setCustStageData] = useState({});
  const [dryRunData, setDryRunData] = useState(null);
  const [applyResult, setApplyResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  // Project description (user may provide for better Council context)
  const [projectDesc, setProjectDesc] = useState('');

  const handleRequestCustomize = (filePath) => {
    setSelectedFile(filePath);
    setCustOpen(true);
    setCustRequest(`"${filePath}" 파일을 수정해주세요: `);
  };

  const handleRunCustomization = async () => {
    if (!custRequest.trim()) return;
    setCustStatus('running');
    setCustStageData({});
    setDryRunData(null);
    setApplyResult(null);
    setErrorMsg('');

    try {
      await api.previewHarness(
        projectDesc || '(기존 하네스 커스터마이징)',
        targetPath,
        'patch',
        (type, event) => {
          switch (type) {
            case 'scan_complete':
            case 'stage1_start':   setCustStage('stage1'); break;
            case 'stage1_complete': setCustStageData((p) => ({ ...p, stage1: event.data })); break;
            case 'stage2_start':   setCustStage('stage2'); break;
            case 'stage2_complete': setCustStageData((p) => ({ ...p, stage2: event.data, metadata: event.metadata })); break;
            case 'stage3_start':   setCustStage('stage3'); break;
            case 'stage3_complete': setCustStageData((p) => ({ ...p, stage3: event.data })); break;
            case 'dryrun_complete': setDryRunData(event.data); setCustStatus('preview'); break;
            case 'error':           setErrorMsg(event.message); setCustStatus('idle'); break;
          }
        },
        custRequest,
      );
    } catch (err) {
      setErrorMsg(err.message); setCustStatus('idle');
    }
  };

  const handleApply = async ({ guides, sensors }) => {
    setCustStatus('applying');
    try {
      const claudeMdOp = guides.find((g) => g.path === 'CLAUDE.md');
      const result = await api.applyHarness(
        targetPath,
        guides.filter((g) => g.path !== 'CLAUDE.md'),
        sensors,
        claudeMdOp?.content || null,
      );
      setApplyResult(result);
      setCustStatus('done');
      setReloadTrigger((n) => n + 1);
    } catch (err) {
      setErrorMsg(err.message); setCustStatus('preview');
    }
  };

  const resetCust = () => {
    setCustStatus('idle');
    setDryRunData(null);
    setApplyResult(null);
    setCustRequest('');
    setCustStageData({});
  };

  const isRunning = custStatus === 'running';

  return (
    <div className="harness-council harness-council--customize">
      {/* Left: File tree */}
      <div className="cust-left">
        <div className="cust-left-header">
          <div className="cust-path" title={targetPath}>
            <span className="cust-source-badge">
              {source === 'template' ? '📦 템플릿' : '🤖 Council'}
            </span>
            <span>{targetPath.split('/').slice(-2).join('/')}</span>
          </div>
          <button className="reset-btn" onClick={onReset} title="처음으로 돌아가기">
            ↩ 새로 시작
          </button>
        </div>

        <FileTreePanel
          targetPath={targetPath}
          selectedFile={selectedFile}
          onSelectFile={setSelectedFile}
          reloadTrigger={reloadTrigger}
        />

        {/* Customization form */}
        <div className={`cust-form-area ${custOpen ? 'cust-form-area--open' : ''}`}>
          <button
            className="cust-form-toggle"
            onClick={() => setCustOpen((v) => !v)}
          >
            <span>✏️ AI 커스터마이징</span>
            <span>{custOpen ? '▲' : '▲'}</span>
          </button>

          {custOpen && (
            <div className="cust-form">
              {custStatus === 'idle' && (
                <>
                  <div className="cust-form-group">
                    <label>수정 요청</label>
                    <textarea
                      rows={4}
                      placeholder={`예: 이 프로젝트는 Python/Django를 사용합니다. TypeScript 관련 규칙을 Python에 맞게 수정하고 Django 관련 규칙을 추가해주세요.`}
                      value={custRequest}
                      onChange={(e) => setCustRequest(e.target.value)}
                    />
                  </div>
                  <div className="cust-form-group">
                    <label>프로젝트 설명 (선택)</label>
                    <input
                      type="text"
                      placeholder="더 나은 커스터마이징을 위해 입력 (비워도 됨)"
                      value={projectDesc}
                      onChange={(e) => setProjectDesc(e.target.value)}
                    />
                  </div>
                  <button
                    className="submit-btn"
                    onClick={handleRunCustomization}
                    disabled={!custRequest.trim()}
                  >
                    Council로 수정
                  </button>
                </>
              )}
              {isRunning && (
                <CustProgress stage={custStage} stageData={custStageData} />
              )}
              {errorMsg && <div className="error-banner" style={{ margin: '8px 0' }}>오류: {errorMsg}</div>}
              {custStatus === 'done' && applyResult && (
                <div>
                  <div className="apply-result apply-result--success" style={{ padding: 10 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: '#28a745' }}>
                      ✅ {applyResult.success?.length}개 파일 적용 완료
                    </div>
                  </div>
                  <button className="toggle-all-btn" style={{ marginTop: 8, width: '100%' }} onClick={resetCust}>
                    다시 커스터마이징
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right: Markdown viewer or Preview */}
      <div className="cust-right">
        {custStatus === 'preview' && dryRunData ? (
          <div style={{ height: '100%', overflow: 'auto' }}>
            <div style={{ padding: '16px 24px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: 16 }}>변경 미리보기</h3>
              <button className="toggle-all-btn" onClick={resetCust}>취소</button>
            </div>
            <HarnessPreview
              guidePreviews={dryRunData.guides_preview}
              sensors={dryRunData.sensors}
              onApply={handleApply}
              isApplying={custStatus === 'applying'}
            />
          </div>
        ) : (
          <MarkdownViewer
            targetPath={targetPath}
            filePath={selectedFile}
            onRequestCustomize={handleRequestCustomize}
          />
        )}
      </div>
    </div>
  );
}

// ============================================================
// Shared sub-components
// ============================================================

function StageProgressBlock({ currentStage, stageData }) {
  const [open, setOpen] = useState(null);
  const list = [
    { key: 'stage1', emoji: '📝', label: 'Stage 1' },
    { key: 'stage2', emoji: '⚖️', label: 'Stage 2' },
    { key: 'stage3', emoji: '🏛️', label: 'Stage 3' },
  ];
  return (
    <div className="stage-progress">
      {list.map(({ key, emoji, label }) => {
        const done = !!stageData[key];
        const active = currentStage === key && !done;
        return (
          <div key={key} className={`stage-block ${done ? 'stage-block--done' : ''} ${active ? 'stage-block--loading' : ''}`}>
            <div className="stage-block-header" onClick={() => done && setOpen(open === key ? null : key)}>
              <span className="stage-emoji">{emoji}</span>
              <span className="stage-label">{STAGE_LABELS[key]}</span>
              {active && <span className="loading-dot">...</span>}
              {done && <span className="stage-toggle">{open === key ? '▲' : '▼'}</span>}
            </div>
            {done && open === key && (
              <div className="stage-block-content">
                {key === 'stage1' && <MiniStage1 proposals={stageData.stage1} />}
                {key === 'stage3' && <MiniStage3 stage3={stageData.stage3} />}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function CustProgress({ stage, stageData }) {
  return (
    <div className="cust-progress">
      {['stage1', 'stage2', 'stage3'].map((key) => (
        <div key={key} className={`cust-stage-dot ${stageData[key] ? 'done' : stage === key ? 'active' : ''}`}>
          {stageData[key] ? '✓' : stage === key ? '…' : '○'} {STAGE_LABELS[key].split(' — ')[0]}
        </div>
      ))}
    </div>
  );
}

function MiniStage1({ proposals }) {
  const [tab, setTab] = useState(0);
  if (!proposals?.length) return null;
  return (
    <div>
      <div className="tabs">
        {proposals.map((p, i) => (
          <button key={i} className={`tab ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>
            {p.model.split('/')[1] || p.model}
          </button>
        ))}
      </div>
      <div className="tab-body markdown-content" style={{ maxHeight: 200 }}>
        <ReactMarkdown>{proposals[tab]?.proposal || ''}</ReactMarkdown>
      </div>
    </div>
  );
}

function MiniStage3({ stage3 }) {
  if (!stage3) return null;
  return (
    <div className="reasoning-box">
      <div className="reasoning-label">Chairman 근거</div>
      <p style={{ fontSize: 12 }}>{stage3.reasoning}</p>
    </div>
  );
}

function TemplateFeatureList() {
  return (
    <div className="gen-feature-list">
      {[
        ['🛡️', '.agent/ (5개)', 'Charter, 금지 목록, 승인 목록, 판단 원칙, 실행 정책'],
        ['📚', 'docs/ (23개)', '제품, 아키텍처, 엔지니어링, 워크플로우, 품질, 거버넌스'],
        ['🔍', 'Sensors (.claude/)', '시크릿 차단 훅 + 테스트 누락 경고 훅'],
        ['📄', 'CLAUDE.md', 'Agent 진입점 + 전체 하네스 참조 맵'],
      ].map(([icon, title, desc]) => (
        <div key={title} className="gen-feature">
          <span>{icon}</span>
          <div>
            <strong>{title}</strong>
            <span>{desc}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

// ============================================================
// Root
// ============================================================

export default function HarnessCouncil() {
  const [phase, setPhase] = useState('generation'); // 'generation' | 'customization'
  const [custContext, setCustContext] = useState(null);

  const handleGenerationComplete = useCallback(({ targetPath, source }) => {
    setCustContext({ targetPath, source });
    setPhase('customization');
  }, []);

  const handleReset = useCallback(() => {
    setPhase('generation');
    setCustContext(null);
  }, []);

  if (phase === 'customization' && custContext) {
    return (
      <CustomizationPhase
        targetPath={custContext.targetPath}
        source={custContext.source}
        onReset={handleReset}
      />
    );
  }

  return <GenerationPhase onComplete={handleGenerationComplete} />;
}
