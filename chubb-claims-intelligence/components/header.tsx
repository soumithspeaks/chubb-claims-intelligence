"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

export default function Header() {
  return (
    <header className="border-b bg-card">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-4">
        <Link href="/" className="flex items-center gap-3" aria-label="CHUBB Claims Intelligence Home">
          <div className="rounded-md bg-primary px-2.5 py-1 text-xs font-semibold leading-none text-primary-foreground">
            CHUBB
          </div>
          <div className="text-sm text-muted-foreground">Claims Intelligence</div>
        </Link>
        <nav className="hidden items-center gap-2 md:flex">
          <Button variant="ghost" className="text-sm">
            Overview
          </Button>
          <Button variant="ghost" className="text-sm">
            Models
          </Button>
          <Button variant="ghost" className="text-sm">
            Reports
          </Button>
          <Separator orientation="vertical" className="mx-2 h-5" />
          <Button className="text-sm">New Claim</Button>
        </nav>
      </div>
    </header>
  )
}
