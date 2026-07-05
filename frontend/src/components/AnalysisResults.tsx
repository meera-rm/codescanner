import React, { useState } from 'react';
import { AlertCircle, AlertTriangle, Info, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react';

interface Issue {
  line: number;
  column: number;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  code: string;
}

interface Suggestion {
  type: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  estimated_improvement: number;
}

interface AnalysisResultsProps {
  filePath?: string;
  language?: string;
  qualityScore?: number;
  issues?: Issue[];
  suggestions?: Suggestion[];
  metrics?: { [key: string]: number };
  estimatedFixTime?: number;
  isLoading?: boolean;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  filePath = 'unknown',
  language = 'unknown',
  qualityScore = 0,
  issues = [],
  suggestions = [],
  metrics = {},
  estimatedFixTime = 0,
  isLoading = false,
}) => {
  const [expandedIssues, setExpandedIssues] = useState(true);
  const [expandedSuggestions, setExpandedSuggestions] = useState(true);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      default:
        return <Info className="w-4 h-4 text-blue-600" />;
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-blue-600 bg-blue-100';
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-3 bg-gray-200 rounded"></div>
          <div className="h-3 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">{filePath}</h3>
            <p className="text-sm text-gray-600 mt-1">Language: {language}</p>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${getQualityColor(qualityScore)}`}>
              {qualityScore.toFixed(0)}
            </div>
            <p className="text-xs text-gray-600 mt-1">Quality Score</p>
          </div>
        </div>

        {estimatedFixTime > 0 && (
          <div className="inline-block bg-orange-100 text-orange-800 text-xs font-semibold px-3 py-1 rounded-full">
            ⏱️ Est. fix time: {estimatedFixTime} min
          </div>
        )}
      </div>

      <div className="p-6">
        {/* Metrics */}
        {Object.keys(metrics).length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {Object.entries(metrics).map(([key, value]) => (
              <div key={key} className="bg-gray-50 p-3 rounded-lg">
                <div className="text-xs text-gray-600 capitalize">
                  {key.replace(/_/g, ' ')}
                </div>
                <div className="text-lg font-semibold text-gray-800 mt-1">
                  {typeof value === 'number' ? value.toFixed(1) : value}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Issues Section */}
        <div className="mb-6">
          <button
            onClick={() => setExpandedIssues(!expandedIssues)}
            className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition"
          >
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="font-semibold text-gray-800">
                Issues ({issues.length})
              </span>
            </div>
            {expandedIssues ? (
              <ChevronUp className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-600" />
            )}
          </button>

          {expandedIssues && (
            <div className="mt-3 space-y-2">
              {issues.length === 0 ? (
                <p className="text-sm text-gray-500 py-3">No issues detected</p>
              ) : (
                issues.map((issue, idx) => (
                  <div
                    key={idx}
                    className={`p-3 border rounded-lg ${getSeverityBg(issue.severity)}`}
                  >
                    <div className="flex gap-2">
                      {getSeverityIcon(issue.severity)}
                      <div className="flex-1">
                        <div className="font-medium text-sm text-gray-800">
                          {issue.message}
                        </div>
                        <div className="text-xs text-gray-600 mt-1">
                          Line {issue.line}:{issue.column} • {issue.code}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Suggestions Section */}
        <div>
          <button
            onClick={() => setExpandedSuggestions(!expandedSuggestions)}
            className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition"
          >
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-600" />
              <span className="font-semibold text-gray-800">
                Suggestions ({suggestions.length})
              </span>
            </div>
            {expandedSuggestions ? (
              <ChevronUp className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-600" />
            )}
          </button>

          {expandedSuggestions && (
            <div className="mt-3 space-y-2">
              {suggestions.length === 0 ? (
                <p className="text-sm text-gray-500 py-3">No suggestions</p>
              ) : (
                suggestions.map((suggestion, idx) => (
                  <div key={idx} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-start justify-between mb-1">
                      <div className="font-medium text-sm text-gray-800">
                        {suggestion.title}
                      </div>
                      <span className={`text-xs font-semibold px-2 py-1 rounded ${getPriorityColor(suggestion.priority)}`}>
                        {suggestion.priority.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2">
                      {suggestion.description}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <div className="text-xs text-gray-600">
                        Estimated improvement:
                      </div>
                      <div className="text-xs font-semibold text-green-600">
                        +{(suggestion.estimated_improvement * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalysisResults;
