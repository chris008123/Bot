#Main Discord bot module for the Code Quality Evaluation Bot.
#Handles all Discord interactions, commands, and event listeners.
import requests
from bs4 import BeautifulSoup

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from io import BytesIO

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Cog, command, has_role, has_permissions

import config
from database import Database, Submission, WeeklyRanking
from analyzer import CodeAnalyzer



# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# BOT INITIALIZATION
# ============================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=config.COMMAND_PREFIX,
    intents=intents,
    help_command=commands.DefaultHelpCommand()
)

# Global database and analyzer instances
db = Database()
analyzer = CodeAnalyzer()


# ============================================================================
# EVENT HANDLERS
# ============================================================================

@bot.event
async def on_ready():
    """Bot startup event."""
    logger.info(f'{bot.user} has connected to Discord')
    logger.info(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Start background tasks
    try:
        weekly_rankings_task.start()
        rule_monitor_task.start()
        daily_announcement_task.start()  
        daily_programming_news.start()
        logger.info('Background tasks started successfully')
    except RuntimeError:
        # Tasks already running
        pass


@bot.event
async def on_message(message: discord.Message):
    """Handle incoming messages for rule monitoring."""
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Check for rule violations
    await monitor_message_rules(message)
    
    # Process commands
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """Handle command errors gracefully."""
    logger.error(f'Command error in {ctx.command}: {error}')
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'❌ You lack permissions to use this command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'❌ Missing argument: {error.param.name}')
    elif isinstance(error, commands.CommandNotFound):
        pass  # Silently ignore unknown commands
    else:
        await ctx.send(f'❌ An error occurred: {str(error)[:100]}')


# ============================================================================
# SUBMISSION HANDLING
# ============================================================================

@bot.command(name='submit')
@commands.cooldown(1, 60, commands.BucketType.user)
async def submit_code(ctx: commands.Context):
    """
    Submit code for quality evaluation.
    
    Usage:
        !submit [with code in reply or attachment]
    
    Supports:
        - Code blocks: ```python ... ```
        - File attachments: .py, .js, .java, etc.
        - GitHub URLs: (coming soon)
    """
    code = None
    language = "python"
    
    try:
        # Check for attachments
        if ctx.message.attachments:
            file = ctx.message.attachments[0]
            
            # Check file size
            if file.size > config.MAX_FILE_SIZE:
                await ctx.send(f'❌ File too large. Max size: {config.MAX_FILE_SIZE / 1024 / 1024:.0f}MB')
                return
            
            # Validate file extension
            file_ext = file.filename.lower().rsplit('.', 1)[-1]
            if f'.{file_ext}' not in config.SUPPORTED_EXTENSIONS:
                await ctx.send(f'❌ Unsupported file type. Supported: {", ".join(config.SUPPORTED_EXTENSIONS)}')
                return
            
            # Detect language from file extension
            language = _detect_language(f'.{file_ext}')
            
            # Download file
            file_bytes = await file.read()
            code = file_bytes.decode('utf-8', errors='ignore')
        
        # Check for code blocks in message content
        elif '```' in ctx.message.content:
            extracted = CodeAnalyzer.extract_python_code(ctx.message.content)
            if extracted:
                code = extracted
                language = "python"
        
        # Check if it's a reply
        elif ctx.message.reference:
            referenced_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if '```' in referenced_msg.content:
                extracted = CodeAnalyzer.extract_python_code(referenced_msg.content)
                if extracted:
                    code = extracted
                    language = "python"
        
        if not code:
            await ctx.send(
                '❌ No code found. Please submit code using one of these methods:\n'
                '1. Attach a code file\n'
                '2. Use code blocks: ```python\\ncode\\n```\n'
                '3. Reply to a message with code blocks'
            )
            return
        
        # Check code size
        if len(code) > config.MAX_CODE_SIZE:
            await ctx.send(f'❌ Code too large. Max size: {config.MAX_CODE_SIZE} characters')
            return
        
        # Show analyzing message
        analyzing_msg = await ctx.send('🔍 Analyzing your code...')
        
        # Run analysis with timeout
        try:
            score, feedback = await asyncio.wait_for(
                asyncio.to_thread(analyzer.analyze, code, language),
                timeout=config.ANALYSIS_TIMEOUT
            )
        except asyncio.TimeoutError:
            await analyzing_msg.edit(content='⏱️ Analysis timed out. Code may be too complex.')
            return
        
        # Store in database
        submission_id = db.add_submission(
            user_id=ctx.author.id,
            code=code,
            language=language,
            score=score,
            feedback=feedback
        )
        
        # Generate feedback embed
        embed = _create_score_embed(ctx.author, score, feedback, language)
        
        # Edit analyzing message with results
        await analyzing_msg.edit(content=None, embed=embed)
        
        logger.info(f'Submission from {ctx.author} (ID: {submission_id}): Score {score}')
        
    except asyncio.TimeoutError:
        await ctx.send('⏱️ Analysis timed out. Code may be too complex.')
    except ValueError as e:
        logger.warning(f'Invalid input in submission: {e}')
        await ctx.send(f'❌ Invalid input: {str(e)[:100]}')
    except Exception as e:
        logger.error(f'Error processing submission: {e}', exc_info=True)
        await ctx.send(f'❌ Error analyzing code: An unexpected error occurred.')


@bot.command(name='mystats')
async def user_stats(ctx: commands.Context):
    """Show your submission history and statistics."""
    try:
        submissions = db.get_user_submissions(ctx.author.id)
        
        if not submissions:
            await ctx.send('📊 You haven\'t submitted any code yet!')
            return
        
        avg_score = db.get_user_avg_score(ctx.author.id)
        
        # Create embed
        embed = discord.Embed(
            title=f'📊 Stats for {ctx.author.name}',
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name='📈 Statistics',
            value=(
                f'**Total Submissions:** {len(submissions)}\n'
                f'**Average Score:** {avg_score:.1f}/100\n'
                f'**Latest Score:** {submissions[0].score}/100'
            ),
            inline=False
        )
        
        # Show recent submissions
        recent_text = '\n'.join([
            f'• **{sub.score}/100** - {sub.timestamp.strftime("%Y-%m-%d %H:%M")} ({sub.language})'
            for sub in submissions[:5]
        ])
        
        embed.add_field(
            name='🕐 Recent Submissions',
            value=recent_text or 'None',
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f'Error in mystats: {e}')
        await ctx.send(f'❌ Error retrieving stats: {str(e)[:100]}')


@bot.command(name='leaderboard')
async def show_leaderboard(ctx: commands.Context):
    """Display the top 10 code quality rankings."""
    try:
        rankings = db.get_latest_rankings()
        
        if not rankings:
            await ctx.send('📊 No rankings available yet. Check back after the first week!')
            return
        
        # Create embed
        embed = discord.Embed(
            title='🏆 Weekly Code Quality Leaderboard',
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        embed.description = 'Top performers based on code quality analysis'
        
        leaderboard_text = ''
        # Batch fetch users to reduce API calls (max 10 rankings shown)
        user_ids = [ranking.user_id for ranking in rankings[:10]]
        users = {}
        
        for user_id in user_ids:
            try:
                user = await bot.fetch_user(user_id)
                users[user_id] = user.name
            except discord.NotFound:
                users[user_id] = f'User {user_id}'
            except Exception as e:
                logger.warning(f'Error fetching user {user_id}: {e}')
                users[user_id] = f'User {user_id}'
        
        for ranking in rankings[:10]:
            username = users.get(ranking.user_id, f'User {ranking.user_id}')
            medal = ['🥇', '🥈', '🥉'][ranking.rank - 1] if ranking.rank <= 3 else f'{ranking.rank}.'
            
            leaderboard_text += (
                f'{medal} **{username}** - '
                f'{ranking.avg_score:.1f}/100 ({ranking.submission_count} submissions)\n'
            )
        
        embed.add_field(
            name='Rankings',
            value=leaderboard_text or 'No data',
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f'Error in leaderboard: {e}', exc_info=True)
        await ctx.send('❌ Error retrieving leaderboard.')


@bot.command(name='feedback')
async def get_feedback(ctx: commands.Context, submission_id: Optional[int] = None):
    """
    Get detailed feedback on a submission.
    Uses most recent submission if ID not specified.
    """
    try:
        if submission_id:
            submission = db.get_submission(submission_id)
            if not submission or submission.user_id != ctx.author.id:
                await ctx.send('❌ Submission not found or you don\'t have permission to view it.')
                return
        else:
            submissions = db.get_user_submissions(ctx.author.id, limit=1)
            if not submissions:
                await ctx.send('❌ You haven\'t submitted any code yet.')
                return
            submission = submissions[0]
        
        # Create detailed feedback embed
        embed = discord.Embed(
            title=f'📋 Detailed Feedback - Score: {submission.score}/100',
            color=_score_to_color(submission.score),
            timestamp=submission.timestamp
        )
        
        feedback = submission.feedback
        
        # Analysis results
        analysis = feedback.get('analysis', {})
        
        analysis_text = _format_analysis(analysis)
        if analysis_text:
            embed.add_field(name='🔍 Analysis Results', value=analysis_text, inline=False)
        
        # Deductions
        deductions = feedback.get('deductions', [])
        if deductions:
            deductions_text = '\n'.join([
                f'• **{d["reason"]}** (-{d["amount"]} pts)'
                for d in deductions
            ])
            embed.add_field(name='❌ Deductions', value=deductions_text, inline=False)
        
        # Bonuses
        bonuses = feedback.get('bonuses', [])
        if bonuses:
            bonuses_text = '\n'.join([
                f'• **{b["reason"]}** (+{b["amount"]} pts)'
                for b in bonuses
            ])
            embed.add_field(name='✅ Bonuses', value=bonuses_text, inline=False)
        
        embed.set_footer(text=f'Language: {submission.language}')
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f'Error in feedback: {e}')
        await ctx.send(f'❌ Error retrieving feedback: {str(e)[:100]}')


# ============================================================================
# ADMIN COMMANDS
# ============================================================================

@bot.command(name='violations')
@commands.check(lambda ctx: ctx.author.id in config.ADMIN_USER_IDS)
async def check_violations(ctx: commands.Context, user_id: Optional[int] = None, hours: int = 24):
    """
    [ADMIN] Check rule violations.
    
    Usage:
        !violations <user_id> [hours]
        !violations --recent [hours]
    """
    try:
        violations = []
        
        if user_id:
            violations = db.get_user_violations(user_id, unresolved_only=True)
        else:
            violations = db.get_recent_violations(hours=hours)
        
        if not violations:
            await ctx.send(f'✅ No violations found in the last {hours} hours.')
            return
        
        embed = discord.Embed(
            title='⚠️ Recent Rule Violations',
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        # Batch fetch users
        user_ids = list(set([v['user_id'] for v in violations[:10]]))
        users = {}
        
        for uid in user_ids:
            try:
                user = await bot.fetch_user(uid)
                users[uid] = user.name
            except discord.NotFound:
                users[uid] = f'User {uid}'
            except Exception as e:
                logger.warning(f'Error fetching user {uid}: {e}')
                users[uid] = f'User {uid}'
        
        for v in violations[:10]:
            username = users.get(v['user_id'], f'User {v["user_id"]}')
            
            embed.add_field(
                name=f'{username} - {v["type"]}',
                value=f'{v["message"]}\n*{v["timestamp"].strftime("%Y-%m-%d %H:%M:%S")}*',
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f'Error in violations: {e}', exc_info=True)
        await ctx.send('❌ Error retrieving violations.')


@bot.command(name='dbstats')
@commands.check(lambda ctx: ctx.author.id in config.ADMIN_USER_IDS)
async def database_stats(ctx: commands.Context):
    """[ADMIN] Show database statistics."""
    try:
        stats = db.get_database_stats()
        
        embed = discord.Embed(
            title='📊 Database Statistics',
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name='Total Submissions', value=stats['total_submissions'])
        embed.add_field(name='Active Users', value=stats['total_users'])
        embed.add_field(name='Total Violations', value=stats['total_violations'])
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f'Error in dbstats: {e}')
        await ctx.send(f'❌ Error: {str(e)[:100]}')


@bot.command(name='forceranking')
@commands.check(lambda ctx: ctx.author.id in config.ADMIN_USER_IDS)
async def force_ranking(ctx: commands.Context):
    """[ADMIN] Manually generate weekly rankings."""
    try:
        await ctx.send('⏳ Generating rankings...')
        rankings = db.generate_weekly_rankings()
        await ctx.send(f'✅ Rankings generated! Top user: {rankings[0].user_id if rankings else "N/A"}')
    except Exception as e:
        logger.error(f'Error in forceranking: {e}')
        await ctx.send(f'❌ Error: {str(e)[:100]}')


@bot.command(name='help_admin')
@commands.check(lambda ctx: ctx.author.id in config.ADMIN_USER_IDS)
async def admin_help(ctx: commands.Context):
    """[ADMIN] Show admin commands."""
    embed = discord.Embed(
        title='🔧 Admin Commands',
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name='!violations [user_id] [hours]',
        value='Check rule violations',
        inline=False
    )
    embed.add_field(
        name='!dbstats',
        value='Show database statistics',
        inline=False
    )
    embed.add_field(
        name='!forceranking',
        value='Manually generate weekly rankings',
        inline=False
    )
    embed.add_field(
        name='Configuration',
        value=f'Admins: {len(config.ADMIN_USER_IDS)}\nLeaderboard Size: {config.LEADERBOARD_SIZE}',
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="clearall")
@commands.check(lambda ctx: ctx.author.id in config.ADMIN_USER_IDS)
@commands.bot_has_permissions(manage_messages=True)
async def clear_channel(ctx: commands.Context):
    """
    [ADMIN] Clears all messages in the current channel.
    Messages older than 14 days are deleted one-by-one.
    """

    await ctx.send(
        "⚠️ **WARNING** ⚠️\n"
        "This will delete **ALL messages** in this channel.\n"
        "Type `CONFIRM` within 10 seconds to proceed."
    )

    def check(m):
        return (
            m.author == ctx.author and
            m.channel == ctx.channel and
            m.content == "CONFIRM"
        )

    try:
        await bot.wait_for("message", timeout=10.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ Channel clear cancelled.")
        return

    await ctx.send("🧹 Clearing channel… this may take a moment.")

    deleted = 0

    async for message in ctx.channel.history(limit=None):
        try:
            await message.delete()
            deleted += 1
            await asyncio.sleep(0.5)  # prevent rate limits
        except discord.Forbidden:
            await ctx.send("❌ Missing permissions to delete messages.")
            return
        except Exception:
            pass

    await ctx.send(f"✅ Channel cleared. **{deleted} messages deleted.**")

    logger.warning(
        f"Channel #{ctx.channel.name} cleared by {ctx.author} ({ctx.author.id})"
    )


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

@tasks.loop(hours=1)
async def weekly_rankings_task():
    """
    Periodic task to generate weekly rankings.
    Runs at configured day/time.
    """
    now = datetime.now()
    
    # Check if it's the right day and time
    if (now.weekday() == config.RANKING_DAY and 
        now.hour == config.RANKING_HOUR):
        
        try:
            logger.info('Generating weekly rankings...')
            rankings = db.generate_weekly_rankings()
            
            # Post to announcements channel
            if config.ANNOUNCEMENTS_CHANNEL_ID:
                channel = bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
                if channel:
                    embed = await _create_leaderboard_embed(rankings)
                    await channel.send(
                        '🏆 **Weekly Code Quality Rankings** 🏆',
                        embed=embed
                    )
            
            logger.info(f'Rankings generated with {len(rankings)} users')
        
        except Exception as e:
            logger.error(f'Error in ranking task: {e}')


@tasks.loop(hours=1)
async def rule_monitor_task():
    """
    Periodic task to check for and report violations to admins.
    """
    try:
        violations = db.get_recent_violations(hours=1)
        
        if violations and config.ADMIN_USER_IDS:
            # Get first admin for DM
            admin_id = config.ADMIN_USER_IDS[0]
            
            try:
                admin = await bot.fetch_user(admin_id)
            except discord.NotFound:
                logger.warning(f'Admin user {admin_id} not found')
                return
            except Exception as e:
                logger.warning(f'Error fetching admin user: {e}')
                return
            
            if admin:
                embed = discord.Embed(
                    title='⚠️ Rule Violations Report',
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                
                # Batch fetch violating users
                user_ids = list(set([v['user_id'] for v in violations[:5]]))
                users = {}
                
                for uid in user_ids:
                    try:
                        user = await bot.fetch_user(uid)
                        users[uid] = user.name
                    except discord.NotFound:
                        users[uid] = f'User {uid}'
                    except Exception as e:
                        logger.warning(f'Error fetching user {uid}: {e}')
                        users[uid] = f'User {uid}'
                
                for v in violations[:5]:
                    username = users.get(v['user_id'], f'User {v["user_id"]}')
                    
                    embed.add_field(
                        name=f'{username} - {v["type"]}',
                        value=v['message'][:100] if v['message'] else 'N/A',
                        inline=False
                    )
                
                await admin.send(embed=embed)
    
    except Exception as e:
        logger.error(f'Error in rule monitor task: {e}', exc_info=True)

# For making annoucements 
@tasks.loop(minutes=1)
async def daily_announcement_task():
    """
    Sends a message every day at 08:00.
    """
    now = datetime.now()

    if now.hour == 8 and now.minute == 0:
        channel = bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)

        if channel:
            await channel.send(
                "🌅 **Good morning everyone!**\n"
                "Keep coding, keep improving 🚀 ~SL \n 😈 and learn to make money as \n"
                "soon as possible ~Xris""li brx frpplw wr qrwklqj brx duh glvwudfwhg eb hyhubwklqj" 
                
            )

        # Prevent duplicate sends within the same minute
        await asyncio.sleep(60)

@tasks.loop(minutes=1)
async def daily_programming_news():
    now = datetime.now()

    if now.hour == 8 and now.minute == 5:
        channel = bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)

        if not channel:
            return

        try:
            news = fetch_programming_news(limit=5)

            if not news:
                await channel.send("📰 No programming news found today.")
                return

            message = "📰 **Daily Programming News**\n\n"
            for i, (title, link) in enumerate(news, 1):
                message += f"**{i}. {title}**\n{link}\n\n"

            await channel.send(message)

            # Prevent duplicate sends
            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"News fetch error: {e}")


