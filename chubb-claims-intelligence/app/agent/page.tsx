"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import Header from "@/components/header"

export default function AgentPage() {
  const [isOnline, setIsOnline] = useState(false)
  const [activePickup, setActivePickup] = useState<any>(null)

  const handleAcceptPickup = (pickup: any) => {
    setActivePickup(pickup)
    alert(`Pickup #${pickup.id} accepted! Navigate to location.`)
  }

  const handleCompletePickup = () => {
    alert("Pickup completed! Payment credited.")
    setActivePickup(null)
  }

  return (
    <main className="min-h-dvh">
      <Header />
      <section className="mx-auto w-full max-w-7xl px-4 py-8">
        {/* Page Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Agent Portal</h1>
            <p className="text-muted-foreground">Accept pickup requests and manage your route</p>
          </div>
          <div className="flex items-center gap-4">
            <Label htmlFor="online-toggle" className="text-sm font-medium">
              {isOnline ? "🟢 Online" : "⚫ Offline"}
            </Label>
            <Switch 
              id="online-toggle" 
              checked={isOnline} 
              onCheckedChange={setIsOnline}
            />
          </div>
        </div>

        {/* Agent Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-green-600">$342.50</div>
              <div className="text-xs text-muted-foreground mt-1">Wallet Balance</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-blue-600">$85.20</div>
              <div className="text-xs text-muted-foreground mt-1">Today's Earnings</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-purple-600">157</div>
              <div className="text-xs text-muted-foreground mt-1">Total Pickups</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-orange-600">4.8 ⭐</div>
              <div className="text-xs text-muted-foreground mt-1">Rating</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-red-600">12</div>
              <div className="text-xs text-muted-foreground mt-1">Pickups Today</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Active Pickup */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>🚚 Active Pickup</CardTitle>
              <CardDescription>Current pickup in progress</CardDescription>
            </CardHeader>
            <CardContent>
              {activePickup ? (
                <div className="space-y-4">
                  <div className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                          👤
                        </div>
                        <div>
                          <div className="font-semibold">{activePickup.user}</div>
                          <div className="text-xs text-muted-foreground">{activePickup.phone}</div>
                        </div>
                      </div>
                      <Badge>{activePickup.status}</Badge>
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Waste Type:</span>
                        <span className="font-medium">{activePickup.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Est. Weight:</span>
                        <span className="font-medium">{activePickup.weight}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Your Earnings:</span>
                        <span className="font-semibold text-green-600">{activePickup.earnings}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Distance:</span>
                        <span className="font-medium">{activePickup.distance}</span>
                      </div>
                    </div>

                    <div className="border rounded p-3 bg-muted/50">
                      <div className="text-xs font-medium text-muted-foreground mb-1">📍 Pickup Location</div>
                      <div className="text-sm">{activePickup.address}</div>
                    </div>

                    <div className="border rounded p-3 bg-muted/50">
                      <div className="text-xs font-medium text-muted-foreground mb-1">🔐 OTP Code</div>
                      <div className="text-2xl font-bold tracking-wider">{activePickup.otp}</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <Button variant="outline" className="w-full">
                      📞 Call User
                    </Button>
                    <Button variant="outline" className="w-full">
                      💬 Chat
                    </Button>
                  </div>

                  <Button onClick={handleCompletePickup} className="w-full bg-green-600 hover:bg-green-700" size="lg">
                    ✅ Complete Pickup
                  </Button>
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <div className="text-6xl mb-4">🚫</div>
                  <div>No active pickup</div>
                  <div className="text-sm">Accept a request to start</div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Map & Navigation */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>🗺️ Map & Navigation</CardTitle>
              <CardDescription>Your location and nearby requests</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-square bg-slate-200 rounded-lg flex items-center justify-center text-muted-foreground mb-4">
                <div className="text-center">
                  <div className="text-4xl mb-2">📍</div>
                  <div>Map View</div>
                  <div className="text-sm">(Google Maps Integration)</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" className="w-full">
                  🧭 Navigate
                </Button>
                <Button variant="outline" className="w-full">
                  📍 Update Location
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Available Pickup Requests */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>📋 Available Pickup Requests</CardTitle>
            <CardDescription>Accept requests near your location</CardDescription>
          </CardHeader>
          <CardContent>
            {isOnline ? (
              <div className="space-y-4">
                {[
                  { 
                    id: 1, 
                    user: "John Doe", 
                    phone: "+1 234 567 8900",
                    type: "Plastic - PET", 
                    weight: "3.5 kg", 
                    earnings: "$1.40",
                    distance: "2.3 km",
                    address: "123 Main St, Downtown",
                    eta: "8 mins",
                    otp: "753291"
                  },
                  { 
                    id: 2, 
                    user: "Jane Smith",
                    phone: "+1 234 567 8901", 
                    type: "Paper - Cardboard", 
                    weight: "7.0 kg", 
                    earnings: "$2.10",
                    distance: "3.8 km",
                    address: "456 Oak Ave, Uptown",
                    eta: "12 mins",
                    otp: "842156"
                  },
                  { 
                    id: 3, 
                    user: "Bob Wilson",
                    phone: "+1 234 567 8902", 
                    type: "Metal - Aluminum", 
                    weight: "4.2 kg", 
                    earnings: "$6.72",
                    distance: "1.5 km",
                    address: "789 Pine Rd, Suburbia",
                    eta: "5 mins",
                    otp: "619384"
                  }
                ].map((pickup) => (
                  <div key={pickup.id} className="border rounded-lg p-4 hover:border-green-500 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center text-xl">
                          ♻️
                        </div>
                        <div>
                          <div className="font-semibold">{pickup.user}</div>
                          <div className="text-sm text-muted-foreground">{pickup.type}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-green-600 text-lg">{pickup.earnings}</div>
                        <div className="text-xs text-muted-foreground">{pickup.distance} away</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3 mb-3 text-sm">
                      <div>
                        <div className="text-muted-foreground text-xs">Weight</div>
                        <div className="font-medium">{pickup.weight}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground text-xs">Distance</div>
                        <div className="font-medium">{pickup.distance}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground text-xs">ETA</div>
                        <div className="font-medium">{pickup.eta}</div>
                      </div>
                    </div>

                    <div className="text-sm text-muted-foreground mb-3">
                      📍 {pickup.address}
                    </div>

                    <div className="flex gap-2">
                      <Button 
                        onClick={() => handleAcceptPickup(pickup)}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                        disabled={activePickup !== null}
                      >
                        ✅ Accept Pickup
                      </Button>
                      <Button variant="outline" className="px-4">
                        👁️
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <div className="text-6xl mb-4">⚫</div>
                <div className="font-medium mb-1">You're Offline</div>
                <div className="text-sm">Turn on availability to see pickup requests</div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Today's Completed Pickups */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>✅ Today's Completed Pickups</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { id: 1, type: "Plastic - HDPE", weight: "2.8 kg", earnings: "$1.26", time: "10:30 AM" },
                { id: 2, type: "E-waste - Phones", weight: "0.5 kg", earnings: "$2.50", time: "11:45 AM" },
                { id: 3, type: "Glass - Clear", weight: "5.0 kg", earnings: "$0.75", time: "2:15 PM" }
              ].map((pickup) => (
                <div key={pickup.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-sm">
                      ✅
                    </div>
                    <div>
                      <div className="font-medium text-sm">{pickup.type}</div>
                      <div className="text-xs text-muted-foreground">{pickup.time}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-green-600">{pickup.earnings}</div>
                    <div className="text-xs text-muted-foreground">{pickup.weight}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>
    </main>
  )
}
