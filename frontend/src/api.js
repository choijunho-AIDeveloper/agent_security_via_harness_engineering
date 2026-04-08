/**
 * API client for the LLM Council Harness Generator backend.
 */

const API_BASE = 'http://localhost:8001';

export const api = {
  /**
   * Validate and resolve a target path (no LLM calls).
   */
  async validatePath(targetPath) {
    const response = await fetch(`${API_BASE}/api/harness/validate-path`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_path: targetPath }),
    });
    if (!response.ok) throw new Error('경로 검증 실패');
    return response.json();
  },

  /**
   * Fast scan of the current project harness state (no LLM calls).
   */
  async analyzeHarness(targetPath) {
    const response = await fetch(`${API_BASE}/api/harness/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_path: targetPath }),
    });
    if (!response.ok) throw new Error('하네스 분석 실패');
    return response.json();
  },

  /**
   * Run the 3-stage council and stream stage-by-stage events.
   *
   * @param {string} projectDescription
   * @param {string} targetPath
   * @param {string} intent  "init" | "update" | "patch"
   * @param {function} onEvent  (eventType: string, event: object) => void
   */
  async previewHarness(projectDescription, targetPath, intent, onEvent, customizationRequest = null) {
    const response = await fetch(`${API_BASE}/api/harness/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_description: projectDescription,
        target_path: targetPath,
        intent,
        customization_request: customizationRequest,
      }),
    });

    if (!response.ok) throw new Error('하네스 미리보기 요청 실패');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      for (const line of chunk.split('\n')) {
        if (!line.startsWith('data: ')) continue;
        try {
          const event = JSON.parse(line.slice(6));
          onEvent(event.type, event);
        } catch {
          // skip malformed lines
        }
      }
    }
  },

  /**
   * Apply the approved harness package to the target directory.
   *
   * @param {string} targetPath
   * @param {Array}  guides       - file operations for guide documents
   * @param {object} sensors      - { settings_json, hook_scripts }
   * @param {string|null} claudeMd - CLAUDE.md content
   */
  async applyHarness(targetPath, guides, sensors, claudeMd = null) {
    const response = await fetch(`${API_BASE}/api/harness/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_path: targetPath,
        guides,
        sensors,
        claude_md: claudeMd,
      }),
    });
    if (!response.ok) throw new Error('하네스 적용 실패');
    return response.json();
  },

  /**
   * Read a single harness file's content.
   */
  async readFile(targetPath, filePath) {
    const response = await fetch(`${API_BASE}/api/harness/file`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_path: targetPath, file_path: filePath }),
    });
    if (!response.ok) throw new Error('파일 읽기 실패');
    return response.json();
  },

  /**
   * Scan and return the harness file list for the tree viewer.
   */
  async scanFiles(targetPath) {
    const response = await fetch(`${API_BASE}/api/harness/scan-files`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_path: targetPath }),
    });
    if (!response.ok) throw new Error('파일 스캔 실패');
    return response.json();
  },

  /**
   * Preview what the default template would write (no LLM, instant).
   *
   * @param {string} targetPath
   */
  async previewTemplate(targetPath) {
    const response = await fetch(`${API_BASE}/api/harness/template/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_path: targetPath }),
    });
    if (!response.ok) throw new Error('템플릿 미리보기 실패');
    return response.json();
  },

  /**
   * Apply the default template to the target directory (no LLM, instant).
   *
   * @param {string}   targetPath
   * @param {string[]|null} selectedPaths  null = all, array = selected only
   * @param {boolean}  includeSensors
   */
  async applyTemplate(targetPath, selectedPaths = null, includeSensors = true) {
    const response = await fetch(`${API_BASE}/api/harness/template/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_path: targetPath,
        selected_paths: selectedPaths,
        include_sensors: includeSensors,
      }),
    });
    if (!response.ok) throw new Error('템플릿 적용 실패');
    return response.json();
  },
};
