# agent_skills
a collection of curated agent skills for personal workflows

# Setup
1. git clone this repo

2. symlink /.claude/skills to the repo (destructive, will replace). Windows will need developer mode on.

   Powershell:
   cmd /c mklink /D "$env:USERPROFILE\.claude\skills" "D:\...\agent-skills"

   OR
   
   ln -s ~/dev/agent-skills ~/.claude/skills
