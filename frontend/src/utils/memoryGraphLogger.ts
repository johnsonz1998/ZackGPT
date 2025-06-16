/**
 * Memory Graph Logging Utilities
 * Provides structured logging for MemoryGraph component events and performance
 */

export interface MemoryGraphLogEntry {
  timestamp: string;
  component: string;
  event: string;
  data?: any;
  performance?: {
    duration?: number;
    nodeCount?: number;
    linkCount?: number;
    renderTime?: number;
    operation?: string;
    [key: string]: any;
  };
  user?: {
    userAgent: string;
    url: string;
    viewport: {
      width: number;
      height: number;
    };
  };
}

export class MemoryGraphLogger {
  private static instance: MemoryGraphLogger;
  private logs: MemoryGraphLogEntry[] = [];
  private readonly maxLogs = 100;
  private readonly storageKey = 'memoryGraphLogs';
  
  private constructor() {
    // Load existing logs from sessionStorage
    this.loadLogsFromStorage();
  }
  
  public static getInstance(): MemoryGraphLogger {
    if (!MemoryGraphLogger.instance) {
      MemoryGraphLogger.instance = new MemoryGraphLogger();
    }
    return MemoryGraphLogger.instance;
  }
  
  /**
   * Log a MemoryGraph event with structured data
   */
  public logEvent(event: string, data?: any, performance?: any): void {
    const logEntry: MemoryGraphLogEntry = {
      timestamp: new Date().toISOString(),
      component: 'MemoryGraph',
      event,
      data: this.sanitizeData(data),
      performance,
      user: {
        userAgent: navigator.userAgent,
        url: window.location.href,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      }
    };
    
    // Add to logs array
    this.logs.push(logEntry);
    
    // Keep only last maxLogs entries
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }
    
    // Console logging with emoji prefix
    const emoji = this.getEventEmoji(event);
    console.log(`${emoji} [MemoryGraph] ${event}:`, logEntry);
    
    // Store in sessionStorage
    this.saveLogsToStorage();
    
    // Send to backend if available (fire and forget)
    this.sendToBackend(logEntry);
  }
  
  /**
   * Log performance metrics for MemoryGraph operations
   */
  public logPerformance(operation: string, startTime: number, additionalData?: any): void {
    const duration = performance.now() - startTime;
    this.logEvent(`performance_${operation}`, additionalData, {
      duration,
      operation,
      ...additionalData
    });
  }
  
  /**
   * Log user interactions with the MemoryGraph
   */
  public logInteraction(action: string, target?: any, context?: any): void {
    this.logEvent(`interaction_${action}`, {
      target: this.sanitizeData(target),
      context: this.sanitizeData(context)
    });
  }
  
  /**
   * Log filtering and search operations
   */
  public logFiltering(filterType: string, params: any, results: any): void {
    this.logEvent(`filter_${filterType}`, {
      params: this.sanitizeData(params),
      results: {
        totalBefore: results.totalBefore,
        totalAfter: results.totalAfter,
        filteredCount: results.filteredCount
      }
    });
  }
  
  /**
   * Log visualization rendering events
   */
  public logVisualization(renderType: string, metrics: any): void {
    this.logEvent(`viz_${renderType}`, null, {
      ...metrics,
      renderType
    });
  }
  
  /**
   * Get all logs for analysis
   */
  public getLogs(): MemoryGraphLogEntry[] {
    return [...this.logs];
  }
  
  /**
   * Clear all logs
   */
  public clearLogs(): void {
    this.logs = [];
    this.saveLogsToStorage();
    console.log('🧹 [MemoryGraph] Logs cleared');
  }
  
  /**
   * Export logs as JSON for analysis
   */
  public exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }
  
  /**
   * Get performance summary
   */
  public getPerformanceSummary(): any {
    const perfLogs = this.logs.filter(log => log.event.startsWith('performance_'));
    const operations = perfLogs.reduce((acc, log) => {
      const op = log.performance?.operation || 'unknown';
      if (!acc[op]) {
        acc[op] = { count: 0, totalDuration: 0, avgDuration: 0 };
      }
      acc[op].count++;
      acc[op].totalDuration += log.performance?.duration || 0;
      acc[op].avgDuration = acc[op].totalDuration / acc[op].count;
      return acc;
    }, {} as any);
    
    return {
      totalOperations: perfLogs.length,
      operations,
      timeRange: {
        first: perfLogs[0]?.timestamp,
        last: perfLogs[perfLogs.length - 1]?.timestamp
      }
    };
  }
  
  private sanitizeData(data: any): any {
    if (!data) return data;
    
    // Remove large objects that might cause performance issues
    if (typeof data === 'object') {
      const sanitized = { ...data };
      
      // Remove DOM nodes
      Object.keys(sanitized).forEach(key => {
        if (sanitized[key] instanceof Node) {
          sanitized[key] = '[DOM Node]';
        }
        // Truncate long strings
        if (typeof sanitized[key] === 'string' && sanitized[key].length > 200) {
          sanitized[key] = sanitized[key].substring(0, 200) + '...';
        }
      });
      
      return sanitized;
    }
    
    return data;
  }
  
  private getEventEmoji(event: string): string {
    if (event.startsWith('performance_')) return '⚡';
    if (event.startsWith('interaction_')) return '👆';
    if (event.startsWith('filter_')) return '🔍';
    if (event.startsWith('viz_')) return '🎨';
    if (event.includes('error')) return '❌';
    if (event.includes('success')) return '✅';
    if (event.includes('warning')) return '⚠️';
    return '🧠';
  }
  
  private loadLogsFromStorage(): void {
    try {
      const stored = sessionStorage.getItem(this.storageKey);
      if (stored) {
        this.logs = JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load MemoryGraph logs from storage:', error);
    }
  }
  
  private saveLogsToStorage(): void {
    try {
      sessionStorage.setItem(this.storageKey, JSON.stringify(this.logs));
    } catch (error) {
      console.warn('Failed to save MemoryGraph logs to storage:', error);
    }
  }
  
  private async sendToBackend(logEntry: MemoryGraphLogEntry): Promise<void> {
    try {
      // Only send in development or when explicitly enabled
      if (process.env.NODE_ENV === 'development' || process.env.REACT_APP_ENABLE_LOGGING === 'true') {
        await fetch('/api/logs/frontend', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(logEntry)
        });
      }
    } catch (error) {
      // Silently fail - logging shouldn't break the app
      console.debug('Failed to send log to backend:', error);
    }
  }
}

// Export singleton instance
export const memoryGraphLogger = MemoryGraphLogger.getInstance();

// Export convenience functions
export const logMemoryGraphEvent = (event: string, data?: any, performance?: any) => {
  memoryGraphLogger.logEvent(event, data, performance);
};

export const logMemoryGraphPerformance = (operation: string, startTime: number, additionalData?: any) => {
  memoryGraphLogger.logPerformance(operation, startTime, additionalData);
};

export const logMemoryGraphInteraction = (action: string, target?: any, context?: any) => {
  memoryGraphLogger.logInteraction(action, target, context);
};

export const logMemoryGraphFiltering = (filterType: string, params: any, results: any) => {
  memoryGraphLogger.logFiltering(filterType, params, results);
};

export const logMemoryGraphVisualization = (renderType: string, metrics: any) => {
  memoryGraphLogger.logVisualization(renderType, metrics);
}; 