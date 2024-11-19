# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source files
COPY . .

# Add missing dependency explicitly
RUN npm install @babel/plugin-proposal-private-property-in-object --save-dev

# Build the React app
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Copy built assets from the build stage
COPY --from=build /app/package.json /app/package-lock.json /app/build /app/

# Install only production dependencies
RUN npm ci --only=production

# Expose the listening port
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]
