/**
 * Performance Optimization Utilities
 * 
 * Provides tools for optimizing application performance,
 * especially for high-concurrency scenarios (500+ users)
 */

import { logger } from './errorHandler'

// Connection Pool Configuration for Database
export interface ConnectionPoolConfig {
  min: number
  max: number
  acquireTimeoutMillis: number
  createTimeoutMillis: number
  idleTimeoutMillis: number
  createRetryIntervalMillis: number
}

export const PRODUCTION_DB_CONFIG: ConnectionPoolConfig = {
  min: 20,
  max: 100,
  acquireTimeoutMillis: 60000,
  createTimeoutMillis: 30000,
  idleTimeoutMillis: 600000,
  createRetryIntervalMillis: 200
}

// WebSocket Scaling Configuration
export interface WebSocketConfig {
  maxConnections: number
  pingTimeout: number
  pingInterval: number
  upgradeTimeout: number
  maxHttpBufferSize: number
  allowEIO3: boolean
  transports: string[]
}

export const PRODUCTION_WS_CONFIG: WebSocketConfig = {
  maxConnections: 1000,
  pingTimeout: 60000,
  pingInterval: 25000,
  upgradeTimeout: 10000,
  maxHttpBufferSize: 1e6, // 1MB
  allowEIO3: true,
  transports: ['websocket', 'polling']
}

// Caching Configuration
export interface CacheConfig {
  examTTL: number        // 30 minutes
  analyticsTTL: number   // 5 minutes
  sessionTTL: number     // 1 hour
  userTTL: number        // 15 minutes
  maxMemoryUsage: number // 512MB
}

export const PRODUCTION_CACHE_CONFIG: CacheConfig = {
  examTTL: 30 * 60 * 1000,      // 30 minutes
  analyticsTTL: 5 * 60 * 1000,   // 5 minutes  
  sessionTTL: 60 * 60 * 1000,    // 1 hour
  userTTL: 15 * 60 * 1000,       // 15 minutes
  maxMemoryUsage: 512 * 1024 * 1024  // 512MB
}

// Memory Cache Implementation
class MemoryCache {
  private cache = new Map<string, { data: any; expiry: number; size: number }>()
  private totalSize = 0
  private readonly maxSize: number

  constructor(maxSize: number = PRODUCTION_CACHE_CONFIG.maxMemoryUsage) {
    this.maxSize = maxSize
  }

  set(key: string, value: any, ttl: number): void {
    const size = this.estimateSize(value)
    const expiry = Date.now() + ttl

    // Remove expired entries and enforce memory limits
    this.cleanup()
    
    if (this.totalSize + size > this.maxSize) {
      this.evictLRU(size)
    }

    // Store the value
    if (this.cache.has(key)) {
      this.totalSize -= this.cache.get(key)!.size
    }

    this.cache.set(key, { data: value, expiry, size })
    this.totalSize += size

    logger.debug(`Cache SET: ${key}, size: ${size}B, total: ${this.totalSize}B`)
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null

    if (Date.now() > entry.expiry) {
      this.delete(key)
      return null
    }

    logger.debug(`Cache HIT: ${key}`)
    return entry.data as T
  }

  delete(key: string): boolean {
    const entry = this.cache.get(key)
    if (entry) {
      this.totalSize -= entry.size
      logger.debug(`Cache DELETE: ${key}, freed: ${entry.size}B`)
    }
    return this.cache.delete(key)
  }

  clear(): void {
    this.cache.clear()
    this.totalSize = 0
    logger.info('Cache cleared')
  }

  getStats(): { 
    entries: number
    totalSize: number
    maxSize: number
    hitRate: number
  } {
    return {
      entries: this.cache.size,
      totalSize: this.totalSize,
      maxSize: this.maxSize,
      hitRate: 0 // Would need request tracking for accurate hit rate
    }
  }

  private cleanup(): void {
    const now = Date.now()
    const expired = Array.from(this.cache.entries())
      .filter(([_, entry]) => now > entry.expiry)
      .map(([key]) => key)

    expired.forEach(key => this.delete(key))

    if (expired.length > 0) {
      logger.debug(`Cleaned up ${expired.length} expired cache entries`)
    }
  }

