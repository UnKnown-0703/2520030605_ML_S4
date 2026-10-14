try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $docPath = "E:\KLU\Y2--S1\ML\2520030605_ML_S4\ProjectML\Heart_Disease_Prediction_Case_Study_Report.docx"
    $pdfPath = "E:\KLU\Y2--S1\ML\2520030605_ML_S4\ProjectML\Heart_Disease_Prediction_Case_Study_Report.pdf"
    $doc = $word.Documents.Open($docPath)
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close()
    $word.Quit()
    Write-Host "PDF successfully created!"
} catch {
    Write-Host "Word COM error: " $_.Exception.Message
}
