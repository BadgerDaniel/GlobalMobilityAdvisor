# Team Deployment Guide - Global IQ Mobility Advisor

This guide helps your teammates deploy the Global IQ Mobility Advisor application using Docker.

## 🚀 Quick Start for Team Members

### Prerequisites

**⚠️ IMPORTANT: Make sure you have Docker installed first!**

#### Install Docker Desktop:
- **Windows**: Download from [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
- **Mac**: Download from [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- **Linux**: Follow [Docker Engine installation guide](https://docs.docker.com/engine/install/)

**After installation, make sure Docker Desktop is running** (you should see the Docker whale icon in your system tray/menu bar).

#### Verify Docker Installation:
```bash
docker --version
docker-compose --version
```
Both commands should return version numbers. If not, Docker is not properly installed.

#### Other Requirements:
- OpenAI API key

### Method 1: Using the Deployment Script (Recommended)

#### For Mac/Linux:
1. **Get the project files** (from shared folder/Git repository)
2. **Navigate to project directory**:
   ```bash
   cd global-iq-application
   ```
3. **Add your OpenAI API key**:
   ```bash
   echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
   ```
4. **Run the deployment script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
5. **Access the application**: http://localhost:8000

#### For Windows (Command Prompt or PowerShell):
1. **Get the project files** (from shared folder/Git repository)
2. **Navigate to project directory**:
   ```cmd
   cd global-iq-application
   ```
3. **Add your OpenAI API key**:
   ```cmd
   echo OPENAI_API_KEY=your_actual_api_key_here > .env
   ```
4. **Run Docker Compose directly** (since deploy.sh is a bash script):
   ```cmd
   docker-compose up --build
   ```
5. **Access the application**: http://localhost:8000

### Method 2: Manual Docker Compose (Works on All Platforms)

```bash
# 1. Navigate to project
cd global-iq-application

# 2. Create .env file with your API key
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env

# 3. Build and run
docker-compose up --build
```

### Method 3: Using Pre-built Docker Image

If a Docker Hub image is available:
```bash
docker run -d \
  --name global-iq-app \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key_here \
  yourusername/global-iq-mobility-advisor:latest
```

## 🔐 Login Credentials

Use these test credentials:
- **Demo User**: `demo` / `demo`
- **Admin User**: `admin` / `admin123`
- **Employee**: `employee` / `employee123`
- **HR Manager**: `hr_manager` / `hr2024`

## ✅ Application Features

Your deployed application includes:
- 🔐 **Authentication System** - Role-based login
- 💬 **Session-based Chat** - Chat history within sessions
- 📁 **File Processing** - Upload PDF, DOCX, TXT, CSV, JSON, XLSX
- 🤖 **AI Agent Routing** - Policy and compensation analysis
- 👨‍💼 **Admin Commands** - User management tools

## 🛠️ Useful Commands

```bash
# View application logs
docker logs global-iq-mobility-advisor

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Rebuild after code changes
docker-compose up --build

# Check running containers
docker ps
```

## 🔧 Troubleshooting

### Docker Not Installed
If you get "docker: command not found":
1. Install Docker Desktop from the links above
2. Make sure Docker Desktop is running
3. Restart your terminal/command prompt

### Port Already in Use
```bash
# Stop existing containers
docker stop global-iq-mobility-advisor
docker rm global-iq-mobility-advisor

# Or use different port
docker run -p 8001:8000 global-iq-app
```

### Application Won't Start
1. **Check Docker is running** (Docker Desktop icon in system tray/menu bar)
2. **Verify your OpenAI API key** is correct in `.env`
3. **Check logs**: `docker logs global-iq-mobility-advisor`
4. **Try rebuilding**: `docker-compose up --build`

### Permission Issues (Mac/Linux)
```bash
chmod +x deploy.sh
```

### Windows-Specific Issues
- Use Command Prompt or PowerShell (not Git Bash for Docker commands)
- Make sure Docker Desktop is running before executing commands
- If using PowerShell, you might need to enable execution policies

## 📝 Development Notes

- **Port**: Application runs on port 8000
- **Environment**: All dependencies included in Docker image
- **Database**: Uses session-based storage (no external DB required)
- **Files**: Uploaded files are processed in memory

## 🎯 Success Indicators

When successfully deployed, you should see:
- ✅ Login screen at http://localhost:8000
- ✅ Successful authentication with test credentials
- ✅ Chat interface with file upload capability
- ✅ AI responses to policy and compensation queries

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed (especially Docker)
3. Make sure Docker Desktop is running
4. Contact the development team with error logs
