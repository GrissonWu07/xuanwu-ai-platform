FROM node:20-alpine AS builder
WORKDIR /app

COPY main/xuanwu-portal/package*.json ./
RUN npm ci

COPY main/xuanwu-portal/ ./
RUN npm run build

FROM nginx:1.27-alpine
COPY main/xuanwu-portal/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
