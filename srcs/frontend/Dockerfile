FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
# CMD ["npm", "run", "dev", "--", "--host"]
RUN npm run build

# =========================================
# Stage 2: Prepare Nginx to Serve Static Files
# =========================================

FROM nginxinc/nginx-unprivileged:alpine3.23 AS runner

# # Copy custom Nginx config
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# # Copy the static build output from the build stage to Nginx's default HTML serving directory
COPY --chown=nginx:nginx --from=builder /app/dist /usr/share/nginx/html

# # Use a built-in non-root user for security best practices
USER nginx

# # Expose port 8080 to allow HTTP traffic
# # Note: The default Nginx container now listens on port 8080 instead of 80
EXPOSE 5173

# # Start Nginx directly with custom config
ENTRYPOINT ["nginx", "-c", "/etc/nginx/nginx.conf"]
CMD ["-g", "daemon off;"]
