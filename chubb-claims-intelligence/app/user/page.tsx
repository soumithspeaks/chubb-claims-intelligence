"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import Header from "@/components/header"

export default function UserPage() {
  const [selectedImages, setSelectedImages] = useState<string[]>([])
  const [classificationResult, setClassificationResult] = useState<any>(null)
  const [isClassifying, setIsClassifying] = useState(false)

  // Cleanup object URLs on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      selectedImages.forEach(url => {
        if (url.startsWith('blob:')) {
          URL.revokeObjectURL(url)
        }
      })
    }
  }, [selectedImages])

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      // Create object URLs for uploaded files (these are safe blob: URLs)
      const imageUrls = Array.from(files)
        .filter(file => file.type.startsWith('image/')) // Only accept image files
        .map(file => URL.createObjectURL(file))
        .slice(0, 5) // Max 5 images
      setSelectedImages(imageUrls)
    }
  }

  const handleClassify = async () => {
    setIsClassifying(true)
    // Simulate API call
    setTimeout(() => {
      setClassificationResult({
        category: "Plastic",
        subcategory: "PET",
        confidence: 0.94,
        estimated_weight_kg: 2.5,
        estimated_payment: 1.25,
        color_code: "#FFA726",
        icon: "♻️"
      })
      setIsClassifying(false)
    }, 1500)
  }

  const handleRequestPickup = () => {
    alert("Pickup request created! Agent will be assigned shortly.")
  }

  return (
    <main className="min-h-dvh">
      <Header />
      <section className="mx-auto w-full max-w-7xl px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">User Portal</h1>
          <p className="text-muted-foreground">Upload waste images for AI classification and request pickup</p>
        </div>

        {/* User Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-green-600">$127.50</div>
              <div className="text-xs text-muted-foreground mt-1">Wallet Balance</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-blue-600">45.2 kg</div>
              <div className="text-xs text-muted-foreground mt-1">Waste Recycled</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-purple-600">113 kg</div>
              <div className="text-xs text-muted-foreground mt-1">CO₂ Saved</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-orange-600">23</div>
              <div className="text-xs text-muted-foreground mt-1">Total Pickups</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload & Classification Section */}
          <Card>
            <CardHeader>
              <CardTitle>📸 Waste Classification</CardTitle>
              <CardDescription>Upload 1-5 images of your waste for AI analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="images">Upload Images</Label>
                <Input 
                  id="images" 
                  type="file" 
                  accept="image/*" 
                  multiple 
                  onChange={handleImageUpload}
                  className="mt-2"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Maximum 5 images • JPG, PNG, WEBP
                </p>
              </div>

              {selectedImages.length > 0 && (
                <div>
                  <Label>Selected Images ({selectedImages.length})</Label>
                  <div className="grid grid-cols-3 gap-2 mt-2">
                    {selectedImages.map((url, idx) => (
                      <div key={idx} className="aspect-square rounded-lg overflow-hidden border">
                        {/* Safe: Using blob: URLs created by URL.createObjectURL() - not user input */}
                        <img src={url} alt={`Waste ${idx + 1}`} className="w-full h-full object-cover" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <Button 
                onClick={handleClassify} 
                disabled={selectedImages.length === 0 || isClassifying}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {isClassifying ? "Analyzing..." : "🤖 Classify Waste"}
              </Button>

              {classificationResult && (
                <div className="border rounded-lg p-4 bg-muted/50 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{classificationResult.icon}</span>
                      <div>
                        <div className="font-semibold">{classificationResult.category}</div>
                        <div className="text-xs text-muted-foreground">{classificationResult.subcategory}</div>
                      </div>
                    </div>
                    <Badge style={{ backgroundColor: classificationResult.color_code }}>
                      {(classificationResult.confidence * 100).toFixed(0)}% confident
                    </Badge>
                  </div>
                  <Separator />
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground">Est. Weight</div>
                      <div className="font-semibold">{classificationResult.estimated_weight_kg} kg</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Est. Payment</div>
                      <div className="font-semibold text-green-600">${classificationResult.estimated_payment}</div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Pickup Request Section */}
          <Card>
            <CardHeader>
              <CardTitle>📍 Request Pickup</CardTitle>
              <CardDescription>Schedule waste collection at your location</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="address">Pickup Address</Label>
                <Input 
                  id="address" 
                  placeholder="Enter your address or use current location"
                  className="mt-2"
                />
              </div>

              <div className="border rounded-lg p-4 bg-muted/50">
                <div className="text-sm font-medium mb-2">🗺️ Location</div>
                <div className="aspect-video bg-slate-200 rounded flex items-center justify-center text-muted-foreground">
                  Map View (Google Maps Integration)
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Pickup Type</Label>
                  <Button variant="outline" className="w-full mt-2">⚡ Immediate</Button>
                </div>
                <div>
                  <Label>Schedule</Label>
                  <Button variant="outline" className="w-full mt-2">📅 Later</Button>
                </div>
              </div>

              {classificationResult && (
                <>
                  <Separator />
                  <div className="space-y-3">
                    <div className="text-sm font-medium">Pickup Summary</div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Waste Type:</span>
                        <span className="font-medium">{classificationResult.category}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Est. Weight:</span>
                        <span className="font-medium">{classificationResult.estimated_weight_kg} kg</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">You'll earn:</span>
                        <span className="font-semibold text-green-600">${classificationResult.estimated_payment}</span>
                      </div>
                    </div>
                  </div>
                </>
              )}

              <Button 
                onClick={handleRequestPickup} 
                disabled={!classificationResult}
                className="w-full bg-blue-600 hover:bg-blue-700"
                size="lg"
              >
                🚚 Request Pickup Now
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Recent Pickups */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Recent Pickups</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { id: 1, type: "Plastic - PET", weight: "3.2 kg", payment: "$1.60", status: "Completed", date: "2 hours ago" },
                { id: 2, type: "Paper - Cardboard", weight: "5.0 kg", payment: "$1.50", status: "In Progress", date: "Today" },
                { id: 3, type: "Metal - Aluminum", weight: "2.0 kg", payment: "$4.00", status: "Completed", date: "Yesterday" }
              ].map((pickup) => (
                <div key={pickup.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                      ♻️
                    </div>
                    <div>
                      <div className="font-medium">{pickup.type}</div>
                      <div className="text-sm text-muted-foreground">{pickup.date}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-green-600">{pickup.payment}</div>
                    <Badge variant={pickup.status === "Completed" ? "default" : "secondary"}>
                      {pickup.status}
                    </Badge>
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
