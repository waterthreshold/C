$filePath = "app_lister.py" # Replace with your actual file path
if (Test-Path -Path $filePath -PathType Leaf) {
# Search for the pattern and grab the first match
	$match = Select-String -Path $filePath -Pattern 'APPLISTER_VERSION\s*=\s*["'']([^"'']+)["'']' | Select-Object -First 1

	if ($match) {
		# Extract the value from the first capturing group
		$version = $match.Matches.Groups[1].Value
		pyinstaller --noconsole --onefile --icon=app.ico --name AppLister_v$version  app_lister.py
	} else {
	   pyinstaller --noconsole --onefile --icon=app.ico app_lister.py
	}
} else {
    Write-Host "Error: The file '$filePath' does not exist." -ForegroundColor Red
}

