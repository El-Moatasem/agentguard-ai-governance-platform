FROM node:20-alpine

WORKDIR /app
RUN corepack enable && corepack prepare yarn@1.22.22 --activate

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

ENV CHOKIDAR_USEPOLLING=true \
    WATCHPACK_POLLING=true \
    NODE_ENV=development

EXPOSE 5173
CMD ["yarn", "dev", "--host", "0.0.0.0"]
