$sevenZip = "C:\Users\10008847\scoop\apps\7zip\25.01\7z.exe"
$dir = $args[0]

Get-ChildItem $dir -Filter "*.7z" | ForEach-Object {
    & $sevenZip x $_.FullName "-o$dir\" -y
}