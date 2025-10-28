@echo off
REM Global IQ Kubernetes Deployment Script for Windows
REM This script builds, pushes, and deploys the Global IQ application to Kubernetes

setlocal enabledelayedexpansion

REM Configuration
if "%DOCKER_USERNAME%"=="" set DOCKER_USERNAME=YOUR_DOCKERHUB_USERNAME
set APP_NAME=global-iq-app
if "%VERSION%"=="" set VERSION=v1
set IMAGE_NAME=%DOCKER_USERNAME%/%APP_NAME%:%VERSION%
set NAMESPACE=global-iq

echo ========================================
echo Global IQ Kubernetes Deployment
echo ========================================
echo.

REM Step 1: Check prerequisites
echo Step 1: Checking prerequisites...

where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not installed
    exit /b 1
)

where kubectl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: kubectl is not installed
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Docker daemon is not running
    exit /b 1
)

REM Check if Kubernetes cluster is accessible
kubectl cluster-info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Cannot connect to Kubernetes cluster
    exit /b 1
)

echo [OK] Prerequisites check passed
echo.

REM Step 2: Build Docker image
echo Step 2: Building Docker image...
echo Image: %IMAGE_NAME%

docker build -t %IMAGE_NAME% .

if %ERRORLEVEL% neq 0 (
    echo Error: Docker build failed
    exit /b 1
)

echo [OK] Docker image built successfully
echo.

REM Step 3: Push to Docker Hub (optional)
echo Step 3: Push to Docker Hub? (y/n)
set /p PUSH_RESPONSE=

if /i "%PUSH_RESPONSE%"=="y" (
    echo Pushing %IMAGE_NAME% to Docker Hub...

    if "%DOCKER_USERNAME%"=="YOUR_DOCKERHUB_USERNAME" (
        echo Error: Please set DOCKER_USERNAME environment variable
        echo Example: set DOCKER_USERNAME=yourname
        exit /b 1
    )

    docker push %IMAGE_NAME%

    if %ERRORLEVEL% neq 0 (
        echo Error: Docker push failed. Make sure you're logged in (docker login^)
        exit /b 1
    )

    echo [OK] Image pushed successfully
) else (
    echo Skipping Docker Hub push
)
echo.

REM Step 4: Create secret.yaml if it doesn't exist
echo Step 4: Checking Kubernetes secrets...

if not exist "k8s\secret.yaml" (
    echo Warning: k8s\secret.yaml not found
    echo Creating from template...

    set /p OPENAI_KEY="Enter your OpenAI API key: "
    set /p CHAINLIT_SECRET="Enter Chainlit auth secret (or press enter for 'password'^): "

    if "!CHAINLIT_SECRET!"=="" set CHAINLIT_SECRET=password

    REM Base64 encode (using PowerShell)
    for /f "delims=" %%i in ('powershell -command "[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('!OPENAI_KEY!'^)^)"') do set OPENAI_KEY_B64=%%i
    for /f "delims=" %%i in ('powershell -command "[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('!CHAINLIT_SECRET!'^)^)"') do set CHAINLIT_SECRET_B64=%%i

    REM Create secret.yaml from template
    powershell -command "(Get-Content k8s\secret.yaml.template) -replace 'REPLACE_WITH_BASE64_ENCODED_OPENAI_KEY', '!OPENAI_KEY_B64!' -replace 'cGFzc3dvcmQ=', '!CHAINLIT_SECRET_B64!' | Set-Content k8s\secret.yaml"

    echo [OK] secret.yaml created
) else (
    echo [OK] secret.yaml exists
)
echo.

REM Step 5: Update deployment image
echo Step 5: Updating deployment manifest...

REM Update the image in deployment.yaml using PowerShell
powershell -command "(Get-Content k8s\deployment.yaml) -replace 'image: .*global-iq-app:.*', 'image: %IMAGE_NAME%' | Set-Content k8s\deployment.yaml"

echo [OK] Deployment manifest updated
echo.

REM Step 6: Deploy to Kubernetes
echo Step 6: Deploying to Kubernetes...

REM Create namespace
kubectl apply -f k8s\namespace.yaml

REM Apply all configurations
kubectl apply -f k8s\configmap.yaml
kubectl apply -f k8s\secret.yaml
kubectl apply -f k8s\persistent-volume.yaml
kubectl apply -f k8s\deployment.yaml

echo [OK] Kubernetes resources deployed
echo.

REM Step 7: Wait for deployment
echo Step 7: Waiting for deployment to be ready...

kubectl wait --for=condition=available --timeout=300s deployment/global-iq-deployment -n %NAMESPACE%

if %ERRORLEVEL% equ 0 (
    echo [OK] Deployment is ready
) else (
    echo Warning: Deployment may not be ready yet
    echo Check status with: kubectl get pods -n %NAMESPACE%
)
echo.

REM Step 8: Display status
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Namespace: %NAMESPACE%
echo Image: %IMAGE_NAME%
echo.
echo Useful commands:
echo   View pods:      kubectl get pods -n %NAMESPACE%
echo   View services:  kubectl get svc -n %NAMESPACE%
echo   View logs:      kubectl logs -f deployment/global-iq-deployment -n %NAMESPACE%
echo   Port forward:   kubectl port-forward svc/global-iq-service 8000:8000 -n %NAMESPACE%
echo   Scale:          kubectl scale deployment/global-iq-deployment --replicas=3 -n %NAMESPACE%
echo   Delete:         kubectl delete namespace %NAMESPACE%
echo.

REM Step 9: Offer to port-forward
echo Would you like to start port-forwarding now? (y/n)
set /p PORT_FORWARD_RESPONSE=

if /i "%PORT_FORWARD_RESPONSE%"=="y" (
    echo.
    echo Starting port-forward on http://localhost:8000
    echo Press Ctrl+C to stop
    kubectl port-forward svc/global-iq-service 8000:8000 -n %NAMESPACE%
) else (
    echo.
    echo Access your application by running:
    echo kubectl port-forward svc/global-iq-service 8000:8000 -n %NAMESPACE%
)

endlocal
