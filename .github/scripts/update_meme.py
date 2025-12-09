import os
import requests
import random
from datetime import datetime, timedelta
from github import Github

# Meme collections for different scenarios using imgflip API IDs
MEME_COLLECTIONS = {
    'very_active': [  # 15+ commits in last 7 days
        'https://i.imgflip.com/2fm6x.jpg',  # Expanding brain
        'https://i.imgflip.com/1ur9b0.jpg',  # Stonks
        'https://i.imgflip.com/30b1gx.jpg',  # I am speed
        'https://i.imgflip.com/4t0m5.jpg',  # Leonardo DiCaprio
    ],
    'active': [  # 7-14 commits in last 7 days
        'https://i.imgflip.com/5aflat.jpg',  # Panik Kalm
        'https://i.imgflip.com/8p0s.jpg',  # Good guy
        'https://i.imgflip.com/1bij.jpg',  # Success kid
        'https://i.imgflip.com/26am.jpg',  # Satisfied seal
    ],
    'moderate': [  # 3-6 commits in last 7 days
        'https://i.imgflip.com/261o3j.jpg',  # This is fine
        'https://i.imgflip.com/grr.jpg',  # Morpheus
        'https://i.imgflip.com/1g8my4.jpg',  # Distracted boyfriend
        'https://i.imgflip.com/3lmzyx.jpg',  # Bernie Sanders
    ],
    'low': [  # 1-2 commits in last 7 days
        'https://i.imgflip.com/3oevdk.jpg',  # Disappointed
        'https://i.imgflip.com/2cp1.jpg',  # Hide the pain
        'https://i.imgflip.com/9vct.jpg',  # Philosoraptor
        'https://i.imgflip.com/1ihzfe.jpg',  # Roll safe
    ],
    'inactive': [  # 0 commits in last 7 days
        'https://i.imgflip.com/1g8my4.jpg',  # Distracted boyfriend
        'https://i.imgflip.com/2cp1.jpg',  # Hide pain Harold
        'https://i.imgflip.com/5gimtn.jpg',  # Bernie sitting
        'https://i.imgflip.com/3umi0.jpg',  # Monkey puppet
    ],
    'weekend_warrior': [  # Most commits on weekends
        'https://i.imgflip.com/4t0m5.jpg',  # Party hard
        'https://i.imgflip.com/1bij.jpg',  # Success kid
    ]
}

def get_commit_count(username, days=7):
    """Get number of commits in the last N days"""
    token = os.getenv('GITHUB_TOKEN')
    g = Github(token)
    
    try:
        user = g.get_user(username)
        since = datetime.now() - timedelta(days=days)
        
        commit_count = 0
        weekend_commits = 0
        
        for repo in user.get_repos():
            try:
                commits = repo.get_commits(author=user, since=since)
                for commit in commits:
                    commit_count += 1
                    # Check if weekend commit
                    if commit.commit.author.date.weekday() in [5, 6]:
                        weekend_commits += 1
            except:
                continue
        
        return commit_count, weekend_commits
    except Exception as e:
        print(f"Error fetching commits: {e}")
        return 0, 0

def get_activity_level(commit_count, weekend_commits):
    """Determine activity level based on commits"""
    weekend_ratio = weekend_commits / commit_count if commit_count > 0 else 0
    
    # Check for weekend warrior pattern
    if commit_count >= 5 and weekend_ratio > 0.6:
        return 'weekend_warrior'
    
    if commit_count >= 15:
        return 'very_active'
    elif commit_count >= 7:
        return 'active'
    elif commit_count >= 3:
        return 'moderate'
    elif commit_count >= 1:
        return 'low'
    else:
        return 'inactive'

def get_meme_for_activity(activity_level, previous_meme=None):
    """Get a random meme for the activity level, avoiding recent repeats"""
    memes = MEME_COLLECTIONS.get(activity_level, MEME_COLLECTIONS['moderate'])
    
    # Avoid repeating the previous meme if possible
    if previous_meme and previous_meme in memes and len(memes) > 1:
        available_memes = [m for m in memes if m != previous_meme]
        return random.choice(available_memes)
    
    return random.choice(memes)

def update_readme_meme(meme_url, commit_count, activity_level):
    """Update README.md with new meme"""
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Activity messages
    activity_messages = {
        'very_active': f'🔥 On fire! {commit_count} commits this week!',
        'active': f'💪 Solid work! {commit_count} commits this week!',
        'moderate': f'📊 Steady progress - {commit_count} commits this week.',
        'low': f'🌱 Growing slowly - {commit_count} commits this week.',
        'inactive': '😴 Taking a break? Time to code!',
        'weekend_warrior': f'🎮 Weekend coder! {commit_count} commits this week!'
    }
    
    message = activity_messages.get(activity_level, 'Coding...')
    
    # Find and replace meme section
    meme_section = f'''### 😂 Productivity Meme

<div align="center">
  <img src="{meme_url}" alt="Commit Meme" width="500"/>
</div>

*{message}*'''
    
    # Replace the meme section
    import re
    pattern = r'### 😂 Productivity Meme.*?\*\*?.*?\*'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, meme_section, content, flags=re.DOTALL)
    else:
        # If section doesn't exist, add it after GitHub Statistics
        stats_end = content.find('---\n\n###  Featured Projects')
        if stats_end != -1:
            content = content[:stats_end] + f'\n{meme_section}\n\n---\n\n' + content[stats_end+5:]
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    username = 'Spamziesagcan'
    
    # Get commit data
    commit_count, weekend_commits = get_commit_count(username)
    print(f"Commits in last 7 days: {commit_count} (Weekend: {weekend_commits})")
    
    # Determine activity level
    activity_level = get_activity_level(commit_count, weekend_commits)
    print(f"Activity level: {activity_level}")
    
    # Get appropriate meme
    meme_url = get_meme_for_activity(activity_level)
    print(f"Selected meme: {meme_url}")
    
    # Update README
    update_readme_meme(meme_url, commit_count, activity_level)
    print("README updated successfully!")

if __name__ == '__main__':
    main()
