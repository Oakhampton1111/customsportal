# Root Dockerfile for Digital Ocean detection
# This forces Digital Ocean to use Docker instead of buildpacks

FROM alpine:latest

# Install basic tools
RUN apk add --no-cache curl

# Create a simple health check endpoint
RUN echo '#!/bin/sh' > /health.sh && \
    echo 'echo "Multi-service application - see backend/ and frontend/ directories"' >> /health.sh && \
    chmod +x /health.sh

EXPOSE 8080

CMD ["/health.sh"]
