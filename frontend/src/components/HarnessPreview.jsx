import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './HarnessPreview.css';

const ACTION_CONFIG = {
  create: { label: 'CREATE', color: '#28a745', bg: '#f0fff4' },
  modify: { label: 'MODIFY', color: '#e67e22', bg: '#fff8f0' },
  delete: { label: 'DELETE', color: '#dc3545', bg: '#fff5f5' },
};

function FileOpCard({ op, checked, onToggle }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = ACTION_CONFIG[op.action] || ACTION_CONFIG.create;
  const hasError = !!op.error;

  return (
    <div
      className={`file-op-card ${hasError ? 'file-op-card--error' : ''}`}
      style={{ borderLeft: `4px solid ${cfg.color}` }}
    >
      <div className="file-op-header">
        <input
          type="checkbox"
          checked={checked}
          onChange={onToggle}
          disabled={hasError}
        />
        <span className="op-badge" style={{ background: cfg.color }}>
          {cfg.label}
        </span>
        <span className="op-path">{op.path}</span>
        {op.reason && <span className="op-reason">{op.reason}</span>}
        {(op.content_after || op.content_before) && (
          <button
            className="op-expand-btn"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? '접기 ▲' : '내용 보기 ▼'}
          </button>
        )}
        {hasError && <span className="op-error">{op.error}</span>}
      </div>

      {expanded && (
        <div className="op-content">
          {op.action === 'modify' && op.content_before && (
            <div className="content-before">
              <div className="content-label">이전 내용</div>
              <pre>{op.content_before}</pre>
            </div>
          )}
          {op.content_after && (
            <div className="content-after" style={{ background: cfg.bg }}>
              <div className="content-label">
                {op.action === 'modify' ? '변경 후 내용' : '파일 내용'}
              </div>
              <pre>{op.content_after}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SensorCard({ sensors }) {
  const [expanded, setExpanded] = useState(false);
  const settingsJson = sensors?.settings_json;
  const hookScripts = sensors?.hook_scripts || [];

  const hookCount = Object.values(settingsJson?.hooks || {})
    .flat()
    .length;

  if (!settingsJson && hookScripts.length === 0) return null;

  return (
    <div className="sensor-card">
      <div className="sensor-header">
        <span className="sensor-icon">⚙️</span>
        <div className="sensor-info">
          <span className="sensor-title">.claude/settings.json</span>
          <span className="sensor-meta">
            훅 {hookCount}개 | 스크립트 {hookScripts.length}개
          </span>
        </div>
        <button
          className="op-expand-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '접기 ▲' : '내용 보기 ▼'}
        </button>
      </div>

      {expanded && (
        <div className="op-content">
          {settingsJson && (
            <div className="content-after">
              <div className="content-label">settings.json</div>
              <pre>{JSON.stringify(settingsJson, null, 2)}</pre>
            </div>
          )}
          {hookScripts.map((script, i) => (
            <div key={i} className="content-after" style={{ marginTop: 8 }}>
              <div className="content-label">
                📜 {script.path}
                {script.executable && (
                  <span style={{ marginLeft: 8, color: '#888', fontSize: 12 }}>
                    (executable)
                  </span>
                )}
              </div>
              <pre>{script.content}</pre>
            </div>
          ))}
        </div>
      )}

      {hookScripts.length > 0 && (
        <div className="hook-script-list">
          {hookScripts.map((script, i) => (
            <div key={i} className="hook-script-item">
              <span className="op-badge" style={{ background: '#6c757d' }}>SCRIPT</span>
              <span className="op-path">{script.path}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function HarnessPreview({
  guidePreviews,
  sensors,
  onApply,
  isApplying,
}) {
  const [checkedGuides, setCheckedGuides] = useState(() =>
    Object.fromEntries(
      (guidePreviews || [])
        .filter((op) => !op.error)
        .map((op) => [op.path, true])
    )
  );
  const [includeSensors, setIncludeSensors] = useState(true);

  const allOps = guidePreviews || [];
  const validOps = allOps.filter((op) => !op.error);
  const selectedGuides = validOps.filter((op) => checkedGuides[op.path]);

  const hasSensors =
    sensors &&
    (Object.values(sensors.settings_json?.hooks || {}).some((arr) => arr.length > 0) ||
      (sensors.hook_scripts || []).length > 0);

  const handleToggleAll = () => {
    const allChecked = validOps.every((op) => checkedGuides[op.path]);
    const next = {};
    validOps.forEach((op) => (next[op.path] = !allChecked));
    setCheckedGuides(next);
  };

  const handleApply = () => {
    onApply({
      guides: selectedGuides.map((op) => ({
        action: op.action,
        path: op.path,
        content: op.content_after || '',
        reason: op.reason || '',
      })),
      sensors: includeSensors && hasSensors ? sensors : { settings_json: {}, hook_scripts: [] },
    });
  };

  const guideOps = allOps.filter(
    (op) => !op.path.startsWith('.claude') && op.path !== 'CLAUDE.md'
  );
  const claudeMdOp = allOps.find((op) => op.path === 'CLAUDE.md');
  const selectedCount =
    selectedGuides.length + (includeSensors && hasSensors ? 1 : 0);

  return (
    <div className="harness-preview">
      {/* Header */}
      <div className="preview-header">
        <h3>하네스 패키지 미리보기</h3>
        <p className="preview-subtitle">
          적용할 항목을 선택하세요. 개별 파일을 체크/해제하여 부분 적용이 가능합니다.
        </p>
      </div>

      {/* Guides Section */}
      <section className="preview-section">
        <div className="section-header">
          <div className="section-title">
            <span className="section-icon">🛡️</span>
            <span>Guides (Feedforward)</span>
            <span className="section-count">{guideOps.length}개 파일</span>
          </div>
          <button className="toggle-all-btn" onClick={handleToggleAll}>
            {validOps.every((op) => checkedGuides[op.path]) ? '전체 해제' : '전체 선택'}
          </button>
        </div>

        <div className="op-list">
          {guideOps.map((op) => (
            <FileOpCard
              key={op.path}
              op={op}
              checked={!!checkedGuides[op.path]}
              onToggle={() =>
                setCheckedGuides((prev) => ({ ...prev, [op.path]: !prev[op.path] }))
              }
            />
          ))}
        </div>
      </section>

      {/* CLAUDE.md Section */}
      {claudeMdOp && (
        <section className="preview-section">
          <div className="section-header">
            <div className="section-title">
              <span className="section-icon">📄</span>
              <span>CLAUDE.md (진입점)</span>
            </div>
          </div>
          <div className="op-list">
            <FileOpCard
              op={claudeMdOp}
              checked={!!checkedGuides[claudeMdOp.path]}
              onToggle={() =>
                setCheckedGuides((prev) => ({
                  ...prev,
                  [claudeMdOp.path]: !prev[claudeMdOp.path],
                }))
              }
            />
          </div>
        </section>
      )}

      {/* Sensors Section */}
      {hasSensors && (
        <section className="preview-section">
          <div className="section-header">
            <div className="section-title">
              <span className="section-icon">🔍</span>
              <span>Sensors (Feedback)</span>
            </div>
            <label className="sensor-toggle">
              <input
                type="checkbox"
                checked={includeSensors}
                onChange={(e) => setIncludeSensors(e.target.checked)}
              />
              포함
            </label>
          </div>
          <SensorCard sensors={sensors} />
        </section>
      )}

      {/* Apply Button */}
      <div className="preview-actions">
        <span className="selected-count">{selectedCount}개 항목 선택됨</span>
        <button
          className="apply-btn"
          onClick={handleApply}
          disabled={isApplying || selectedCount === 0}
        >
          {isApplying ? '적용 중...' : `선택한 항목 적용 (${selectedCount}개)`}
        </button>
      </div>
    </div>
  );
}
