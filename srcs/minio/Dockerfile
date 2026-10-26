# Builds minio + mc once (needs internet at BUILD time only).
FROM golang:alpine AS build
RUN apk add --no-cache git gcc musl-dev
# After the first successful build, pin these to the versions that resolved
# (e.g. find them with: docker run --rm ready2roll_minio minio --version).
ARG MINIO_REF=latest
ARG MC_REF=latest
RUN go install github.com/minio/minio@${MINIO_REF} \
 && go install github.com/minio/mc@${MC_REF}

FROM alpine:3.20
COPY --from=build /go/bin/minio /go/bin/mc /usr/local/bin/
