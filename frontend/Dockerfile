# ==========================================
# 1. Base Stage (Базовая настройка)
# ==========================================
FROM node:20-alpine AS base

RUN apk add --no-cache libc6-compat

WORKDIR /app

ENV HOST=0.0.0.0
ENV PORT=3000

# ==========================================
# 2. Development Stage (Для локальной разработки)
# ==========================================
FROM base AS development

COPY package*.json ./

RUN npm install

COPY . .

CMD ["npm", "run", "dev"]

# ==========================================
# 3. Builder Stage (Сборка для продакшена)
# ==========================================
FROM base AS builder

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

# ==========================================
# 4. Production Stage (Финальный минимальный образ)
# ==========================================
FROM base AS production

ENV NODE_ENV=production

COPY --from=builder /app/.output /app/.output

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
