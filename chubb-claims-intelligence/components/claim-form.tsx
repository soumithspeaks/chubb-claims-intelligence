"use client"

import type * as React from "react"
import { useState } from "react"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { useToast } from "@/hooks/use-toast"

const schema = z.object({
  amount: z.string().min(1),
  claimType: z.enum(["Collision", "Theft", "Natural Disaster", "Vandalism", "Other"]),
  policeReport: z.boolean(),
  imageCount: z.number().int().min(0).max(6),
})

export type AnalysisResult = {
  riskScore: number
  fraudProbability: number
  damageSeverity: "Minor" | "Moderate" | "Severe"
  costEstimate: number
  recommendedActions: string[]
  imageBase64?: string
}

export default function ClaimForm() {
  const { toast } = useToast()
  const [amount, setAmount] = useState("")
  const [claimType, setClaimType] = useState<"Collision" | "Theft" | "Natural Disaster" | "Vandalism" | "Other">(
    "Collision",
  )
  const [policeReport, setPoliceReport] = useState(false)
  const [files, setFiles] = useState<FileList | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const [lastImage, setLastImage] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const imageCount = files?.length || 0

    const parse = schema.safeParse({
      amount,
      claimType,
      policeReport,
      imageCount,
    })
    if (!parse.success) {
      toast({ title: "Invalid input", description: "Please review your claim details.", variant: "destructive" })
      return
    }

    try {
      setSubmitting(true)
      const formData = new FormData()
      formData.append("amount", amount)
      formData.append("claimType", claimType)
      formData.append("policeReport", String(policeReport))
      if (files) {
        Array.from(files).forEach(file => {
          formData.append("files", file)
        })
      }
      formData.append("imageCount", String(imageCount))

      const res = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      })
      if (!res.ok) throw new Error("Failed to analyze claim")
      const data: AnalysisResult = await res.json()

      if (data.imageBase64) {
        setLastImage(data.imageBase64)
      } else {
        setLastImage(null)
      }

      window.dispatchEvent(new CustomEvent("analysis:updated", { detail: data }))
      toast({ title: "Analysis complete", description: "Review the insights on the right." })
    } catch (err: any) {
      toast({ title: "Analysis failed", description: err?.message ?? "Please try again.", variant: "destructive" })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={onSubmit} className="grid gap-4">
      <div className="grid gap-2">
        <Label htmlFor="amount">Claim Amount</Label>
        <Input
          id="amount"
          type="number"
          inputMode="decimal"
          placeholder="e.g. 1500"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
        <p className="text-xs text-muted-foreground">Enter the claimant's requested amount in USD.</p>
      </div>

      <div className="grid gap-2">
        <Label>Claim Type</Label>
        <Select 
          value={claimType}
          onValueChange={(value: string) => {
            if (value === "Collision" || 
                value === "Theft" || 
                value === "Natural Disaster" || 
                value === "Vandalism" || 
                value === "Other") {
              setClaimType(value)
            }
          }}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select claim type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Collision">Collision</SelectItem>
            <SelectItem value="Theft">Theft</SelectItem>
            <SelectItem value="Natural Disaster">Natural Disaster</SelectItem>
            <SelectItem value="Vandalism">Vandalism</SelectItem>
            <SelectItem value="Other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center justify-between rounded-md border p-3">
        <div className="space-y-0.5">
          <Label htmlFor="police">Police Report</Label>
          <p className="text-xs text-muted-foreground">Does this claim include an official police report?</p>
        </div>
        <Switch id="police" checked={policeReport} onCheckedChange={setPoliceReport} />
      </div>

      <div className="grid gap-2">
        <Label htmlFor="images">Damage Images</Label>
        <Input
          id="images"
          type="file"
          accept="image/*"
          multiple
          onChange={(e) => setFiles(e.currentTarget.files)}
          aria-describedby="image-help"
        />
        <p id="image-help" className="text-xs text-muted-foreground">
          Upload up to 6 images to support damage assessment.
        </p>
      </div>

      {lastImage && (
        <div className="my-4">
          <Label>Uploaded Image Preview</Label>
          <img
            src={`data:image/png;base64,${lastImage}`}
            alt="Uploaded preview"
            style={{ maxWidth: "100%", borderRadius: "8px", marginTop: "8px" }}
          />
        </div>
      )}

      <Button type="submit" disabled={submitting} className="w-full">
        {submitting ? (
          <span className="inline-flex items-center gap-2">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground/40 border-t-transparent"></span>
            Analyzing…
          </span>
        ) : (
          "Analyze Claim"
        )}
      </Button>
    </form>
  )
}