# ============================================================================
# RULE MONITORING
# ============================================================================

async def monitor_message_rules(message: discord.Message):
    """Check messages for rule violations."""
    content = message.content.lower()
    
    # Check for banned words
    for banned in config.BANNED_WORDS:
        if banned.lower() in content:
            db.add_violation(
                message.author.id,
                'banned_word',
                f'Message contained banned word/phrase: {banned}'
            )
            logger.warning(f'Banned word detected from {message.author}')
            break
    
    # Check for spam (excessive caps)
    if len(message.content) > 10:
        caps_ratio = sum(1 for c in message.content if c.isupper()) / len(message.content)
        if caps_ratio > config.SPAM_CONFIG['caps_lock_threshold']:
            db.add_violation(
                message.author.id,
                'spam',
                f'Excessive caps lock: {caps_ratio:.0%}'
            )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def fetch_programming_news(limit=5):
    """
    Fetch recent programming news from Hacker News.
    """
    url = "https://news.ycombinator.com/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    rows = soup.select(".athing")[:limit]

    for row in rows:
        title = row.select_one(".titleline a").text
        link = row.select_one(".titleline a")["href"]
        articles.append((title, link))

    return articles


def _detect_language(filename: str) -> str:
    """Detect programming language from file extension."""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
    }
    return ext_map.get(filename.lower(), 'unknown')


