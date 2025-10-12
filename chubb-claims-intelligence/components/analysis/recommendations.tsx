"use client"

import * as React from "react"
import { Badge } from "@/components/ui/badge"

type Result = {
  recommendedActions: string[]
}

export default function Recommendations() {
  const [actions, setActions] = React.useState<string[] | null>(null)

  React.useEffect(() => {
    const onUpdate = (e: Event) => {
      const ce = e as CustomEvent<Result>
      setActions(ce.detail?.recommendedActions ?? [])
    }
    window.addEventListener("analysis:updated", onUpdate as any)
    return () => window.removeEventListener("analysis:updated", onUpdate as any)
  }, [])

  if (!actions || actions.length === 0) {
    return <p className="text-sm text-muted-foreground">Run an analysis to see recommended next steps.</p>
  }

  return (
    <ul className="grid list-disc gap-2 pl-4">
      {actions.map((a, i) => (
        <li key={i} className="text-sm leading-relaxed">
          <Badge variant="outline" className="mr-2 align-middle">
            Action
          </Badge>
          <span className="align-middle">{a}</span>
        </li>
      ))}
    </ul>
  )
}
