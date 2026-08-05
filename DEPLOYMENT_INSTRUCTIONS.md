# How to Deploy on Render

There are two ways to deploy your application to Render: using the provided `render.yaml` Blueprint (Easiest), or setting up the backend and frontend manually step-by-step.

Before you begin, make sure your code is pushed to a repository on GitHub or GitLab.

---

## Method 1: Using the Blueprint (Easiest & Recommended)

Since we already created a `render.yaml` file, Render can automatically detect your setup and create both services for you.

1. Go to [Render.com](https://dashboard.render.com) and log in.
2. Click the **"New +"** button at the top right and select **"Blueprint"**.
3. Connect your GitHub/GitLab account and select your repository.
4. Render will read the `render.yaml` file and prompt you for the required environment variables:
   - `MONGO_URL`: Your MongoDB Atlas connection string.
   - `FRONTEND_URL`: (Optional initially) The URL of your deployed frontend to allow CORS.
   - `REACT_APP_BACKEND_URL`: (Optional initially) The URL of your deployed backend.
5. Click **"Apply"**.
6. **Important Post-Deploy Step:**
   - Once the services are created, copy the URL of your new backend service (e.g., `https://app-backend-xyz.onrender.com`).
   - Go to your Frontend service settings -> Environment -> Update `REACT_APP_BACKEND_URL` with that backend URL.
   - Copy the URL of your new frontend service (e.g., `https://app-frontend-xyz.onrender.com`).
   - Go to your Backend service settings -> Environment -> Update `FRONTEND_URL` with that frontend URL.
   - Manually trigger a "Deploy" on both services for the changes to take effect.

---

## Method 2: Manual Step-by-Step Setup

If you prefer to create the services one by one manually, follow these instructions:

### Part 1: Deploying the Backend (FastAPI)

1. In your Render Dashboard, click **"New +"** and select **"Web Service"**.
2. Select **"Build and deploy from a Git repository"** and choose your repository.
3. Fill in the following details:
   - **Name**: `app-backend` (or whatever you prefer)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Scroll down to **Environment Variables** and add:
   - Key: `MONGO_URL` | Value: *Your MongoDB connection string*
   - Key: `PYTHON_VERSION` | Value: `3.11.0`
5. Click **"Create Web Service"**.
6. Wait for the deployment to finish, and **copy the URL of your deployed backend** (e.g., `https://app-backend-xyz.onrender.com`).

### Part 2: Deploying the Frontend (React)

1. Go back to the Render Dashboard, click **"New +"** and select **"Static Site"**.
2. Select the same GitHub repository.
3. Fill in the following details:
   - **Name**: `app-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn install && yarn build`
   - **Publish directory**: `build`
4. Scroll down to **Environment Variables** and add:
   - Key: `REACT_APP_BACKEND_URL` | Value: *Paste the backend URL you copied in Part 1*
   - Key: `NODE_VERSION` | Value: `20.0.0`
5. Click **"Create Static Site"**.
6. While it builds, go to the **Redirects/Rewrites** section of your new static site:
   - **Source**: `/*`
   - **Destination**: `/index.html`
   - **Action**: `Rewrite`
   - *(This ensures that React Router works correctly when users refresh the page).*
7. **Copy the URL of your deployed frontend** (e.g., `https://app-frontend-xyz.onrender.com`).

### Part 3: Connecting the Backend to the Frontend (CORS)

Now that your frontend is deployed, you need to tell your backend to allow requests from it.

1. Go back to your **Backend Service** in the Render dashboard.
2. Go to the **Environment** tab.
3. Add a new environment variable:
   - Key: `FRONTEND_URL` | Value: *Paste the frontend URL you copied in Part 2*
4. Click **Save Changes**. Render will automatically redeploy the backend with the new CORS settings.

Your application is now fully deployed and connected!