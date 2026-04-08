import { useState, useEffect } from 'react';
import { api } from '../api';
import './FileTreePanel.css';

// 파일 확장자/경로 기반 아이콘
function fileIcon(path) {
  if (path.startsWith('.agent/')) return '🛡️';
  if (path.startsWith('.claude/hooks/')) return '⚙️';
  if (path.startsWith('.claude/')) return '🔧';
  if (path === 'CLAUDE.md') return '📄';
  if (path.startsWith('docs/10_product/')) return '🎯';
  if (path.startsWith('docs/20_architecture/')) return '🏗️';
  if (path.startsWith('docs/30_engineering/')) return '⚗️';
  if (path.startsWith('docs/40_workflow/')) return '🔄';
  if (path.startsWith('docs/50_quality/')) return '✅';
  if (path.startsWith('docs/60_templates/')) return '📋';
  if (path.startsWith('docs/70_governance/')) return '📜';
  if (path.endsWith('.sh')) return '💻';
  if (path.endsWith('.json')) return '⚙️';
  return '📝';
}

// 디렉토리 그룹 정의
const DIR_GROUPS = [
  { key: '.agent', label: '.agent/', desc: 'Agent 제어 (최우선)', icon: '🛡️' },
  { key: 'docs/10_product', label: '10_product/', desc: '제품 도메인', icon: '🎯' },
  { key: 'docs/20_architecture', label: '20_architecture/', desc: '구조적 제약', icon: '🏗️' },
  { key: 'docs/30_engineering', label: '30_engineering/', desc: '코드 품질', icon: '⚗️' },
  { key: 'docs/40_workflow', label: '40_workflow/', desc: '개발 프로세스', icon: '🔄' },
  { key: 'docs/50_quality', label: '50_quality/', desc: '품질 보증', icon: '✅' },
  { key: 'docs/60_templates', label: '60_templates/', desc: '템플릿', icon: '📋' },
  { key: 'docs/70_governance', label: '70_governance/', desc: '문서 운영', icon: '📜' },
  { key: '.claude', label: '.claude/', desc: 'Sensors (훅)', icon: '🔧' },
];

function groupFiles(files) {
  const groups = {};
  const root = [];

  for (const f of files) {
    if (f.dir === '') {
      root.push(f);
      continue;
    }
    const group = DIR_GROUPS.find((g) => f.path.startsWith(g.key + '/'));
    const key = group ? group.key : f.dir;
    if (!groups[key]) groups[key] = [];
    groups[key].push(f);
  }

  return { groups, root };
}

export default function FileTreePanel({ targetPath, selectedFile, onSelectFile, reloadTrigger }) {
  const [files, setFiles] = useState([]);
  const [collapsed, setCollapsed] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!targetPath) return;
    setLoading(true);
    api.scanFiles(targetPath)
      .then((data) => setFiles(data.files || []))
      .catch(() => setFiles([]))
      .finally(() => setLoading(false));
  }, [targetPath, reloadTrigger]);

  const toggleCollapse = (key) =>
    setCollapsed((prev) => ({ ...prev, [key]: !prev[key] }));

  const { groups, root } = groupFiles(files);

  if (loading) {
    return <div className="file-tree-loading">파일 목록 로딩 중...</div>;
  }

  if (files.length === 0) {
    return <div className="file-tree-empty">파일이 없습니다</div>;
  }

  return (
    <div className="file-tree">
      {/* Grouped directories */}
      {DIR_GROUPS.map(({ key, label, desc, icon }) => {
        const groupFiles = groups[key];
        if (!groupFiles?.length) return null;
        const isCollapsed = collapsed[key];

        return (
          <div key={key} className="tree-group">
            <div
              className="tree-group-header"
              onClick={() => toggleCollapse(key)}
            >
              <span className="tree-group-toggle">{isCollapsed ? '▶' : '▼'}</span>
              <span className="tree-group-icon">{icon}</span>
              <div className="tree-group-info">
                <span className="tree-group-label">{label}</span>
                <span className="tree-group-desc">{desc}</span>
              </div>
              <span className="tree-group-count">{groupFiles.length}</span>
            </div>

            {!isCollapsed && (
              <div className="tree-files">
                {groupFiles.map((f) => (
                  <button
                    key={f.path}
                    className={`tree-file ${selectedFile === f.path ? 'tree-file--active' : ''}`}
                    onClick={() => onSelectFile(f.path)}
                  >
                    <span className="tree-file-icon">{fileIcon(f.path)}</span>
                    <span className="tree-file-name">{f.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* Root-level files (CLAUDE.md, etc.) */}
      {root.length > 0 && (
        <div className="tree-group tree-group--root">
          {root.map((f) => (
            <button
              key={f.path}
              className={`tree-file tree-file--root ${selectedFile === f.path ? 'tree-file--active' : ''}`}
              onClick={() => onSelectFile(f.path)}
            >
              <span className="tree-file-icon">{fileIcon(f.path)}</span>
              <span className="tree-file-name">{f.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