def _score_to_color(score: int) -> discord.Color:
    """Convert score to color for embeds."""
    if score >= 90:
        return discord.Color.green()
    elif score >= 75:
        return discord.Color.blue()
    elif score >= 60:
        return discord.Color.gold()
    elif score >= 40:
        return discord.Color.orange()
    else:
        return discord.Color.red()


def _create_score_embed(
    author: discord.Member,
    score: int,
    feedback: Dict,
    language: str
) -> discord.Embed:
    """Create a formatted score embed."""
    embed = discord.Embed(
        title=f'✅ Code Analysis Complete',
        color=_score_to_color(score),
        timestamp=datetime.now()
    )
    
    # Score
    score_text = f'**{score}/100**'
    if score >= 90:
        score_text += ' 🌟 Excellent!'
    elif score >= 75:
        score_text += ' ✅ Great!'
    elif score >= 60:
        score_text += ' 👍 Good!'
    elif score >= 40:
        score_text += ' ⚠️ Needs Work'
    else:
        score_text += ' ❌ Major Issues'
    
    embed.add_field(name='📊 Score', value=score_text, inline=False)
    
    # Language
    embed.add_field(name='💻 Language', value=language.capitalize(), inline=True)
    
    # Summary of deductions/bonuses
    deductions = feedback.get('deductions', [])
    bonuses = feedback.get('bonuses', [])
    
    if deductions:
        deductions_list = ', '.join([d['reason'][:30] for d in deductions[:3]])
        embed.add_field(name='❌ Issues Found', value=deductions_list, inline=False)
    
    if bonuses:
        bonuses_list = ', '.join([b['reason'][:30] for b in bonuses])
        embed.add_field(name='✅ Bonuses', value=bonuses_list, inline=False)
    
    embed.add_field(
        name='📋 More Info',
        value='Use `!feedback` to see detailed analysis',
        inline=False
    )
    
    embed.set_author(name=author.name, icon_url=author.avatar)
    
    return embed


