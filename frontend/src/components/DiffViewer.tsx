import React, { useMemo } from 'react';

interface DiffViewerProps {
  original: string;
  refactored: string;
  fileName?: string;
  style?: 'split' | 'unified';
}

const computeCharDiff = (original: string, refactored: string) => {
  const originalChars = original.split('');
  const refactoredChars = refactored.split('');

  // Simple character-level diff using LCS-inspired approach
  const originalHighlights: { type: 'unchanged' | 'removed' | 'added', text: string }[] = [];
  const refactoredHighlights: { type: 'unchanged' | 'removed' | 'added', text: string }[] = [];

  let i = 0, j = 0;
  while (i < originalChars.length || j < refactoredChars.length) {
    if (i < originalChars.length && j < refactoredChars.length && originalChars[i] === refactoredChars[j]) {
      originalHighlights.push({ type: 'unchanged', text: originalChars[i] });
      refactoredHighlights.push({ type: 'unchanged', text: refactoredChars[j] });
      i++;
      j++;
    } else if (i < originalChars.length && (j >= refactoredChars.length || originalChars[i] !== refactoredChars[j])) {
      originalHighlights.push({ type: 'removed', text: originalChars[i] });
      i++;
    } else {
      refactoredHighlights.push({ type: 'added', text: refactoredChars[j] });
      j++;
    }
  }

  return { originalHighlights, refactoredHighlights };
};

const DiffLine: React.FC<{
  highlights: { type: 'unchanged' | 'removed' | 'added', text: string }[];
  isOriginal?: boolean;
}> = ({ highlights }) => {
  return (
    <div className="diff-line" style={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
      {highlights.map((h, idx) => {
        if (h.type === 'unchanged') {
          return <span key={idx}>{h.text}</span>;
        } else if (h.type === 'removed') {
          return (
            <span key={idx} style={{ backgroundColor: '#fee', color: '#c33', textDecoration: 'line-through' }}>
              {h.text}
            </span>
          );
        } else {
          return (
            <span key={idx} style={{ backgroundColor: '#efe', color: '#3c3' }}>
              {h.text}
            </span>
          );
        }
      })}
    </div>
  );
};

export const DiffViewer: React.FC<DiffViewerProps> = ({
  original,
  refactored,
  fileName = 'Code',
  style = 'split'
}) => {
  const { originalHighlights, refactoredHighlights } = useMemo(
    () => computeCharDiff(original, refactored),
    [original, refactored]
  );

  if (style === 'split') {
    return (
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '1px',
        backgroundColor: '#ddd',
        fontSize: '12px',
        borderRadius: '4px',
        overflow: 'hidden',
        border: '1px solid #ccc'
      }}>
        {/* Original */}
        <div style={{ padding: '12px', backgroundColor: '#f5f5f5' }}>
          <div style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#666',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            📝 Original
          </div>
          <div style={{
            backgroundColor: '#fff',
            padding: '8px',
            borderRadius: '3px',
            maxHeight: '400px',
            overflowY: 'auto',
            border: '1px solid #eee'
          }}>
            <DiffLine highlights={originalHighlights} isOriginal />
          </div>
        </div>

        {/* Refactored */}
        <div style={{ padding: '12px', backgroundColor: '#f5f5f5' }}>
          <div style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#666',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            ✨ Refactored
          </div>
          <div style={{
            backgroundColor: '#fff',
            padding: '8px',
            borderRadius: '3px',
            maxHeight: '400px',
            overflowY: 'auto',
            border: '1px solid #eee'
          }}>
            <DiffLine highlights={refactoredHighlights} />
          </div>
        </div>
      </div>
    );
  }

  // Unified view
  return (
    <div style={{
      backgroundColor: '#fff',
      border: '1px solid #ccc',
      borderRadius: '4px',
      overflow: 'hidden',
      fontSize: '12px'
    }}>
      <div style={{
        padding: '12px',
        backgroundColor: '#f5f5f5',
        borderBottom: '1px solid #eee',
        fontSize: '11px',
        fontWeight: 600,
        color: '#666',
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
      }}>
        {fileName}
      </div>
      <div style={{
        padding: '12px',
        fontFamily: 'monospace',
        maxHeight: '500px',
        overflowY: 'auto'
      }}>
        <div style={{ marginBottom: '8px' }}>
          <div style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#c33',
            marginBottom: '4px',
            textTransform: 'uppercase'
          }}>
            Removed
          </div>
          <DiffLine highlights={originalHighlights.filter(h => h.type !== 'unchanged')} isOriginal />
        </div>
        <div>
          <div style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#3c3',
            marginBottom: '4px',
            textTransform: 'uppercase'
          }}>
            Added
          </div>
          <DiffLine highlights={refactoredHighlights.filter(h => h.type !== 'unchanged')} />
        </div>
      </div>
    </div>
  );
};

export default DiffViewer;
