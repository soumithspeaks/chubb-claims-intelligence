
import { NextRequest, NextResponse } from "next/server"

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData()
    
    // Prepare the data for ML backend
    const mlFormData = new FormData()
    
    // Add claim data
    const claimData = {
      ClaimAmount: Number(formData.get("amount")),
      VehiclePrice: 25000, // Default value
      VehicleAge: 3,
      PolicyDuration: 365,
      previous_claims_count: 0,
      time_to_report: 1,
      claim_time: new Date().toISOString().split('T')[0],
      required_documents: {
        'Police Report': formData.get("policeReport") === "true",
        'Medical Report': false,
        'Witness Statement': false,
        'Photos': false
      },
      claimType: formData.get("claimType")
    }
    
    mlFormData.append('claim_data', JSON.stringify(claimData))
    
    // Add files
    const files = formData.getAll("files")
    if (files.length > 0) {
      for (const file of files) {
        mlFormData.append('files', file)
      }
    }

    // Call ML backend
    const mlResponse = await fetch('http://localhost:8000/api/analyze-claim', {
      method: 'POST',
      body: mlFormData
    })

    if (!mlResponse.ok) {
      throw new Error('ML analysis failed')
    }

    const mlResult = await mlResponse.json()

    // Convert first image to base64 if available
    let imageBase64 = null
    if (files.length > 0) {
      const file = files[0] as File
      const arrayBuffer = await file.arrayBuffer()
      const buffer = Buffer.from(arrayBuffer)
      imageBase64 = buffer.toString("base64")
    }

    // Return combined result
    return NextResponse.json({
      riskScore: Math.round(mlResult.riskScore),
      fraudProbability: Math.round(mlResult.fraudProbability * 100),
      damageSeverity: mlResult.damageSeverity,
      costEstimate: Math.round(mlResult.costEstimate),
      recommendedActions: mlResult.recommendations,
      imageBase64,
      details: mlResult.details || {}
    })
  } catch (error) {
    console.error('Analysis failed:', error)
    return NextResponse.json(
      { error: 'Failed to process claim' },
      { status: 500 }
    )
  }
}
