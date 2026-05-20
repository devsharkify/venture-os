FROM node:20-alpine AS build

WORKDIR /app

COPY package.json yarn.lock* ./
RUN yarn install --ignore-engines --network-timeout 100000

COPY . .

ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV CI=false
ENV GENERATE_SOURCEMAP=false

RUN yarn build

FROM node:20-alpine
RUN npm install -g serve
WORKDIR /app
COPY --from=build /app/build ./build
CMD ["sh", "-c", "serve -s build -l ${PORT:-3000}"]
