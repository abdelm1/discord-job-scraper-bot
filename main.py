import discord
from discord.ext import commands, tasks
from discord import app_commands
import serpapi
import json
import logging
from datetime import datetime
import requests
import typing  # Import the typing module

# Configure logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s]: %(message)s',
    level=logging.INFO
)
with open("config.json", "r") as f:
    config = json.load(f)


TOKEN = config["TOKEN"]
api_key = config["api_key"]
api_key_google = config["api_key_google"]
cse_id = config["cse_id"]
FORUM_CHANNEL_ID = config["FORUM_CHANNEL_ID"]
allowed_user_ids = config["allowed_user_ids"]
JOBS_FILE_PATH = config["JOBS_FILE_PATH"]
LOCATION = config["LOCATION"]
QUERY = config["QUERY"]
DEFAULT_LINK_METHOD = config["DEFAULT_LINK_METHOD"]

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), help_command=None)
client = serpapi.Client(api_key=api_key)

def get_first_link(api_key, cse_id, query):
    base_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key_google}&cx={cse_id}"

    response = requests.get(base_url)
    data = response.json()
    if "items" in data and data["items"]:
        first_link = data["items"][0]["link"]
        return first_link
    else:
        return None

def get_first_link_api(job_id):
    results = client.search({
        'engine': 'google_jobs_listing',
        'q': job_id,
    })
    print(results)
    print("+++++++++++++++++++++")
    # Extract and return the link for applying from the apply_options
    if 'apply_options' in results and results['apply_options']:
        return results['apply_options'][0]['link']
    else:
        # If apply options are not available, return the Google search URL
        return results['search_metadata']['google_jobs_listing_url']



DEFAULT_LINK_METHOD = 'api'  # Default method for retrieving job links

def get_job_link(job_id, query_details,method=DEFAULT_LINK_METHOD):
    if method == 'api':
        return get_first_link_api(job_id)
    elif method == 'scraping':
        return get_first_link(api_key, cse_id, query_details)
    else:
        return None


@bot.event
async def on_ready():
    logging.info(f'We have logged in as {bot.user}')
    guild_id = discord.Object(id=1203466857571549184)
    # bot.tree.copy_global_to(guild=guild_id)
    await bot.tree.sync(guild=guild_id)
    
    job_scrape.start()


METHODS = ['api', 'scraping']



@bot.hybrid_command(name='set_link_method', description='Set the method for job links (api or scraping).')
async def set_link_method(ctx, method: str):
    if ctx.author.id in allowed_user_ids:
        global DEFAULT_LINK_METHOD
        if method.lower() in METHODS:
            DEFAULT_LINK_METHOD = method.lower()
            await ctx.send(f"Default job link method set to: {DEFAULT_LINK_METHOD}")
        else:
            await ctx.send("Invalid method. Please use 'api' or 'scraping'.")
    else:
        await ctx.send("You are not authorized to use this command.")


@bot.hybrid_command(name='update_location', description='Update the location of the search results.')
async def update_location(ctx, new_location: str):
    if ctx.author.id in allowed_user_ids:
        global LOCATION
        LOCATION = new_location
        logging.info(f"Location updated to {new_location}")
        await ctx.send(f"Location updated to {new_location}")
    else:
        await ctx.send("You are not authorized to use this command.")


@bot.hybrid_command(name='update_query', description='Update the query of the search results.')
async def update_query(ctx, new_query: str):
    if ctx.author.id in allowed_user_ids:
        global QUERY
        QUERY = new_query
        logging.info(f"Query updated to {new_query}")
        await ctx.send(f"Query updated to {new_query}")
    else:
        await ctx.send("You are not authorized to use this command.")

@bot.hybrid_command(name='help', description='Show current settings information.')
async def help(ctx):
    embed = discord.Embed(title='Current Settings Information', color=discord.Color.green())
    embed.add_field(name='Location', value=LOCATION if LOCATION else 'Default (Texas)', inline=False)
    embed.add_field(name='Query', value=QUERY if QUERY else 'Default (Junior Data Analyst)', inline=False)
    await ctx.send(embed=embed)

@tasks.loop(minutes=5)
async def job_scrape():
    try:
        with open(JOBS_FILE_PATH, 'r') as file:
            JOB_ID_SET = set(json.load(file))
    except FileNotFoundError:
        JOB_ID_SET = set()

    location = LOCATION if LOCATION else 'Texas'
    query = QUERY if QUERY else 'Junior Data Analyst'

    results = client.search({
        'engine': 'google_jobs',
        'q': query,
        'location': location,
        'chips': 'date_posted:today'
    })
    logging.info('-----------------------')
    for job_result in results.get('jobs_results', []):
        job_id = job_result.get('job_id')
        if job_id not in JOB_ID_SET:
            JOB_ID_SET.add(job_id)

            title = job_result.get('title', 'N/A')
            logging.info(f"New Job Found: {title}")

            description = job_result.get('description', 'N/A')[:4092]
            if len(description) >= 4092:
                description = description + '...'

            posted_at = job_result.get('detected_extensions', {}).get('posted_at', 'N/A')
            schedule_type = job_result.get('detected_extensions', {}).get('schedule_type', 'N/A')

            thumbnail_url = job_result.get('thumbnail', '')
            company = job_result.get('company_name')
            via = job_result.get('via')

            description_snippet = job_result.get('description', '')[:2380]
            query_details = f'intext:"{description_snippet}"'
            
            related_links = job_result.get('related_links', [])

            job_link = get_job_link(job_id,query_details)
            if job_link is None:
                logging.warning(f"Failed to retrieve job link for {job_id}")
                continue
            link = job_link if job_link else related_links[0].get('link', 'N/A') if related_links else 'N/A'

            embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
            embed.add_field(name='Posted At', value=posted_at, inline=True)
            embed.add_field(name='Schedule Type', value=schedule_type, inline=True)

            view=discord.ui.View()
            button=discord.ui.Button(label='Offer Link',url=link)
            view.add_item(button)

            embed.set_thumbnail(url=thumbnail_url)

            target_channel = bot.get_channel(FORUM_CHANNEL_ID)
            if target_channel and isinstance(target_channel, discord.ForumChannel):
                content = f"{company} {via}"
                created_thread = await target_channel.create_thread(name=title,embed=embed,content=content,view=view)
            else:
                logging.error(f"Error: Forum Channel with ID {FORUM_CHANNEL_ID} not found or is not a valid forum channel.")

    with open(JOBS_FILE_PATH, 'w') as file:
        json.dump(list(JOB_ID_SET), file)

bot.run(TOKEN)
