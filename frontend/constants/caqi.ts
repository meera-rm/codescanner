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
  return typeof score === 'number' && !isNaN(score) && score >= 0 && score <= CAQI_MAX;
}

/**
 * Validate dimension score is in valid range
 */
export function validateDimensionScore(score: number): boolean {
  return typeof score === 'number' && !isNaN(score) && score >= 0 && score <= DIMENSION_MAX;
}

/**
 * Validate all dimension scores in an object
 */
export function validateDimensions(dimensions: Record<string, number>): boolean {
  return DIMENSIONS.every(dim => {
    const score = dimensions[dim];
    return validateDimensionScore(score);
  });
}

/**
 * Validate severity level
 */
export function validateSeverity(severity: string): severity is 'low' | 'medium' | 'high' | 'critical' {
  return ['low', 'medium', 'high', 'critical'].includes(severity);
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

/**
 * Validate all configuration on startup
 */
export function validateConfiguration(): void {
  const errors: string[] = [];

  // Validate thresholds
  if (CAQI_MAX <= 0) errors.push('CAQI_MAX must be > 0');
  if (DIMENSION_MAX <= 0) errors.push('DIMENSION_MAX must be > 0');

  // Validate grade thresholds are in order
  const thresholdValues = Object.values(GRADE_THRESHOLDS);
  for (let i = 0; i < thresholdValues.length - 1; i++) {
    if (thresholdValues[i] <= thresholdValues[i + 1]) {
      errors.push('Grade thresholds must be in descending order');
      break;
    }
  }

  // Validate colors are valid hex
  const colorValues = Object.values(COLOR_SCALE);
  const hexRegex = /^#[0-9A-F]{6}$/i;
  for (const color of colorValues) {
    if (!hexRegex.test(color)) {
      errors.push(`Invalid color format: ${color}`);
    }
  }

  // Validate dimensions exist
  for (const dim of DIMENSIONS) {
    if (!DIMENSION_LABELS[dim]) {
      errors.push(`Missing label for dimension: ${dim}`);
    }
  }

  if (errors.length > 0) {
    console.error('Configuration validation errors:', errors);
    throw new Error(`Invalid CAQI configuration:\n${errors.join('\n')}`);
  }
}

// Run validation on import
if (typeof window !== 'undefined') {
  validateConfiguration();
}
