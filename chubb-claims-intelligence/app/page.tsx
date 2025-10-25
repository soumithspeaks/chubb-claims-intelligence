import { Suspense } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import Header from "@/components/header"

export default function Page() {
  return (
    <main className="min-h-dvh">
      <Header />
      <section className="mx-auto w-full max-w-7xl px-4 py-8 md:py-10">
        {/* Hero Section */}
        <div className="mb-8 flex flex-col items-start justify-between gap-4 md:mb-12 md:flex-row md:items-end">
          <div>
            <h1 className="text-pretty text-4xl font-bold tracking-tight md:text-5xl">
              Enterprise Waste Management Platform
            </h1>
            <p className="mt-3 text-lg text-muted-foreground">
              AI-powered waste classification, smart agent matching, and incentivized recycling for a sustainable future
            </p>
          </div>
          <div className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white">♻️ EcoSmart</div>
        </div>

        {/* Main Cards Grid */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
          {/* User App Card */}
          <Card className="border-2 hover:border-green-500 transition-colors">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">👤</span>
                User Portal
              </CardTitle>
              <CardDescription>
                Request waste pickups and earn money through recycling
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>📸 AI-powered waste classification</li>
                <li>📍 Real-time pickup tracking</li>
                <li>💰 Instant payment for recyclables</li>
                <li>🌍 Track environmental impact</li>
              </ul>
              <Link href="/user" className="block">
                <Button className="w-full bg-green-600 hover:bg-green-700">
                  Launch User App →
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Agent App Card */}
          <Card className="border-2 hover:border-blue-500 transition-colors">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">🚚</span>
                Agent Portal
              </CardTitle>
              <CardDescription>
                Accept pickup requests and maximize your earnings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>🗺️ Smart route optimization</li>
                <li>📱 Real-time request notifications</li>
                <li>💵 Track daily earnings</li>
                <li>⭐ Build your reputation</li>
              </ul>
              <Link href="/agent" className="block">
                <Button className="w-full bg-blue-600 hover:bg-blue-700">
                  Launch Agent App →
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Admin Dashboard Card */}
          <Card className="border-2 hover:border-purple-500 transition-colors">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">📊</span>
                Admin Dashboard
              </CardTitle>
              <CardDescription>
                Monitor platform operations and analytics
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>📈 Real-time platform metrics</li>
                <li>👥 User & agent management</li>
                <li>💳 Payment reconciliation</li>
                <li>🏭 Recycling unit coordination</li>
              </ul>
              <Link href="/admin" className="block">
                <Button className="w-full bg-purple-600 hover:bg-purple-700">
                  Launch Admin Panel →
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <Separator className="my-8" />

        {/* Features Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-6">Platform Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">🤖 AI Classification</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Deep learning models classify 8+ waste categories with 90%+ accuracy
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-base">🎯 Smart Matching</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Intelligent agent assignment based on location, rating, and availability
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-base">💳 Instant Payments</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Dynamic pricing with automated wallet credits and agent payouts
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-base">🌱 Impact Tracking</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Real-time CO₂ reduction, trees saved, and environmental metrics
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Waste Categories Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-6">Supported Waste Categories</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
            {[
              { name: "Plastic", icon: "♻️", color: "bg-orange-100 text-orange-700" },
              { name: "Paper", icon: "📄", color: "bg-amber-100 text-amber-700" },
              { name: "Metal", icon: "🔩", color: "bg-slate-100 text-slate-700" },
              { name: "Glass", icon: "🍾", color: "bg-cyan-100 text-cyan-700" },
              { name: "E-waste", icon: "💻", color: "bg-red-100 text-red-700" },
              { name: "Organic", icon: "🌱", color: "bg-green-100 text-green-700" },
              { name: "Hazardous", icon: "⚠️", color: "bg-yellow-100 text-yellow-700" },
              { name: "Textiles", icon: "👕", color: "bg-purple-100 text-purple-700" }
            ].map((category) => (
              <div 
                key={category.name}
                className={`${category.color} rounded-lg p-4 text-center font-medium`}
              >
                <div className="text-2xl mb-1">{category.icon}</div>
                <div className="text-xs">{category.name}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="text-3xl font-bold text-green-600">10k+</div>
              <div className="text-sm text-muted-foreground mt-1">Active Users</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-3xl font-bold text-blue-600">500+</div>
              <div className="text-sm text-muted-foreground mt-1">Verified Agents</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-3xl font-bold text-purple-600">2.5M kg</div>
              <div className="text-sm text-muted-foreground mt-1">Waste Recycled</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-3xl font-bold text-orange-600">1.2M kg</div>
              <div className="text-sm text-muted-foreground mt-1">CO₂ Saved</div>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  )
}
