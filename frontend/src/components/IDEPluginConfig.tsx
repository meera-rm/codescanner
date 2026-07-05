import React, { useState } from 'react';
import { Settings, Save, X } from 'lucide-react';

interface IDEPluginConfigProps {
  sessionId?: string;
  onSave?: (config: any) => void;
  onClose?: () => void;
  isOpen?: boolean;
}

const IDEPluginConfig: React.FC<IDEPluginConfigProps> = ({
  sessionId,
  onSave,
  onClose,
  isOpen = true,
}) => {
  const [config, setConfig] = useState({
    auto_analysis: true,
    real_time_feedback: true,
    analysis_type: 'quick',
    debounce_ms: 500,
    max_file_size_kb: 500,
  });

  const handleChange = (field: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = () => {
    if (onSave) {
      onSave(config);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-purple-600" />
            <h2 className="text-lg font-semibold text-gray-800">
              Plugin Configuration
            </h2>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-100 rounded transition"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          )}
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Auto Analysis */}
          <div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={config.auto_analysis}
                onChange={e =>
                  handleChange('auto_analysis', e.target.checked)
                }
                className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
              />
              <div>
                <p className="font-medium text-gray-800">Auto Analysis</p>
                <p className="text-xs text-gray-600 mt-1">
                  Automatically analyze files as you edit
                </p>
              </div>
            </label>
          </div>

          {/* Real-time Feedback */}
          <div className="pt-3 border-t border-gray-200">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={config.real_time_feedback}
                onChange={e =>
                  handleChange('real_time_feedback', e.target.checked)
                }
                className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
              />
              <div>
                <p className="font-medium text-gray-800">Real-time Feedback</p>
                <p className="text-xs text-gray-600 mt-1">
                  Show inline suggestions and issues
                </p>
              </div>
            </label>
          </div>

          {/* Analysis Type */}
          <div className="pt-3 border-t border-gray-200">
            <label className="block mb-2">
              <p className="font-medium text-gray-800 mb-2">Analysis Type</p>
              <select
                value={config.analysis_type}
                onChange={e =>
                  handleChange('analysis_type', e.target.value)
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="quick">Quick (Fast)</option>
                <option value="comprehensive">
                  Comprehensive (Thorough)
                </option>
                <option value="incremental">Incremental (Changed files)</option>
              </select>
              <p className="text-xs text-gray-600 mt-2">
                Affects analysis depth and speed
              </p>
            </label>
          </div>

          {/* Debounce */}
          <div className="pt-3 border-t border-gray-200">
            <label className="block">
              <p className="font-medium text-gray-800 mb-2">
                Debounce Delay
              </p>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="100"
                  max="2000"
                  step="100"
                  value={config.debounce_ms}
                  onChange={e =>
                    handleChange('debounce_ms', parseInt(e.target.value))
                  }
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-sm font-semibold text-gray-800 min-w-[60px]">
                  {config.debounce_ms}ms
                </span>
              </div>
              <p className="text-xs text-gray-600 mt-2">
                Wait time before triggering analysis
              </p>
            </label>
          </div>

          {/* Max File Size */}
          <div className="pt-3 border-t border-gray-200">
            <label className="block">
              <p className="font-medium text-gray-800 mb-2">
                Max File Size
              </p>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min="100"
                  max="5000"
                  step="100"
                  value={config.max_file_size_kb}
                  onChange={e =>
                    handleChange('max_file_size_kb', parseInt(e.target.value))
                  }
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
                <span className="text-sm text-gray-600">KB</span>
              </div>
              <p className="text-xs text-gray-600 mt-2">
                Skip files larger than this
              </p>
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 p-6 border-t border-gray-200 bg-gray-50 rounded-b-lg">
          {onClose && (
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-800 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium"
            >
              Cancel
            </button>
          )}
          <button
            onClick={handleSave}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-medium"
          >
            <Save className="w-4 h-4" />
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default IDEPluginConfig;
