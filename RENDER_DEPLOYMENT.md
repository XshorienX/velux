# How to Deploy VeLuX on Render (Local MongoDB Edition)

This guide will walk you through deploying your **VeLuX System** on [Render.com](https://render.com) using a **Local MongoDB Instance** running directly inside your Backend server. This saves you from needing to use MongoDB Atlas!

We have included a `render.yaml` Blueprint file to automate this complex setup.

---

## Important Note on Pricing
Because we are running a local MongoDB database inside the Render container, Render requires a **Persistent Disk** to store the database files so they don't get deleted when the server restarts. 
- Persistent Disks **cannot** be attached to Free Tier instances.
- You must use at least the **Starter Plan ($7/month)** on the backend to attach the disk. 
- (If you want to stay 100% free on Render, you MUST use an external Database like MongoDB Atlas).

---

## Step 1: Push Your Code
Make sure all your latest code (including the `render.yaml` file) is pushed to your GitHub or GitLab repository.

---

## Step 2: Deploy Using Blueprint

1. Go to [Render.com](https://dashboard.render.com) and log in.
2. Click the **"New +"** button at the top right and select **"Blueprint"**.
3. Connect your GitHub/GitLab account and select your repository.
4. Render will read the `render.yaml` file. The `render.yaml` is configured to:
   - Automatically download and install MongoDB binaries during deployment.
   - Boot up MongoDB locally in the background on port 27017.
   - Point the FastAPI app to `mongodb://127.0.0.1:27017`.
   - Mount a 1GB Persistent Disk to `/data/db` to save the data permanently.

5. Fill out the missing environment variables when prompted:
   - **`JWT_SECRET`**: Enter a strong, random password or key to secure user sessions.
   - **`ADMIN_PASSWORD`**: Enter the password you want to use for the `SHORIEN` admin account.
   - **`REACT_APP_BACKEND_URL`**: (Leave this blank for now).
   - **`FRONTEND_URL`**: (Leave this blank for now).
6. Click **"Apply"**.

Render will now begin building both the `velux-backend` and `velux-frontend` Web Services. Wait for both builds to finish.

---

## Step 3: Connect Frontend and Backend

Once the services are deployed, they need to know each other's URLs to communicate properly (CORS).

1. **Find your URLs**:
   - Go to your Render Dashboard.
   - Click on `velux-backend` and copy the URL at the top left (e.g., `https://velux-backend-xyz.onrender.com`).
   - Click on `velux-frontend` and copy its URL at the top left (e.g., `https://velux-frontend-xyz.onrender.com`).

2. **Update Frontend Settings**:
   - In the Render Dashboard, click on `velux-frontend`.
   - Go to the **Environment** tab.
   - Find `REACT_APP_BACKEND_URL` and paste the **Backend URL** you just copied.
   - Click **Save Changes** (Render will automatically redeploy the frontend).

3. **Update Backend CORS**:
   - In the Render Dashboard, click on `velux-backend`.
   - Go to the **Environment** tab.
   - Find `FRONTEND_URL` and paste the **Frontend URL** you just copied.
   - Click **Save Changes** (Render will automatically redeploy the backend).

🎉 **Your VeLuX System is now fully deployed on Render with an internal Local MongoDB!** You can access it by visiting your Frontend URL.