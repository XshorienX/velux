# How to Deploy VeLuX on Render (MongoDB Edition)

This guide will walk you through deploying your **VeLuX System** on [Render.com](https://render.com) utilizing a MongoDB database.

We have included a `render.yaml` Blueprint file to make deployment as easy as clicking a few buttons.

---

## Step 0: Prepare Your Database
Before deploying to Render, you need a MongoDB database hosted in the cloud.
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) and create a free account.
2. Create a free **M0 Cluster**.
3. Create a Database User and save the **password**.
4. In Network Access, allow access from anywhere (`0.0.0.0/0`).
5. Click "Connect" -> "Connect your application" and copy the **Connection String** (it starts with `mongodb+srv://...`).

---

## Step 1: Push Your Code
Make sure all your latest code (including the `render.yaml` file) is pushed to your GitHub or GitLab repository.

---

## Step 2: Deploy Using Blueprint

1. Go to [Render.com](https://dashboard.render.com) and log in.
2. Click the **"New +"** button at the top right and select **"Blueprint"**.
3. Connect your GitHub/GitLab account and select your repository.
4. Render will read the `render.yaml` file and prompt you for the required environment variables:
   - **`MONGO_URL`**: Paste your MongoDB Atlas connection string here (replace `<password>` with your actual DB password).
   - **`JWT_SECRET`**: Enter a strong, random password or key to secure user sessions.
   - **`ADMIN_PASSWORD`**: Enter the password you want to use for the `SHORIEN` admin account.
   - **`REACT_APP_BACKEND_URL`**: (Leave this blank for now, or enter a dummy URL like `https://temp.com`).
   - **`FRONTEND_URL`**: (Leave this blank for now, or enter a dummy URL like `https://temp.com`).
5. Click **"Apply"**.

Render will now begin building both the `velux-backend` and `velux-frontend` Web Services. Wait for both builds to finish.

---

## Step 3: Connect Frontend and Backend

Once the services are deployed, they need to know each other's URLs to communicate properly.

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

🎉 **Your VeLuX System is now fully deployed on Render with MongoDB!** You can access it by visiting your Frontend URL.