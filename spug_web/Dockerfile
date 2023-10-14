FROM whatwewant/builder-node:v16-1 as builder

WORKDIR /build

COPY ./package.json .

COPY ./yarn.lock .

RUN  yarn

COPY . .

RUN yarn build

FROM whatwewant/serve:v1

COPY --from=builder /build/build /var/www/html

