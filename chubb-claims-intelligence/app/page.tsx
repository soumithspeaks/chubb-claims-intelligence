import { Suspense } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import Header from "@/components/header"
import ClaimForm from "@/components/claim-form"
import ResultCards from "@/components/analysis/result-cards"
import RiskFraudChart from "@/components/analysis/risk-fraud-chart"
import Recommendations from "@/components/analysis/recommendations"

export type AnalysisResult = {
  riskScore: number // 0-100
  fraudProbability: number // 0-100
  damageSeverity: "Minor" | "Moderate" | "Severe"
  costEstimate: number
  recommendedActions: string[]
}

export default function Page() {
  return (
    <main className="min-h-dvh">
      <Header />
      <section className="mx-auto w-full max-w-6xl px-4 py-8 md:py-10">
        <div className="mb-6 flex flex-col items-start justify-between gap-4 md:mb-8 md:flex-row md:items-end">
          <div>
            <h1 className="text-pretty text-3xl font-semibold tracking-tight md:text-4xl">
              AI-Powered Claims Intelligence
            </h1>
            <p className="mt-2 text-muted-foreground">
              Streamline claim evaluation with automated fraud detection, image-based damage assessment, and cost
              estimation.
            </p>
          </div>
          <div className="rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground">CHUBB</div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Form */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-balance">Submit a Claim for Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <ClaimForm />
            </CardContent>
          </Card>

          {/* Analysis */}
          <div className="grid grid-cols-1 gap-6 lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Analysis Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <ResultCards />
                <Separator />
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                  <div className="rounded-lg border bg-card p-4">
                    <h3 className="mb-3 text-sm font-medium text-muted-foreground">Risk vs. Fraud (Overview)</h3>
                    <Suspense fallback={<div className="text-sm text-muted-foreground">Loading chart…</div>}>
                      <RiskFraudChart />
                    </Suspense>
                  </div>
                  <div className="rounded-lg border bg-card p-4">
                    <h3 className="mb-3 text-sm font-medium text-muted-foreground">Recommended Actions</h3>
                    <Recommendations />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </main>
  )
}
