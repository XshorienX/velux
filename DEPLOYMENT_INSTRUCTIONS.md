# How to Deploy on Render (With Local SQLite Database)

Since we have switched the database from MongoDB to a local SQLite database, deploying on Render requires a **Persistent Disk**. Without a persistent disk, Render will wipe your database every time the server restarts or a new deployment occurs.

Follow these step-by-step instructions to deploy your backend and frontend correctly.

Before you begin, make sure all your code is pushed to a repository on GitHub or GitLab.

---

## Step 1: Deploy the Backend (FastAPI) & Setup Persistent Disk

1. Go to [Render.com](https://dashboard.render.com) and log in.
2. Click the **"New +"** button at the top right and select **"Web Service"**.
3. Select **"Build and deploy from a Git repository"** and choose your repository.
4. Fill in the basic details:
   - **Name**: `app-backend` (or your preferred name)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`

5. **CRITICAL - Setup Persistent Disk:**
   - Scroll down to the **Advanced** section and click **Add Disk**.
   - **Name**: `sqlite-data`
   - **Mount Path**: `/data`
   - *(Note: Persistent Disks require a paid Render plan. If you are on the free tier, your database will reset periodically unless you upgrade.)*

6. Scroll down to **Environment Variables** and add:
   - Key: `SQLITE_DB_PATH` | Value: `/data/local.db` *(This ensures your database saves to the persistent disk)*
   - Key: `PYTHON_VERSION` | Value: `3.11.0`

7. Click **"Create Web Service"**.
8. Wait for the deployment to finish, and **copy the URL of your deployed backend** (e.g., `https://app-backend-xyz.onrender.com`). You will need this for the frontend.

---

## Step 2: Deploy the Frontend (React)

1. Go back to the Render Dashboard, click **"New +"** and select **"Static Site"**.
2. Select the same GitHub repository.
3. Fill in the following details:
   - **Name**: `app-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn install && yarn build`
   - **Publish directory**: `build`

4. Scroll down to **Environment Variables** and add:
   - Key: `REACT_APP_BACKEND_URL` | Value: *Paste the backend URL you copied in Step 1*
   - Key: `NODE_VERSION` | Value: `20.18.0`

5. Click **"Create Static Site"**.
6. Once created, go to the **Redirects/Rewrites** section of your new frontend service in the Render dashboard:
   - Add a new rule:
   - **Source**: `/*`
   - **Destination**: `/index.html`
   - **Action**: `Rewrite`
   - *(This ensures that React Router works correctly when users navigate between pages or refresh).*

7. **Copy the URL of your deployed frontend** (e.g., `https://app-frontend-xyz.onrender.com`).

---

## Step 3: Connect the Backend to the Frontend (CORS Setup)

Now that your frontend is deployed, you need to tell your backend to accept requests from it securely.

1. Go back to your **Backend Service** in the Render dashboard.
2. Go to the **Environment** tab.
3. Add a new environment variable:
   - Key: `FRONTEND_URL` | Value: *Paste the frontend URL you copied in Step 2*
4. Click **Save Changes**. Render will automatically redeploy the backend with the new CORS settings.

🎉 Your application is now fully deployed, and your SQLite database is safely stored on a persistent disk!