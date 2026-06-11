import React from 'react';

interface LiveCodeEditorProps {
  code: string;
  language: 'python' | 'javascript' | 'sql';
  onCodeChange: (code: string) => void;
  onLanguageChange: (language: 'python' | 'javascript' | 'sql') => void;
  isAnalyzing: boolean;
  theme?: 'light' | 'dark';
}

export const LiveCodeEditor: React.FC<LiveCodeEditorProps> = ({
  code,
  language,
  onCodeChange,
  onLanguageChange,
  isAnalyzing,
  theme = 'light'
}) => {
  const bgColor = theme === 'light' ? '#ffffff' : '#1f1f1f';
  const borderColor = theme === 'light' ? '#e0e0e0' : '#333333';
  const textColor = theme === 'light' ? '#2c2c2c' : '#ffffff';
  const panelBg = theme === 'light' ? '#f5f5f5' : '#2a2a2a';
  const inputBg = theme === 'light' ? '#f9f9f9' : '#2a2a2a';

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      gap: '0',
      backgroundColor: bgColor,
      borderRadius: '4px',
      overflow: 'hidden',
      border: `1px solid ${borderColor}`
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px 16px',
        backgroundColor: panelBg,
        borderBottom: `1px solid ${borderColor}`,
        flexShrink: 0
      }}>
        <span style={{ fontSize: '12px', fontWeight: 600, color: textColor }}>
          💻 Language:
        </span>
        <select
          value={language}
          onChange={(e) => onLanguageChange(e.target.value as any)}
          style={{
            padding: '6px 10px',
            borderRadius: '3px',
            border: `1px solid ${borderColor}`,
            backgroundColor: inputBg,
            color: textColor,
            fontSize: '12px',
            fontFamily: "'DM Mono', monospace",
            cursor: 'pointer'
          }}
        >
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="sql">SQL</option>
        </select>

        {isAnalyzing && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            marginLeft: 'auto',
            color: '#f39c12',
            fontSize: '12px'
          }}>
            <span style={{ fontSize: '12px' }}>⏳</span>
            <span>Analyzing...</span>
          </div>
        )}

        <div style={{
          marginLeft: isAnalyzing ? '0' : 'auto',
          fontSize: '11px',
          color: '#999999'
        }}>
          {code.length} chars
        </div>
      </div>

      {/* Editor */}
      <textarea
        value={code}
        onChange={(e) => onCodeChange(e.target.value)}
        placeholder="Paste or type code here... (Python, JavaScript, or SQL)"
        style={{
          flex: 1,
          padding: '16px',
          border: 'none',
          borderRadius: '0',
          backgroundColor: bgColor,
          color: textColor,
          fontFamily: "'DM Mono', monospace",
          fontSize: '12px',
          lineHeight: '1.6',
          resize: 'none',
          outline: 'none',
          fontFeatureSettings: '"liga" off, "calt" off'
        }}
      />

      {/* Footer Info */}
      <div style={{
        padding: '8px 16px',
        backgroundColor: panelBg,
        borderTop: `1px solid ${borderColor}`,
        fontSize: '10px',
        color: '#999999',
        flexShrink: 0
      }}>
        💡 Results update automatically every 300ms • Supports Python, JavaScript, SQL
      </div>
    </div>
  );
};

export default LiveCodeEditor;
