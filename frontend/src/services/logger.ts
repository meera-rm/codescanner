/**
 * Structured logging service for frontend
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
  error?: Error;
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === 'development';
  private logHistory: LogEntry[] = [];
  private maxHistorySize = 100;

  private format(level: LogLevel, message: string, context?: Record<string, any>, error?: Error): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      error,
    };
  }

  private store(entry: LogEntry) {
    this.logHistory.push(entry);
    if (this.logHistory.length > this.maxHistorySize) {
      this.logHistory.shift();
    }
  }

  debug(message: string, context?: Record<string, any>) {
    const entry = this.format('debug', message, context);
    this.store(entry);
    if (this.isDevelopment) {
      console.debug(`[DEBUG] ${message}`, context);
    }
  }

  info(message: string, context?: Record<string, any>) {
    const entry = this.format('info', message, context);
    this.store(entry);
    console.log(`[INFO] ${message}`, context);
  }

  warn(message: string, context?: Record<string, any>) {
    const entry = this.format('warn', message, context);
    this.store(entry);
    console.warn(`[WARN] ${message}`, context);
  }

  error(message: string, error?: Error, context?: Record<string, any>) {
    const entry = this.format('error', message, context, error);
    this.store(entry);
    console.error(`[ERROR] ${message}`, { error, context });
  }

  getHistory(): LogEntry[] {
    return [...this.logHistory];
  }

  clearHistory() {
    this.logHistory = [];
  }

  exportLogs(): string {
    return JSON.stringify(this.logHistory, null, 2);
  }
}

export const logger = new Logger();
export default logger;
