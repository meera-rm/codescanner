/**
 * CAQI Constants - shared across frontend components
 */

export const CAQI_MAX = 500;
export const DIMENSION_MAX = 100;

export const GRADE_THRESHOLDS = {
  'A+': 450,
  'A': 400,
  'B+': 350,
  'B': 300,
  'C+': 250,
  'C': 200,
  'D+': 150,
  'D': 100,
  'F': 0,
} as const;

export const COLOR_SCALE = {
  excellent: '#22c55e',  // Green - 80%+
  good: '#eab308',       // Yellow - 60-79%
  fair: '#f97316',       // Orange - 40-59%
  poor: '#ef4444',       // Red - < 40%
} as const;

export const DIMENSIONS = [
  'security',
  'complexity',
  'documentation',
  'testing',
  'dependencies',
  'maintainability',
] as const;

export const DIMENSION_LABELS: Record<typeof DIMENSIONS[number], string> = {
  security: 'Security',
  complexity: 'Complexity',
  documentation: 'Documentation',
  testing: 'Testing',
  dependencies: 'Dependencies',
  maintainability: 'Maintainability',
};

export const SEVERITY_COLORS: Record<'low' | 'medium' | 'high' | 'critical', string> = {
  low: '#22c55e',      // Green
  medium: '#eab308',   // Yellow
  high: '#f97316',     // Orange
  critical: '#ef4444', // Red
};

export const CONTRIBUTION_THRESHOLDS = {
  highPositive: 5,
  minorPositive: 0,
  minorNegative: -5,
  highNegative: -5,
} as const;

/**
 * Validate CAQI score is in valid range
 */
export function validateCaqiScore(score: number): boolean {
  return typeof score === 'number' && score >= 0 && score <= CAQI_MAX;
}

/**
 * Validate dimension score is in valid range
 */
export function validateDimensionScore(score: number): boolean {
  return typeof score === 'number' && score >= 0 && score <= DIMENSION_MAX;
}

/**
 * Get grade from CAQI score
 */
export function getGrade(score: number): string {
  if (!validateCaqiScore(score)) return 'F';

  for (const [grade, threshold] of Object.entries(GRADE_THRESHOLDS)) {
    if (score >= threshold) return grade;
  }
  return 'F';
}

/**
 * Get color from CAQI score
 */
export function getScoreColor(score: number, max: number = CAQI_MAX): string {
  const percentage = (score / max) * 100;
  if (percentage >= 80) return COLOR_SCALE.excellent;
  if (percentage >= 60) return COLOR_SCALE.good;
  if (percentage >= 40) return COLOR_SCALE.fair;
  return COLOR_SCALE.poor;
}

/**
 * Format date for display
 */
export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Invalid date';
    }
    return date.toLocaleDateString();
  } catch {
    return 'Invalid date';
  }
}
