FROM node:lts-alpine

WORKDIR /app

# Copy package files first for better layer caching
# Use the existing 'node' user (UID 1000) that comes with the image
COPY --chown=node:node package.json package-lock.json* ./

# Install ALL dependencies (including devDependencies for Vite)
RUN npm install --silent

# Copy application code with proper ownership
COPY --chown=node:node . .

# Switch to non-root user (using the existing 'node' user)
USER node

# Expose Vite dev server port
EXPOSE 5173

# Default command for development
CMD ["npm", "run", "dev", "--", "--host"]
