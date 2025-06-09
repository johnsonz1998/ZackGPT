# ZackGPT Web Search Setup Guide

ZackGPT now includes powerful web search capabilities that allow the AI to access real-time information from the internet. This guide will help you configure and use these features.

## Features

- **Real-time web search** - Access current information, news, and data
- **Multiple search engines** - SerpAPI, Google Custom Search, and DuckDuckGo fallback
- **Smart detection** - Automatically detects when web search is needed
- **Webpage content extraction** - Can fetch and read webpage content
- **Integrated responses** - Search results are seamlessly integrated into AI responses

## Configuration

### 1. Environment Variables

Add these variables to your `.env` file:

```bash
# Web Search Configuration
WEB_SEARCH_ENABLED=true
WEB_SEARCH_MAX_RESULTS=5
WEB_SEARCH_TIMEOUT=10
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Search API Keys (choose one or more)
SERPAPI_KEY=your_serpapi_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
```

### 2. Search Engine Setup

#### Option 1: SerpAPI (Recommended)

1. Sign up for a free account at [serpapi.com](https://serpapi.com)
2. Get your API key from the dashboard
3. Add it to your `.env` file as `SERPAPI_KEY`
4. Free tier includes 100 searches/month

#### Option 2: Google Custom Search

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable the Custom Search API
3. Create credentials (API key)
4. Set up a Custom Search Engine at [cse.google.com](https://cse.google.com)
5. Add both `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` to your `.env` file
6. Free tier includes 100 searches/day

#### Option 3: DuckDuckGo (Fallback)

- No API key required
- Automatically available as fallback
- Limited results but always works

### 3. Install Dependencies

```bash
pip install requests beautifulsoup4 lxml
```

Or update from requirements.txt:

```bash
pip install -r requirements.txt
```

## Usage

### Automatic Detection

ZackGPT automatically detects when web search is needed based on your questions:

- **Current events**: "What's happening in the news today?"
- **Real-time data**: "What's the weather like?", "Bitcoin price"
- **Recent information**: "Latest updates on AI"
- **Specific searches**: "Search for Python tutorials"

### Explicit Search Commands

You can also explicitly request web searches:

- "Search for [topic]"
- "Look up [information]"
- "Find information about [subject]"
- "What is [recent topic]"

### Example Queries

```
❯ What's the latest news about AI?
❯ Search for Python web scraping tutorials
❯ What's the weather like in New York today?
❯ Who won the latest sports championship?
❯ Look up the current Bitcoin price
❯ Tell me about recent developments in quantum computing
```

## Search Behavior

### Smart Detection Triggers

The system looks for these patterns to decide when to search:

1. **Time indicators**: today, now, current, latest, recent
2. **News keywords**: news, happening, events, updates
3. **Search triggers**: search for, look up, tell me about
4. **Real-time data**: weather, stocks, cryptocurrency, scores
5. **Current year references**: 2024, 2023, etc.

### Search Process

1. **Query extraction** - Extracts the actual search terms from your question
2. **Multi-engine search** - Tries search engines in order of preference
3. **Result formatting** - Formats results for AI consumption
4. **Integration** - Adds search results to the AI's context
5. **Response generation** - AI provides comprehensive answer with current data

## Troubleshooting

### Common Issues

1. **"Web search is disabled"**
   - Check that `WEB_SEARCH_ENABLED=true` in your `.env` file
   - Restart the application after changing environment variables

2. **"No search results found"**
   - Verify your API keys are correct
   - Check your internet connection
   - Try a different search query

3. **API key errors**
   - Make sure API keys are active and have remaining quota
   - Check that the keys are properly formatted in `.env`

4. **Import errors**
   - Install missing dependencies: `pip install requests beautifulsoup4 lxml`
   - Update requirements: `pip install -r requirements.txt`

### Debug Mode

Enable debug mode to see detailed search information:

```bash
DEBUG_MODE=true
```

This will show:
- Search query extraction
- Which search engines are tried
- Search results and formatting
- Integration with AI responses

## API Rate Limits

### SerpAPI
- Free: 100 searches/month
- Paid plans available for higher limits

### Google Custom Search
- Free: 100 searches/day
- Paid plans available for higher limits

### DuckDuckGo
- No rate limits (fallback service)
- Limited result quality

## Security Notes

- API keys are stored in environment variables (never in code)
- All web requests use standard User-Agent headers
- Search results are processed and filtered before AI consumption
- No personal data is sent to search APIs

## Advanced Configuration

### Custom User Agent

```bash
USER_AGENT=YourCustomBot/1.0 (+https://yoursite.com)
```

### Search Result Limits

```bash
WEB_SEARCH_MAX_RESULTS=10  # More results (uses more tokens)
```

### Timeout Settings

```bash
WEB_SEARCH_TIMEOUT=15  # Longer timeout for slow connections
```

## Integration with Other Features

- **Memory System**: Search results can be saved to memory for future reference
- **Conversation Context**: Search results are integrated into conversation flow
- **Prompt Evolution**: Search usage helps improve prompt effectiveness
- **Multi-modal**: Can search for and analyze different types of content

## Support

If you encounter issues:

1. Check the logs for detailed error messages
2. Verify your API keys and configuration
3. Test with simple queries first
4. Check the GitHub issues for known problems

Happy searching! 🔍 