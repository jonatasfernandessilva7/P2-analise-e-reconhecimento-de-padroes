FROM node:22.14.0 AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci || (rm -rf node_modules && npm install)

COPY . .

RUN npm run build

FROM node:22.14.0

WORKDIR /app

COPY --from=build /app/dist ./dist
COPY --from=build /app/package*.json ./

RUN npm ci --omit=dev || (rm -rf node_modules && npm install --omit=dev)

EXPOSE 4000

CMD ["node", "dist/sistemaP2/server/server.mjs"]
