"use client"

import * as React from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"

type Result = {
  riskScore: number
  fraudProbability: number
  damageSeverity: "Minor" | "Moderate" | "Severe"
  costEstimate: number
  recommendedActions: string[]
}

export default function ResultCards() {
  const [result, setResult] = React.useState<Result | null>(null)

  React.useEffect(() => {
    function onUpdate(e: Event) {
      const ce = e as CustomEvent<Result>
      setResult(ce.detail)
    }
    window.addEventListener("analysis:updated", onUpdate as any)
    return () => window.removeEventListener("analysis:updated", onUpdate as any)
  }, [])

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <KpiCard
        label="Risk Assessment"
        value={result ? `${result.riskScore}%` : "—"}
        progress={result?.riskScore ?? 0}
        tone="primary"
      />
      <KpiCard
        label="Fraud Probability"
        value={result ? `${result.fraudProbability}%` : "—"}
        progress={result?.fraudProbability ?? 0}
        tone="destructive"
      />
      <KpiCard
        label="Damage Severity"
        value={result?.damageSeverity ?? "—"}
        badgeTone={result ? severityTone(result.damageSeverity) : undefined}
      />
      <KpiCard label="Estimated Cost" value={result ? `$${result.costEstimate.toLocaleString()}` : "—"} />
    </div>
  )
}

function KpiCard({
  label,
  value,
  progress,
  tone,
  badgeTone,
}: {
  label: string
  value: string
  progress?: number
  tone?: "primary" | "destructive"
  badgeTone?: "default" | "secondary" | "destructive" | "outline"
}) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">{label}</span>
          {badgeTone ? (
            <Badge variant={badgeTone}>{value}</Badge>
          ) : (
            <span className="text-lg font-semibold">{value}</span>
          )}
        </div>
        {typeof progress === "number" ? (
          <div className="mt-3">
            <Progress
              value={progress}
              className={tone === "destructive" ? "bg-muted [&>div]:bg-destructive" : "bg-muted [&>div]:bg-primary"}
            />
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}

function severityTone(s: Result["damageSeverity"]): "default" | "secondary" | "destructive" {
  if (s === "Minor") return "secondary"
  if (s === "Moderate") return "default"
  return "destructive"
}
