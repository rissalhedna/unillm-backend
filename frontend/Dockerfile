FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npx prisma generate --schema=./prisma/schema.prisma

RUN npm run build --verbose

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]