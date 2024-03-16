# Discord Job Scraper Bot

## Overview

The Discord Job Scraper Bot is a Python-based Discord bot designed to automate job search tasks within Discord communities. It continuously scans the web for new job listings based on user-defined criteria and posts them in designated Discord channels. This bot is particularly useful for keeping community members updated with the latest job opportunities relevant to their interests.

## Features

- **Automated Job Search**: The bot automatically searches for job listings at predefined intervals, ensuring users stay updated with the latest opportunities without manual intervention.
- **Flexible Query Settings**: Users can easily update job search parameters, including location and query keywords, empowering them to tailor job searches to their preferences.
- **Authorization System**: Certain commands are restricted to authorized users, ensuring security and control over bot functionality.
- **Multiple Posting Methods**: The bot supports multiple methods for retrieving job links, including API integration and web scraping, allowing for robust and reliable job listing retrieval.
- **Structured Posting Format**: Job listings are presented in a structured and visually appealing format, including essential details such as job title, description, company information, and application links.
- **Threaded Posting**: Job listings are posted as threads in designated Discord channels, facilitating organized discussions and interactions around specific job opportunities.
- **Persistence and Deduplication**: The bot maintains a record of posted job IDs to prevent duplicate postings and ensure a streamlined user experience.

## Technologies Used

- **Python**: The bot is developed using the Python programming language for its versatility and extensive library support.
- **Discord.py**: The bot utilizes the Discord.py library for interacting with the Discord API and creating Discord bots.
- **SerpApi**: Integration with SerpApi enables web scraping and retrieval of job listings from search engine results.
- **JSON**: Configuration parameters are stored in a JSON file for easy management and customization.
- **Requests**: The Requests library is used for making HTTP requests to external APIs.

## Setup and Deployment

1. **Clone the Repository**: Clone the repository to your local machine using Git:

   ```
   git clone https://github.com/abdelm1/discord-job-scraper-bot.git
   ```

2. **Install Dependencies**: Navigate to the project directory and install the required dependencies using pip:

   ```
   cd discord-job-scraper-bot
   pip install serpapi
   pip install discord
   pip install logging
   ```

3. **Configure the Bot**: Edit the `config.json` file to include your bot token, API keys, channel IDs, and other configurable parameters.

4. **Run the Bot**: Run the bot script using Python:

   ```
   python main.py
   ```

5. **Invite the Bot**: Invite the bot to your Discord server using the OAuth2 URL generated from the Discord Developer Portal.

## Usage

- Use Discord commands to interact with the bot and update job search settings.
- Regularly check the designated Discord channels for new job listings posted by the bot.
- Review and apply to relevant job opportunities shared by the bot within your Discord community.
