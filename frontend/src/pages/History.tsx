import { Card, PosterCard, PosterGridSkeleton } from '@/components/ui'
import { useRecent } from '@/hooks/useStats'

export function History() {
  const { data: recentData, loading } = useRecent(48)

  const items = recentData?.recent ?? []

  return (
    <Card className="p-5">
      <h3 className="font-semibold mb-4">最近播放</h3>
      {loading ? (
        <PosterGridSkeleton count={24} />
      ) : items.length === 0 ? (
        <p className="text-center text-default-400 py-8">暂无播放记录</p>
      ) : (
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-4">
          {items.map((item, index) => (
            <PosterCard
              key={`recent-${item.item_name}-${item.time}-${index}`}
              title={item.show_name || item.name || item.item_name}
              posterUrl={item.poster_url}
              backdropUrl={item.backdrop_url}
              itemName={item.item_name}
              username={item.username}
              time={item.time}
              showEpisode
              overview={item.overview}
            />
          ))}
        </div>
      )}
    </Card>
  )
}
