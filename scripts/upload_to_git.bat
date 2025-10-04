@echo off
echo Uploading AI Agent project to GitHub...

cd /d "c:\Users\Ashmit Pandey\Downloads\Ai-Agent-main"

git init
git remote add origin https://github.com/Ashmit-299/Ai-Agent.git

git add .
git commit -m "Initial commit: AI Content Uploader Agent with RL and video generation"

git branch -M main
git push -u origin main

echo Upload complete!
pause