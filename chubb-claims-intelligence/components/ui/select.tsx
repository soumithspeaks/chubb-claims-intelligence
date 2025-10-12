"use client"

import type * as React from "react"
import { cn } from "@/lib/utils"

export function Select({
  value,
  onValueChange,
  children,
}: {
  value?: string
  onValueChange?: (v: string) => void
  children: React.ReactNode
}) {
  return (
    <div data-select value={value} onChange={() => {}}>
      {children}
    </div>
  )
}

export function SelectTrigger({ children, className, ...props }: React.HTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      className={cn("flex w-full items-center justify-between rounded-md border bg-card px-3 py-2 text-sm", className)}
      {...props}
    >
      {children}
    </button>
  )
}

export function SelectValue({ placeholder }: { placeholder?: string }) {
  return <span className="text-muted-foreground">{placeholder}</span>
}

export function SelectContent({ children }: { children: React.ReactNode }) {
  return <div className="mt-2 w-full rounded-md border bg-popover p-1 text-sm">{children}</div>
}

export function SelectItem({
  value,
  children,
}: {
  value: string
  children: React.ReactNode
}) {
  // This minimal select simply uses a button list and dispatches an event so parent can control value
  return (
    <button
      type="button"
      onClick={(e) => {
        const ev = new CustomEvent("select:value", { detail: value })
        window.dispatchEvent(ev)
      }}
      className="block w-full rounded px-2 py-1.5 text-left hover:bg-accent"
    >
      {children}
    </button>
  )
}
