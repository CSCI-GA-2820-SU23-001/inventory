#!/bin/bash
echo "Copying IBM Cloud apikey into development environment..."
docker cp ~/.inventory/apikey.json inventory:/home/vscode 
docker exec inventory sudo chown vscode:vscode /home/vscode/apikey.json
echo "Complete"
