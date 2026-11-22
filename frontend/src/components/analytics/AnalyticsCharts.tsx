import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Card } from '../ui/Card'
import type { EmailActivityDay, EmailCategoryMetric, TaskSummaryMetrics } from '../../types/analytics'

const chartColors = [
  '#F04464', '#E76A83', '#D94868', '#F59E0B', '#B45370',
  '#F4A7B8', '#9D5165', '#626273', '#F7CDD6',
]

function ChartEmpty({ message }: { message: string }) {
  return (
    <div className="flex h-60 items-center justify-center rounded-xl bg-background-secondary px-5 text-center text-sm text-foreground-secondary">
      {message}
    </div>
  )
}

export function EmailCategoryChart({ data }: { data: EmailCategoryMetric[] }) {
  const nonzero = data.filter((item) => item.count > 0)
  return (
    <Card className="p-5 sm:p-6">
      <div className="mb-4">
        <h2 className="text-base font-bold text-foreground">Email categories</h2>
        <p className="mt-1 text-xs text-foreground-secondary">Active, non-deleted emails by stored category.</p>
      </div>
      {nonzero.length === 0 ? <ChartEmpty message="No email category data is available yet." /> : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[minmax(0,1fr)_minmax(150px,0.8fr)] sm:items-center">
          <div role="img" aria-label="Email category distribution">
            <ResponsiveContainer width="100%" height={230}>
              <PieChart>
                <Pie data={nonzero} dataKey="count" nameKey="category" innerRadius={58} outerRadius={88} paddingAngle={2}>
                  {nonzero.map((entry, index) => <Cell key={entry.category} fill={chartColors[index % chartColors.length]} />)}
                </Pie>
                <Tooltip formatter={(value) => [value, 'Emails']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="grid grid-cols-2 gap-x-3 gap-y-2 text-xs sm:grid-cols-1">
            {nonzero.map((item, index) => (
              <li key={item.category} className="flex items-center justify-between gap-2">
                <span className="flex min-w-0 items-center gap-2 text-foreground-secondary">
                  <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: chartColors[index % chartColors.length] }} />
                  <span className="truncate capitalize">{item.category}</span>
                </span>
                <span className="font-semibold text-foreground">{item.count}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  )
}

function formatUtcDay(value: string): string {
  return new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short', timeZone: 'UTC' })
    .format(new Date(`${value}T00:00:00Z`))
}

export function EmailActivityChart({ data }: { data: EmailActivityDay[] }) {
  const hasActivity = data.some((item) => item.count > 0)
  return (
    <Card className="p-5 sm:p-6">
      <div className="mb-4">
        <h2 className="text-base font-bold text-foreground">Email activity</h2>
        <p className="mt-1 text-xs text-foreground-secondary">Daily received emails over the last 30 UTC calendar days.</p>
      </div>
      {!hasActivity ? <ChartEmpty message="No email activity was recorded during this period." /> : (
        <div role="img" aria-label="Daily email activity over the last 30 UTC days">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={data} margin={{ top: 8, right: 10, left: -18, bottom: 2 }}>
              <CartesianGrid stroke="#ECE8EA" strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={formatUtcDay} minTickGap={24} tick={{ fill: '#626273', fontSize: 11 }} />
              <YAxis allowDecimals={false} width={34} tick={{ fill: '#626273', fontSize: 11 }} />
              <Tooltip labelFormatter={(label) => formatUtcDay(String(label))} formatter={(value) => [value, 'Emails']} />
              <Line type="monotone" dataKey="count" stroke="#F04464" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  )
}

export function TaskStatusChart({ data }: { data: TaskSummaryMetrics }) {
  const chartData = [
    { status: 'Pending', count: data.pending, fill: '#F04464' },
    { status: 'In progress', count: data.in_progress, fill: '#D94868' },
    { status: 'Completed', count: data.completed, fill: '#626273' },
    { status: 'Overdue', count: data.overdue, fill: '#B45370' },
  ]
  const hasTasks = data.total > 0
  return (
    <Card className="p-5 sm:p-6">
      <div className="mb-4">
        <h2 className="text-base font-bold text-foreground">Task status</h2>
        <p className="mt-1 text-xs text-foreground-secondary">Current status and overdue tasks.</p>
      </div>
      {!hasTasks ? <ChartEmpty message="No tasks have been created yet." /> : (
        <div role="img" aria-label="Task counts by status and overdue state">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 18, left: 8, bottom: 5 }}>
              <CartesianGrid stroke="#ECE8EA" strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" allowDecimals={false} tick={{ fill: '#626273', fontSize: 11 }} />
              <YAxis type="category" dataKey="status" width={82} tick={{ fill: '#626273', fontSize: 11 }} />
              <Tooltip formatter={(value) => [value, 'Tasks']} />
              <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                {chartData.map((item) => <Cell key={item.status} fill={item.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  )
}
