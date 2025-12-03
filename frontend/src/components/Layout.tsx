import { useState, type ReactNode } from 'react'
import { Chip } from '@/components/ui'
import { Play, LayoutDashboard, Flame, Users, Monitor, History, LogOut, Sun, Moon, Filter, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/AuthContext'
import { useTheme } from '@/contexts/ThemeContext'
import { useFilter } from '@/contexts/FilterContext'
import { FilterPanel } from '@/components/FilterPanel'
import { NameMappingPanel } from '@/components/NameMappingPanel'

interface LayoutProps {
  children: (props: { activeTab: string; refreshKey: number }) => ReactNode
}
const TABS = [
  { id: 'overview', label: '概览', icon: LayoutDashboard },
  { id: 'content', label: '热门', icon: Flame },
  { id: 'users', label: '用户', icon: Users },
  { id: 'devices', label: '设备', icon: Monitor },
  { id: 'history', label: '历史', icon: History },
]

const TIME_RANGES = [
  { days: 7, label: '7天' },
  { days: 30, label: '30天' },
  { days: 90, label: '90天' },
  { days: 365, label: '全年' },
]

export function Layout({ children }: LayoutProps) {
  const { username, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const { filters, options, setDays, hasActiveFilters, activeFilterCount } = useFilter()
  const [activeTab, setActiveTab] = useState('overview')
  const [refreshKey] = useState(0)
  const [filterPanelOpen, setFilterPanelOpen] = useState(false)
  const [settingsPanelOpen, setSettingsPanelOpen] = useState(false)

  return (
    <div className="min-h-screen pb-24">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-[var(--color-header-bg)] border-b border-[var(--color-border-light)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 flex-shrink-0">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center flex-shrink-0">
                <Play className="w-5 h-5" fill="currentColor" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold">Emby Stats</h1>
                <p className="text-xs text-zinc-500">播放统计分析</p>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-wrap justify-end">
              {TIME_RANGES.map((range) => (
                <Chip
                  key={range.days}
                  active={!filters.useDateRange && filters.days === range.days}
                  onClick={() => setDays(range.days)}
                >
                  {range.label}
                </Chip>
              ))}
              {/* 筛选按钮 */}
              <button
                onClick={() => setFilterPanelOpen(true)}
                className={cn(
                  'relative p-2 rounded-lg transition-colors',
                  hasActiveFilters
                    ? 'text-primary bg-primary/10 hover:bg-primary/20'
                    : 'text-[var(--color-text-muted)] hover:text-foreground hover:bg-[var(--color-hover-overlay)]'
                )}
                title="筛选"
              >
                <Filter className="w-4 h-4" />
                {activeFilterCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 text-[10px] bg-primary text-white rounded-full flex items-center justify-center">
                    {activeFilterCount}
                  </span>
                )}
              </button>
              <div className="ml-2 pl-2 border-l border-[var(--color-border)] flex items-center gap-2">
                <span className="text-xs text-[var(--color-text-muted)] hidden sm:inline">{username}</span>
                <button
                  onClick={() => setSettingsPanelOpen(true)}
                  className="p-2 rounded-lg text-[var(--color-text-muted)] hover:text-foreground hover:bg-[var(--color-hover-overlay)] transition-colors"
                  title="设置"
                >
                  <Settings className="w-4 h-4" />
                </button>
                <button
                  onClick={toggleTheme}
                  className="p-2 rounded-lg text-[var(--color-text-muted)] hover:text-foreground hover:bg-[var(--color-hover-overlay)] transition-colors"
                  title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
                >
                  {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                </button>
                <button
                  onClick={logout}
                  className="p-2 rounded-lg text-[var(--color-text-muted)] hover:text-foreground hover:bg-[var(--color-hover-overlay)] transition-colors"
                  title="登出"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {children({ activeTab, refreshKey })}
      </main>

      {/* Filter Panel */}
      <FilterPanel isOpen={filterPanelOpen} onClose={() => setFilterPanelOpen(false)} />

      {/* Name Mapping Settings Panel */}
      <NameMappingPanel
        isOpen={settingsPanelOpen}
        onClose={() => setSettingsPanelOpen(false)}
        availableClients={options?.clients || []}
        availableDevices={options?.devices || []}
      />

      {/* Bottom Tab Navigation - Floating */}
      <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
        <div className="flex items-center gap-1 px-2 py-2 bg-[var(--color-nav-bg)] backdrop-blur-2xl rounded-2xl border border-[var(--color-border)] shadow-[0_8px_32px_rgba(0,0,0,0.2)]">
          {TABS.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-all duration-200',
                  isActive
                    ? 'bg-primary/20 text-primary'
                    : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-muted)] hover:bg-[var(--color-hover-overlay)]'
                )}
              >
                <Icon className={cn('w-5 h-5 transition-transform', isActive && 'scale-110')} />
                <span className="text-[10px] font-medium">{tab.label}</span>
              </button>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
