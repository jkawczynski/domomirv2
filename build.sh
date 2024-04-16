rm app/upload/recipes/*
docker build -t domomir_v2 --build-arg APP_VERSION=$(git rev-parse --short HEAD) .
