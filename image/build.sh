docker build -t base-image:latest .
docker tag base-image:latest 2mmanu/agentbuddy:latest
docker push 2mmanu/agentbuddy:latest