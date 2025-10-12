"use client"

import { useEffect, useState } from "react"
import { ResponsiveContainer, BarChart, XAxis, YAxis, Tooltip, Bar, CartesianGrid } from "recharts"

type Result = {
  riskScore: number
  fraudProbability: number
}

export default function RiskFraudChart() {
  const [data, setData] = useState<{ name: string; value: number }[]>([
    { name: "Risk", value: 0 },
    { name: "Fraud", value: 0 },
  ])

  useEffect(() => {
    function onUpdate(e: Event) {
      const ce = e as CustomEvent<Result>
      setData([
        { name: "Risk", value: ce.detail.riskScore ?? 0 },
        { name: "Fraud", value: ce.detail.fraudProbability ?? 0 },
      ])
    }
    window.addEventListener("analysis:updated", onUpdate as any)
    return () => window.removeEventListener("analysis:updated", onUpdate as any)
  }, [])

  return (
    <div className="h-60 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="oklch(var(--color-border))" />
          <XAxis dataKey="name" tickLine={false} axisLine={false} />
          <YAxis domain={[0, 100]} tickLine={false} axisLine={false} />
          <Tooltip
            cursor={{ fill: "oklch(var(--color-muted))" }}
            contentStyle={{ background: "oklch(var(--color-card))", border: "1px solid oklch(var(--color-border))" }}
          />
          <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="oklch(var(--color-primary))" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
