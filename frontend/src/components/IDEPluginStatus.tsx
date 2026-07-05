import React, { useEffect, useState } from 'react';
import { Activity, Wifi, WifiOff, Plus, X } from 'lucide-react';

interface Session {
  session_id: string;
  ide_type: string;
  plugin_version: string;
  is_active: boolean;
  analysis_count: number;
  uptime_seconds: number;
}

interface PluginConfig {
  plugin_id: string;
  ide_type: string;
  enabled: boolean;
  auto_analysis: boolean;
  real_time_feedback: boolean;
  analysis_type: 'quick' | 'comprehensive' | 'incremental';
  debounce_ms: number;
}

interface IDEPluginStatusProps {
  sessions?: Session[];
  onRegisterPlugin?: (ideType: string) => void;
  onCloseSession?: (sessionId: string) => void;
}

const IDEPluginStatus: React.FC<IDEPluginStatusProps> = ({
  sessions = [],
  onRegisterPlugin,
  onCloseSession,
}) => {
  const ideIcons: { [key: string]: string } = {
    vscode: '⚡',
    jetbrains: '🎯',
    sublime: '✨',
    neovim: '📝',
  };

  const formatUptime = (seconds: number): string => {
    if (seconds < 60) return `${Math.floor(seconds)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-800">IDE Plugin Status</h3>
        </div>
        {sessions.length > 0 && (
          <span className="bg-purple-100 text-purple-800 text-xs font-semibold px-3 py-1 rounded-full">
            {sessions.filter(s => s.is_active).length} Active
          </span>
        )}
      </div>

      {sessions.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No IDE plugins connected</p>
          {onRegisterPlugin && (
            <button
              onClick={() => onRegisterPlugin('vscode')}
              className="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition"
            >
              <Plus className="w-4 h-4" />
              Connect IDE
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map(session => (
            <div
              key={session.session_id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
            >
              <div className="flex items-center gap-3 flex-1">
                <span className="text-xl">{ideIcons[session.ide_type] || '📱'}</span>
                <div className="flex-1">
                  <div className="font-medium text-gray-800 capitalize">
                    {session.ide_type}
                  </div>
                  <div className="text-sm text-gray-500">
                    v{session.plugin_version} • {session.analysis_count} analyses
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right text-sm">
                  <div className="text-gray-600">
                    Uptime: {formatUptime(session.uptime_seconds)}
                  </div>
                  <div className="flex items-center gap-1 justify-end mt-1">
                    {session.is_active ? (
                      <>
                        <Wifi className="w-4 h-4 text-green-600" />
                        <span className="text-green-600 text-xs font-semibold">Connected</span>
                      </>
                    ) : (
                      <>
                        <WifiOff className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-400 text-xs">Disconnected</span>
                      </>
                    )}
                  </div>
                </div>

                {onCloseSession && session.is_active && (
                  <button
                    onClick={() => onCloseSession(session.session_id)}
                    className="p-1 hover:bg-gray-200 rounded transition"
                    title="Close session"
                  >
                    <X className="w-4 h-4 text-gray-500" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default IDEPluginStatus;
