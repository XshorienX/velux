# Stage 1: Build the React application
FROM node:20.18-alpine as builder
WORKDIR /app

# Copy package files
COPY package.json yarn.lock .npmrc ./

# Install dependencies securely bypassing peer conflicts
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

# We set the backend URL to empty so it automatically routes to the same IP (caught by Nginx)
ENV REACT_APP_BACKEND_URL=""

# Build the app
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled React build
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]