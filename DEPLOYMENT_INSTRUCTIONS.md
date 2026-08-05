# Deploying on Render using render.yaml

Your project is ready to be deployed on Render! I have created a `render.yaml` file in the root of your project. Render uses this "Blueprint" file to automatically provision and configure both your backend and frontend.

## Step-by-Step Deployment Instructions

### 1. Push your code to GitHub/GitLab
Make sure all your code, including the newly created `render.yaml` file, is pushed to a repository on GitHub or GitLab.

### 2. Log in to Render
Go to [Render.com](https://render.com) and log in to your dashboard.

### 3. Create a New Blueprint
1. Click the **"New +"** button at the top right of the dashboard.
2. Select **"Blueprint"** from the dropdown menu.
3. Connect your GitHub or GitLab account if you haven't already.
4. Select the repository containing your project.

### 4. Configure Blueprint Variables
Render will read the `render.yaml` file and prepare to create two services:
- **app-backend**: A Web Service for your FastAPI backend.
- **app-frontend**: A Static Site for your React frontend.

During the setup, Render will prompt you for two Environment Variables that cannot be hardcoded for security reasons:

1. **`MONGO_URL`** (for the backend): 
   - Provide your MongoDB Atlas connection string (e.g., `mongodb+srv://<user>:<password>@cluster0...`).
2. **`REACT_APP_BACKEND_URL`** (for the frontend): 
   - You need to provide the external URL of your backend service. 
   - **Important:** At first, you might not know the exact backend URL. You can enter a placeholder (like `https://placeholder.onrender.com`), finish the Blueprint creation, and once the backend service is created, copy its actual URL (e.g., `https://app-backend-xxxxx.onrender.com`), and update this variable in your `app-frontend` service settings, then trigger a manual deploy for the frontend.

### 5. Apply and Deploy
Click **"Apply"** or **"Create"**. Render will start deploying both services.
- The **backend** will install Python dependencies and start the Uvicorn server.
- The **frontend** will install Node dependencies, build the React app, and serve it statically.

### Notes
- **CORS Setup**: The backend is currently configured to accept CORS from `os.environ.get("FRONTEND_URL", "http://localhost:3000")`. You should add `FRONTEND_URL` as an environment variable in your backend's Render dashboard settings to point to your deployed frontend URL (e.g., `https://app-frontend-xxxxx.onrender.com`) to avoid CORS errors.
- **Routing**: The static site is configured to rewrite all routes to `/index.html` to fully support your React app's routing.