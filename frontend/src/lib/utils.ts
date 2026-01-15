import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }
  return `${m}:${String(s).padStart(2, '0')}`
}

export function formatNumber(num: number): string {
  return num.toLocaleString()
}

/**
 * Parse a datetime string from backend as local time
 * Backend returns strings like "2026-01-15 11:25:56" which are already in local timezone
 * We need to parse them as local time, not UTC
 */
function parseLocalDateTime(dateStr: string): Date {
  // Replace space with 'T' to make it ISO-like, but without timezone suffix
  // This makes the browser parse it as local time
  const isoLike = dateStr.replace(' ', 'T')
  return new Date(isoLike)
}

export function formatDate(dateStr: string): string {
  const date = parseLocalDateTime(dateStr)
  return date.toLocaleDateString()
}

export function formatTime(dateStr: string): string {
  const date = parseLocalDateTime(dateStr)
  return date.toLocaleTimeString().slice(0, 5)
}

export function formatDateTime(dateStr: string): string {
  const date = parseLocalDateTime(dateStr)
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString().slice(0, 5)}`
}

export function formatHours(hours: number): string {
  if (hours < 1) {
    return `${Math.round(hours * 60)} 分钟`
  }
  const h = Math.floor(hours)
  const m = Math.round((hours - h) * 60)
  if (m === 0) {
    return `${h} 小时`
  }
  return `${h} 小时 ${m} 分钟`
}
