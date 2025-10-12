"use client"

import type * as React from "react"
import { cn } from "@/lib/utils"

export interface SwitchProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
}

export function Switch({ checked = false, onCheckedChange, className, ...props }: SwitchProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onCheckedChange?.(!checked)}
      className={cn(
        "inline-flex h-6 w-11 items-center rounded-full border transition-colors",
        checked ? "bg-primary border-primary" : "bg-muted",
      )}
      {...props}
    >
      <span
        className={cn(
          "ml-0.5 inline-block h-5 w-5 transform rounded-full bg-card shadow transition-transform",
          checked ? "translate-x-5" : "translate-x-0",
        )}
      />
    </button>
  )
}
