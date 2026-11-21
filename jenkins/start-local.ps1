$ErrorActionPreference = 'Stop'
$labRuntime = Join-Path $env:LOCALAPPDATA '435L-Lab10'
$env:JENKINS_HOME = Join-Path $labRuntime 'jenkins-home'
$java = Join-Path $labRuntime 'tools/jre/jdk-21.0.13.1+2-jre/bin/java.exe'
$war = Join-Path $labRuntime 'tools/jenkins-2.580.2.war'
if (!(Test-Path -LiteralPath $java) -or !(Test-Path -LiteralPath $war)) {
    throw 'The prepared Lab 10 runtime is missing. Follow README.md for setup.'
}
if (Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue) {
    Write-Output 'Port 8080 is already in use. Check http://localhost:8080.'
    exit 0
}
$process = Start-Process -FilePath $java -ArgumentList @(
    '-Djenkins.install.runSetupWizard=false', '-jar', ('"' + $war + '"'),
    '--httpPort=8080', '--httpListenAddress=127.0.0.1'
) -WindowStyle Hidden -PassThru -RedirectStandardOutput (
    Join-Path $labRuntime 'jenkins.out.log'
) -RedirectStandardError (Join-Path $labRuntime 'jenkins.err.log')
$process.Id | Set-Content (Join-Path $labRuntime 'jenkins.pid')
Write-Output "Jenkins started (PID $($process.Id)): http://localhost:8080"
