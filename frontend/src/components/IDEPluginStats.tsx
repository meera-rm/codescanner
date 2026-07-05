import React from 'react';
import { BarChart3, TrendingUp, FileCode, AlertCircle } from 'lucide-react';

interface Statistics {
  total_analyses: number;
  total_issues_found: number;
  total_suggestions: number;
  avg_analysis_time_ms: number;
  active_sessions: number;
  total_sessions: number;
  by_language: { [key: string]: number };
}

interface IDEPluginStatsProps {
  stats?: Statistics;
  isLoading?: boolean;
}

const IDEPluginStats: React.FC<IDEPluginStatsProps> = ({
  stats = {
    total_analyses: 0,
    total_issues_found: 0,
    total_suggestions: 0,
    avg_analysis_time_ms: 0,
    active_sessions: 0,
    total_sessions: 0,
    by_language: {},
  },
  isLoading = false,
}) => {
  const languageIcons: { [key: string]: string } = {
    python: '🐍',
    javascript: '📜',
    typescript: '📘',
    go: '🐹',
    java: '☕',
    rust: '🦀',
  };

  const getSortedLanguages = () => {
    return Object.entries(stats.by_language)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5);
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Total Analyses</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">
                {stats.total_analyses}
              </p>
            </div>
            <BarChart3 className="w-8 h-8 text-blue-500 opacity-60" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg shadow-md p-6 border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Issues Found</p>
              <p className="text-3xl font-bold text-red-600 mt-2">
                {stats.total_issues_found}
              </p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-500 opacity-60" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Suggestions</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">
                {stats.total_suggestions}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-yellow-500 opacity-60" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Avg Analysis Time</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {stats.avg_analysis_time_ms.toFixed(0)}ms
              </p>
            </div>
            <FileCode className="w-8 h-8 text-green-500 opacity-60" />
          </div>
        </div>
      </div>

      {/* Sessions and Languages */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Active Sessions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Plugin Sessions
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Active Sessions</span>
              <span className="inline-block bg-green-100 text-green-800 font-semibold px-3 py-1 rounded-full text-sm">
                {stats.active_sessions}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Total Sessions</span>
              <span className="inline-block bg-blue-100 text-blue-800 font-semibold px-3 py-1 rounded-full text-sm">
                {stats.total_sessions}
              </span>
            </div>
            <div className="flex items-center justify-between pt-3 border-t border-gray-200">
              <span className="text-gray-600 text-sm">
                Active Rate
              </span>
              <span className="text-lg font-semibold text-gray-800">
                {stats.total_sessions > 0
                  ? ((stats.active_sessions / stats.total_sessions) * 100).toFixed(1)
                  : '0'}%
              </span>
            </div>
          </div>
        </div>

        {/* Languages Analyzed */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Languages Analyzed
          </h3>
          <div className="space-y-2">
            {Object.keys(stats.by_language).length === 0 ? (
              <p className="text-gray-500 text-sm">No analyses yet</p>
            ) : (
              getSortedLanguages().map(([language, count]) => (
                <div key={language} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">
                      {languageIcons[language] || '📄'}
                    </span>
                    <span className="text-gray-700 capitalize font-medium">
                      {language}
                    </span>
                  </div>
                  <span className="inline-block bg-gray-100 text-gray-800 font-semibold px-3 py-1 rounded text-sm">
                    {count}
                  </span>
                </div>
              ))
            )}
            {Object.keys(stats.by_language).length > 5 && (
              <p className="text-gray-500 text-xs pt-2 border-t border-gray-200">
                +{Object.keys(stats.by_language).length - 5} more languages
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IDEPluginStats;
