# How to Deploy VeLuX on a VPS using Docker

This guide explains how to deploy your complete stack (Frontend, Backend, and MongoDB) onto a single VPS using Docker and Docker Compose. This method is incredibly reliable, self-contained, and **does not require a domain name**—you can access it directly via your VPS IP address.

## Step 1: Connect to your VPS
Open your terminal and SSH into your VPS:
```bash
ssh root@160.187.210.81
```
*(Enter your password when prompted).*

## Step 2: Install Docker and Git
Once logged in, run these commands to install Docker and Git on your Ubuntu/Debian VPS:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Git
apt install git -y
```

## Step 3: Clone Your Code to the VPS
You need to pull your codebase onto the VPS. If your GitHub repository is public:
```bash
git clone https://github.com/XshorienX/velux.git
cd velux
```
*(If your repository is private, you will need to generate a Personal Access Token on GitHub and use `git clone https://<token>@github.com/XshorienX/velux.git`)*

## Step 4: Run the Deployment
Because we have created a `docker-compose.yml` file, Docker will automatically build and link the database, backend, and frontend together!

Run this single command inside the `velux` folder:
```bash
docker compose up -d --build
```

### What this does:
1. **MongoDB**: Downloads the official Mongo image and sets up persistent storage.
2. **Backend**: Installs Python dependencies and starts the FastAPI server.
3. **Frontend**: Installs Node modules, builds the React app, and puts it behind a high-performance **Nginx** server.
4. **Nginx Routing**: Nginx serves your UI on port 80 and automatically forwards any `/api/` traffic directly to the backend. This bypasses all CORS errors and removes the need to configure IP addresses in the code!

## Step 5: Access Your App
Wait 1-2 minutes for the build to finish. Once it completes, simply open your web browser and go to:
**http://160.187.210.81**

You should see your login screen! Log in with the default credentials:
- **Username**: SHORIEN
- **Password**: YourSecurePassword!

*(Note: You can change these default credentials by editing the `docker-compose.yml` file before running `docker compose up -d`)*

## Useful Docker Commands for Maintenance:
- **View logs**: `docker compose logs -f`
- **Restart the app**: `docker compose restart`
- **Stop the app**: `docker compose down`