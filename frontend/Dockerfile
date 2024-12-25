FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npx prisma generate --schema=./prisma/schema.prisma
RUN npm run build && npm prune --production

ENV PORT 3000


# FROM node:20-alpine

# WORKDIR /app

# COPY --from=build /app/node_modules ./node_modules
# COPY --from=build /app/prisma ./prisma
# COPY --from=build /app/package.json ./package.json
# COPY --from=build /app/build ./build

EXPOSE 3000

CMD ["node", "build"]
