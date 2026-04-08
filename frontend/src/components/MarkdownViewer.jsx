import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { api } from '../api';
import './MarkdownViewer.css';

export default function MarkdownViewer({ targetPath, filePath, onRequestCustomize }) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState('preview'); // 'preview' | 'raw'

  useEffect(() => {
    if (!targetPath || !filePath) return;
    setLoading(true);
    setError('');
    api.readFile(targetPath, filePath)
      .then((data) => setContent(data.content))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [targetPath, filePath]);

  if (!filePath) {
    return (
      <div className="mv-empty">
        <div className="mv-empty-icon">📄</div>
        <p>왼쪽에서 파일을 선택하면 내용이 표시됩니다</p>
      </div>
    );
  }

  return (
    <div className="markdown-viewer">
      {/* Header */}
      <div className="mv-header">
        <div className="mv-filepath">{filePath}</div>
        <div className="mv-header-actions">
          <div className="mv-view-toggle">
            <button
              className={`mv-toggle-btn ${viewMode === 'preview' ? 'active' : ''}`}
              onClick={() => setViewMode('preview')}
            >
              미리보기
            </button>
            <button
              className={`mv-toggle-btn ${viewMode === 'raw' ? 'active' : ''}`}
              onClick={() => setViewMode('raw')}
            >
              원문
            </button>
          </div>
          {onRequestCustomize && (
            <button
              className="mv-customize-btn"
              onClick={() => onRequestCustomize(filePath)}
            >
              ✏️ AI로 수정
            </button>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="mv-body">
        {loading && (
          <div className="mv-loading">로딩 중...</div>
        )}
        {error && (
          <div className="mv-error">오류: {error}</div>
        )}
        {!loading && !error && viewMode === 'preview' && (
          <div className="mv-content markdown-content">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        )}
        {!loading && !error && viewMode === 'raw' && (
          <pre className="mv-raw">{content}</pre>
        )}
      </div>
    </div>
  );
}
