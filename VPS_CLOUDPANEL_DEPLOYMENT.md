# CloudPanel VPS Deployment Guide

This guide will walk you through deploying your **VeLuX System** across two separate VPS instances using **CloudPanel**. We will use one VPS for the **Backend (Python FastAPI + MongoDB)** and the other for the **Frontend (React)**.

---

## VPS 1: Backend Deployment (Python API & Database)

Since your backend uses MongoDB, you can easily connect it to a hosted cluster (like MongoDB Atlas) or install MongoDB locally on your VPS if preferred.

### Step 1: Create a Python App in CloudPanel
1. Log in to your CloudPanel dashboard on **VPS 1**.
2. Go to **Sites** and click **Add Site**.
3. Choose **Create a Python Site**.
4. Fill in the details:
   - **Domain Name**: `api.yourdomain.com` (Ensure your DNS points to this VPS IP)
   - **Python Version**: Select Python 3.11+
   - **App Port**: Choose a port (e.g., `8001`)

### Step 2: Upload Files and Install Dependencies
1. Connect to VPS 1 via SSH or use the CloudPanel File Manager.
2. Navigate to your app directory: `/htdocs/api.yourdomain.com/`
3. Upload all files from your `backend/` folder into this directory.
4. SSH into the server as the site user (CloudPanel provides SSH credentials per site) and navigate to the directory.
5. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
   ```

### Step 3: Configure Environment Variables
1. Create a `.env` file in the root of your backend directory (`/htdocs/api.yourdomain.com/.env`).
2. Add the following variables:
   ```env
   MONGO_URL=mongodb+srv://<your-db-user>:<your-db-pass>@cluster.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=velux
   FRONTEND_URL=https://checker.yourdomain.com
   JWT_SECRET=generate-a-strong-random-secret-key-here
   ADMIN_USERNAME=SHORIEN
   ADMIN_PASSWORD=YourSecurePassword!
   ```

### Step 4: Configure App Startup
1. In CloudPanel, go to the **Site Settings** for `api.yourdomain.com`.
2. Find the **Startup Command** or **Vhost configuration** section.
3. Your app should be started via Uvicorn:
   ```bash
   uvicorn server:app --host 127.0.0.1 --port 8001
   ```
*(Note: CloudPanel automatically configures NGINX as a reverse proxy to route traffic from port 80/443 down to your local Python port `8001`.)*

4. Restart your Python app via CloudPanel. Your backend is now live!

---

## VPS 2: Frontend Deployment (React)

### Step 1: Build the Frontend Locally
Before uploading to the VPS, you should compile the React frontend.
1. On your local computer, open the `.env` file inside the `frontend/` folder.
2. Update the API URL to point to your new backend VPS:
   ```env
   REACT_APP_BACKEND_URL=https://api.yourdomain.com
   ```
3. Run the build command:
   ```bash
   yarn install
   yarn build
   ```
4. This will create a `build/` folder containing your compiled static site.

### Step 2: Create a Static HTML Site in CloudPanel
1. Log in to your CloudPanel dashboard on **VPS 2**.
2. Go to **Sites** and click **Add Site**.
3. Choose **Create a Static HTML Site**.
4. Fill in the details:
   - **Domain Name**: `checker.yourdomain.com` (Ensure your DNS points to this VPS IP)

### Step 3: Upload Files
1. Open the CloudPanel File Manager for `checker.yourdomain.com`.
2. Navigate to the `htdocs/checker.yourdomain.com/` directory.
3. Delete the default `index.html`.
4. Upload all the contents of your local `build/` folder into this directory.

### Step 4: Configure NGINX for React Router
Because React uses client-side routing, you need to tell NGINX to redirect all traffic to `index.html`.
1. In CloudPanel, go to **Site Settings** -> **Vhost**.
2. Find the `location / { ... }` block and update it to look like this:
   ```nginx
   location / {
       try_files $uri $uri/ /index.html;
   }
   ```
3. Save the Vhost configuration and restart NGINX if prompted.

### Step 5: Issue SSL Certificates
1. Go to the **SSL/TLS** tab in CloudPanel for both your Frontend and Backend sites.
2. Issue a free **Let's Encrypt** certificate for both domains (`api.yourdomain.com` and `checker.yourdomain.com`).

🎉 **Your VeLuX System is now fully deployed across two VPS instances!**