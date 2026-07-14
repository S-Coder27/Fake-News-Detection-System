export default function StatCard({ title, value, note }) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="text-slate-300 text-sm">{title}</div>
      <div className="text-3xl font-bold mt-2">{value}</div>
      <div className="text-xs text-slate-400 mt-1">{note}</div>
    </div>
  )
}