def _format_analysis(analysis: Dict) -> str:
    """Format analysis results for display."""
    text = ''
    
    if 'syntax' in analysis:
        text += f"**Syntax:** {analysis['syntax']}\n"
    
    if 'pylint' in analysis and isinstance(analysis['pylint'], dict):
        text += f"**PEP8:** {analysis['pylint']}\n"
    
    if 'complexity' in analysis:
        if isinstance(analysis['complexity'], (int, float)):
            text += f"**Cyclomatic Complexity:** {analysis['complexity']}\n"
        else:
            text += f"**Complexity:** {analysis['complexity']}\n"
    
    if 'security' in analysis and isinstance(analysis['security'], dict):
        text += f"**Security:** {analysis['security'].get('issue_count', 0)} issues\n"
    
    return text.strip()


async def _create_leaderboard_embed(rankings: List[WeeklyRanking]) -> discord.Embed:
    embed = discord.Embed(
        title='🏆 Top Code Quality Performers',
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    
    leaderboard_text = ''
    for ranking in rankings[:10]:
        user = await bot.fetch_user(ranking.user_id)
        username = user.name if user else f'User {ranking.user_id}'
        
        medal = ['🥇', '🥈', '🥉'][ranking.rank - 1] if ranking.rank <= 3 else f'{ranking.rank}.'
        
        leaderboard_text += (
            f'{medal} **{username}** - '
            f'{ranking.avg_score:.1f}/100 ({ranking.submission_count} subs)\n'
        )
    
    embed.description = leaderboard_text or 'No data'
    return embed


@tasks.loop(minutes=10)
async def keep_alive_task():
    print(f"Keep-alive ping at {datetime.now()}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Prevent duplicate starts if bot reconnects
    if not keep_alive_task.is_running():
        keep_alive_task.start()

bot.run(config.DISCORD_TOKEN)