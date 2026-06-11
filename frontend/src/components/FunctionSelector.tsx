import React, { useState, useMemo } from 'react';

export interface FunctionSelectItem {
  id: string;
  name: string;
  file: string;
  line: number;
  complexity: number;
  severity: 'low' | 'medium' | 'high';
  code: string;
}

interface FunctionSelectorProps {
  functions: FunctionSelectItem[];
  onSelectionChange?: (selected: FunctionSelectItem[]) => void;
  categoryFilter?: 'complexity' | 'security' | 'style' | 'all';
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'high':
      return '#e74c3c';
    case 'medium':
      return '#f39c12';
    case 'low':
      return '#27ae60';
    default:
      return '#95a5a6';
  }
};

const getSeverityLabel = (severity: string) => {
  switch (severity) {
    case 'high':
      return '🔴 High';
    case 'medium':
      return '🟡 Medium';
    case 'low':
      return '🟢 Low';
    default:
      return '⚪ Unknown';
  }
};

export const FunctionSelector: React.FC<FunctionSelectorProps> = ({
  functions,
  onSelectionChange,
  categoryFilter = 'all'
}) => {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filteredFunctions = useMemo(() => {
    if (categoryFilter === 'all') {
      return functions;
    }

    return functions.filter(fn => {
      if (categoryFilter === 'complexity') {
        return fn.complexity > 5;
      }
      // More category filters can be added here
      return true;
    });
  }, [functions, categoryFilter]);

  const handleSelectToggle = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);

    // Notify parent
    const selectedFunctions = filteredFunctions.filter(f => newSelected.has(f.id));
    onSelectionChange?.(selectedFunctions);
  };

  const handleSelectAll = () => {
    if (selectedIds.size === filteredFunctions.length) {
      setSelectedIds(new Set());
      onSelectionChange?.([]);
    } else {
      const allIds = new Set(filteredFunctions.map(f => f.id));
      setSelectedIds(allIds);
      onSelectionChange?.(filteredFunctions);
    }
  };

  const isAllSelected = selectedIds.size > 0 && selectedIds.size === filteredFunctions.length;

  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '4px',
      backgroundColor: '#f9f9f9',
      padding: '0'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '12px',
        borderBottom: '1px solid #eee',
        backgroundColor: '#f5f5f5'
      }}>
        <input
          type="checkbox"
          checked={isAllSelected}
          onChange={handleSelectAll}
          style={{ cursor: 'pointer', width: '18px', height: '18px' }}
        />
        <span style={{ fontWeight: 600, color: '#333' }}>
          {selectedIds.size > 0 ? `${selectedIds.size} selected` : 'Select functions to refactor'}
        </span>
      </div>

      {/* Functions List */}
      <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
        {filteredFunctions.length === 0 ? (
          <div style={{
            padding: '24px',
            textAlign: 'center',
            color: '#999',
            fontSize: '14px'
          }}>
            No functions available
          </div>
        ) : (
          filteredFunctions.map((fn) => (
            <div key={fn.id} style={{
              borderBottom: '1px solid #eee',
              backgroundColor: selectedIds.has(fn.id) ? '#f0f7ff' : '#fff'
            }}>
              {/* Row */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onClick={() => handleSelectToggle(fn.id)}
              >
                <input
                  type="checkbox"
                  checked={selectedIds.has(fn.id)}
                  onChange={() => {}}
                  style={{ cursor: 'pointer', width: '18px', height: '18px' }}
                  onClick={(e) => e.stopPropagation()}
                />

                <div style={{ flex: 1 }}>
                  <div style={{
                    fontWeight: 600,
                    color: '#333',
                    fontSize: '14px',
                    marginBottom: '4px'
                  }}>
                    {fn.name}
                  </div>
                  <div style={{
                    display: 'flex',
                    gap: '12px',
                    fontSize: '12px',
                    color: '#666'
                  }}>
                    <span>📄 {fn.file.split('/').pop()}</span>
                    <span>📍 Line {fn.line}</span>
                    <span style={{
                      color: getSeverityColor(fn.severity),
                      fontWeight: 600
                    }}>
                      {getSeverityLabel(fn.severity)}
                    </span>
                    <span>⚙️ Complexity: {fn.complexity}</span>
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setExpandedId(expandedId === fn.id ? null : fn.id);
                  }}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: '#f0f0f0',
                    border: '1px solid #ddd',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    color: '#666'
                  }}
                >
                  {expandedId === fn.id ? '▼' : '▶'}
                </button>
              </div>

              {/* Expanded Code Preview */}
              {expandedId === fn.id && (
                <div style={{
                  padding: '12px',
                  backgroundColor: '#f5f5f5',
                  borderTop: '1px solid #eee',
                  fontFamily: 'monospace',
                  fontSize: '11px',
                  color: '#333',
                  maxHeight: '200px',
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {fn.code}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      {selectedIds.size > 0 && (
        <div style={{
          padding: '12px',
          borderTop: '1px solid #eee',
          backgroundColor: '#f5f5f5',
          textAlign: 'right',
          fontSize: '12px',
          color: '#666'
        }}>
          {selectedIds.size} function{selectedIds.size !== 1 ? 's' : ''} ready for refactoring
        </div>
      )}
    </div>
  );
};

export default FunctionSelector;