  private evictLRU(requiredSize: number): void {
    // Simple LRU eviction - in production you'd want a more sophisticated algorithm
    const entries = Array.from(this.cache.entries())
    let freedSize = 0

    for (const [key, entry] of entries) {
      this.delete(key)
      freedSize += entry.size
      
      if (freedSize >= requiredSize) {
        break
      }
    }

    logger.warn(`LRU eviction freed ${freedSize}B to accommodate new entry`)
  }

  private estimateSize(obj: any): number {
    const str = JSON.stringify(obj)
    return str.length * 2 // Rough estimate: 2 bytes per character
  }
}

// Global cache instance
export const cache = new MemoryCache()

// Database Query Optimization
class QueryOptimizer {
  static async batchQueries<T>(
    queries: (() => Promise<T>)[],
    batchSize: number = 10
  ): Promise<T[]> {
    const results: T[] = []
    
    for (let i = 0; i < queries.length; i += batchSize) {
      const batch = queries.slice(i, i + batchSize)
      
      const batchResults = await Promise.allSettled(
        batch.map(query => query())
      )
      
      batchResults.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          results.push(result.value)
        } else {
          logger.error(
            `Batch query failed at index ${i + index}`,
            result.reason,
            undefined,
            'database'
          )
          // Depending on requirements, you might want to throw here
        }
      })
    }
    
    return results
  }

  static memoize<T extends (...args: any[]) => Promise<any>>(
    fn: T,
    ttl: number = 5 * 60 * 1000 // 5 minutes
  ): T {
    return ((...args: any[]) => {
      const cacheKey = `memoize:${fn.name}:${JSON.stringify(args)}`
      
      let result = cache.get(cacheKey)
      if (result) {
        return Promise.resolve(result)
      }

      return fn(...args).then(data => {
        cache.set(cacheKey, data, ttl)
        return data
      })
    }) as T
  }
}

// Connection Pooling Helper
class ConnectionManager {
  private static activeConnections = new Set<string>()
  private static connectionCounts = new Map<string, number>()

  static trackConnection(sessionId: string, userId: string): void {
    const connectionId = `${sessionId}:${userId}`
    
    if (!this.activeConnections.has(connectionId)) {
      this.activeConnections.add(connectionId)
      
      const count = this.connectionCounts.get(sessionId) || 0
      this.connectionCounts.set(sessionId, count + 1)
      
      logger.info(`Connection tracked: ${connectionId}, session total: ${count + 1}`)
    }
  }

  static releaseConnection(sessionId: string, userId: string): void {
    const connectionId = `${sessionId}:${userId}`
    
    if (this.activeConnections.has(connectionId)) {
      this.activeConnections.delete(connectionId)
      
      const count = this.connectionCounts.get(sessionId) || 0
      const newCount = Math.max(0, count - 1)
      
      if (newCount === 0) {
        this.connectionCounts.delete(sessionId)
      } else {
        this.connectionCounts.set(sessionId, newCount)
      }
      
      logger.info(`Connection released: ${connectionId}, session total: ${newCount}`)
    }
  }

  static getConnectionStats(): {
    totalConnections: number
    sessionCounts: Record<string, number>
    activeSessions: number
  } {
    return {
      totalConnections: this.activeConnections.size,
      sessionCounts: Object.fromEntries(this.connectionCounts),
      activeSessions: this.connectionCounts.size
    }
  }

  static isSessionOverloaded(sessionId: string, maxConnections: number = 100): boolean {
    const count = this.connectionCounts.get(sessionId) || 0
    return count >= maxConnections
  }
}

// Rate Limiting for High Load
class AdvancedRateLimiter {
  private static buckets = new Map<string, {
    tokens: number
    lastRefill: number
    capacity: number
    refillRate: number
  }>()

