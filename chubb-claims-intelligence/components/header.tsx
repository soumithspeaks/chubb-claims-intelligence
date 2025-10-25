"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

export default function Header() {
  return (
    <header className="border-b bg-card">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-4">
        <Link href="/" className="flex items-center gap-3" aria-label="EcoSmart Waste Management Home">
          <div className="rounded-md bg-green-600 px-2.5 py-1 text-xs font-semibold leading-none text-white">
            ♻️ EcoSmart
          </div>
          <div className="text-sm text-muted-foreground">Waste Management Platform</div>
        </Link>
        <nav className="hidden items-center gap-2 md:flex">
          <Link href="/user">
            <Button variant="ghost" className="text-sm">
              User App
            </Button>
          </Link>
          <Link href="/agent">
            <Button variant="ghost" className="text-sm">
              Agent App
            </Button>
          </Link>
          <Link href="/admin">
            <Button variant="ghost" className="text-sm">
              Admin
            </Button>
          </Link>
          <Separator orientation="vertical" className="mx-2 h-5" />
          <Link href="/docs" target="_blank">
            <Button className="text-sm bg-green-600 hover:bg-green-700">API Docs</Button>
          </Link>
        </nav>
      </div>
    </header>
  )
}