  static checkLimit(
    identifier: string,
    capacity: number = 100,
    refillRate: number = 1, // tokens per second
    cost: number = 1
  ): boolean {
    const now = Date.now()
    let bucket = this.buckets.get(identifier)

    if (!bucket) {
      bucket = {
        tokens: capacity,
        lastRefill: now,
        capacity,
        refillRate
      }
      this.buckets.set(identifier, bucket)
    }

    // Refill tokens based on time elapsed
    const elapsed = (now - bucket.lastRefill) / 1000
    const tokensToAdd = elapsed * bucket.refillRate
    
    bucket.tokens = Math.min(bucket.capacity, bucket.tokens + tokensToAdd)
    bucket.lastRefill = now

    // Check if we have enough tokens
    if (bucket.tokens >= cost) {
      bucket.tokens -= cost
      return true
    }

    logger.warn(
      `Rate limit exceeded for ${identifier}`,
      { 
        additionalData: {
          identifier, 
          tokensAvailable: bucket.tokens, 
          tokensRequired: cost,
          capacity: bucket.capacity,
          refillRate: bucket.refillRate
        }
      }
    )

    return false
  }

  static clearBucket(identifier: string): void {
    this.buckets.delete(identifier)
  }

  static getBucketStats(identifier: string) {
    return this.buckets.get(identifier)
  }
}

// Load Balancing Utilities
class LoadBalancer {
  private static serverHealthScores = new Map<string, number>()
  private static roundRobinIndex = 0

  static updateServerHealth(serverId: string, score: number): void {
    this.serverHealthScores.set(serverId, score)
    logger.debug(`Server health updated: ${serverId} = ${score}`)
  }

  static getOptimalServer(servers: string[]): string | null {
    const healthyServers = servers.filter(server => {
      const health = this.serverHealthScores.get(server) || 1.0
      return health > 0.5 // Only use servers with >50% health
    })

    if (healthyServers.length === 0) {
      logger.error('No healthy servers available', undefined, { additionalData: { servers } })
      return null
    }

    // Weighted round-robin based on health scores
    let bestServer = healthyServers[0]
    let bestScore = this.serverHealthScores.get(bestServer) || 0

    for (const server of healthyServers) {
      const score = this.serverHealthScores.get(server) || 0
      if (score > bestScore) {
        bestServer = server
        bestScore = score
      }
    }

    return bestServer
  }
}

// Resource Monitoring
class ResourceMonitor {
  static getMemoryUsage(): {
    used: number
    total: number
    percentage: number
  } {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      const usage = process.memoryUsage()
      return {
        used: usage.heapUsed,
        total: usage.heapTotal,
        percentage: (usage.heapUsed / usage.heapTotal) * 100
      }
    }
    
    return { used: 0, total: 0, percentage: 0 }
  }

  static logResourceStats(): void {
    const memory = this.getMemoryUsage()
    const cacheStats = cache.getStats()
    const connections = ConnectionManager.getConnectionStats()

    logger.info('Resource Statistics', {
      additionalData: {
      memory: {
        usedMB: Math.round(memory.used / 1024 / 1024),
        totalMB: Math.round(memory.total / 1024 / 1024),
        percentage: Math.round(memory.percentage)
      },
      cache: {
        entries: cacheStats.entries,
        sizeMB: Math.round(cacheStats.totalSize / 1024 / 1024),
        maxSizeMB: Math.round(cacheStats.maxSize / 1024 / 1024)
      },
      connections: {
        total: connections.totalConnections,
        sessions: connections.activeSessions
      }
    }
    })
  }

  static startResourceMonitoring(intervalMs: number = 30000): NodeJS.Timeout {
    return setInterval(() => {
      this.logResourceStats()
      
      // Alert on high memory usage
      const memory = this.getMemoryUsage()
      if (memory.percentage > 85) {
        logger.warn(
          'High memory usage detected',
          { additionalData: { memoryPercentage: memory.percentage } }
        )
      }
    }, intervalMs)
  }
}

// Export optimized configurations
export {
  MemoryCache,
  QueryOptimizer,
  ConnectionManager,
  AdvancedRateLimiter,
  LoadBalancer,
  ResourceMonitor
}