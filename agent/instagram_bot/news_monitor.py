import feedparser
import requests
import logging
from datetime import datetime, date
from typing import List, Dict, Any
import asyncio
from openai import OpenAI
from .config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class NewsMonitor:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.feeds = [
            "https://www.rbc.ua/static/rss/ukrnet.strong.ukr.rss.xml",
            # "https://www.liga.net/newsua/top/rss.xml",
            # "https://nv.ua/ukr/rss/2365.xml",
            "https://www.5.ua/dv/rss",
        ]
    
    def get_ukraine_holidays(self) -> List[Dict[str, Any]]:
        """Get public holidays in Ukraine for today"""
        try:
            today =  date.today()
            # Using a public holidays API - this is a placeholder, you may need to find a suitable API
            # For now, we'll return empty list and focus on RSS feeds
            return []
        except Exception as e:
            logger.error(f"Error fetching Ukraine holidays: {e}")
            return []
    
    def get_rss_news(self, feed_url: str) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            news_items = []
            
            today = date.today()
            yesterday = today.replace(day=today.day-1)
            
            for entry in feed.entries:
                # Parse publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = date(*entry.published_parsed[:3])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = date(*entry.updated_parsed[:3])
                
                # Filter today's and yesterday's news
                if pub_date and (pub_date == today or pub_date == yesterday):
                    news_items.append({
                        'title': entry.title,
                        'link': entry.link,
                        'summary': getattr(entry, 'summary', ''),
                        'published': entry.get('published', ''),
                        'source': feed_url,
                        'when': 'today' if pub_date == today else 'yesterday'
                    })
                
            return news_items
        except Exception as e:
            logger.error(f"Error fetching RSS from {feed_url}: {e}")
            return []
    
    def collect_all_news(self) -> List[Dict[str, Any]]:
        """Collect news from all sources"""
        all_news = []
        
        # Get holidays
        holidays = self.get_ukraine_holidays()
        all_news.extend(holidays)
        
        # Get RSS feeds
        for feed_url in self.feeds:
            rss_news = self.get_rss_news(feed_url)
            all_news.extend(rss_news)
        
        print(all_news)
        logger.info(f"Collected {len(all_news)} news items for today")
        return all_news
    
    def categorize_news(self, news_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize news using OpenAI nano model"""
        if not news_items:
            return {'stressful': [], 'lightweight': [], 'unrelated': []}
        
        try:
            chunk_size = 10
            news_chunks = [news_items[i:i + chunk_size] for i in range(0, len(news_items), chunk_size)]
            
            all_analysis = []
            
            for chunk in news_chunks:
                # Prepare news text for analysis
                news_text = "\n".join([f"- *{item['when']}* - {item['title']}: {item.get('summary', '')}" for item in chunk])
                
                prompt = f"""
                Analyze the following news and categorize each item:

                {news_text}

                Categorize each news item as:
                1. STRESSFUL - war-related, tragic, disasters, people are in grief, national tragedy. It should impact a lot of people and make them feel bad, other news should be categorized as UNRELATED.
                2. LIGHTWEIGHT - viral social media content, memes, funny quotes or videos, entertainment news, sports highlights, positive community events, cultural phenomena - content that brings joy, laughter or positive emotions and has significant social media engagement. Other news should be categorized as UNRELATED.
                3. UNRELATED - other unrelated news (most of the news should be categorized as UNRELATED)

                Stressful event indicators:
                - Mass casualties or major loss of life
                - National tragedies or disasters
                - Deaths of prominent public figures
                - Major terrorist attacks
                - Catastrophic events affecting many people
                
                Not a stressful event indicators:
                - Some drone attacks
                - Some natural disasters
                - Economic issues or market fluctuations
                - Minor incidents or accidents
                - Ongoing war developments (if not major new casualties)
                - Business or administrative issues

                Lightweigt news indicators:
                - Humor
                - Entertainment
                - Sports
                - Positive community events
                - Culture
                - It should be really impactful, funny or important.

                Don't include unrelated news in the response.

                Respond in JSON format:
                {{
                    "analysis": [
                        {{"title": "news title", "category": "STRESSFUL/LIGHTWEIGHT", "reason": "brief explanation", "when": "today/yesterday"}}
                    ]
                }}
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # nano model
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                
                import json
                print(response.choices[0].message.content)
                chunk_analysis = json.loads(response.choices[0].message.content)
                all_analysis.extend(chunk_analysis['analysis'])
            
            # Group news by category
            categorized = {'stressful': [], 'lightweight': [], 'unrelated': []}
            
            for i, item in enumerate(news_items):
                if i < len(all_analysis):
                    category = all_analysis[i]['category'].lower()
                    if category in categorized:
                        item['analysis'] = all_analysis[i]
                        categorized[category].append(item)
            
            return categorized
            
        except Exception as e:
            logger.error(f"Error categorizing news: {e}")
            return {'stressful': [], 'lightweight': [], 'unrelated': []}
    
    def analyze_content_fit(self, lightweight_news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze if lightweight news fits content plan"""
        if not lightweight_news:
            return []
        
        try:
            # Read content plan
            with open('data/content_plan.md', 'r', encoding='utf-8') as f:
                content_plan = f.read()
            
            news_text = "\n".join([f"- {item['title']}: {item.get('summary', '')}" for item in lightweight_news])
            
            prompt = f"""
            Content Plan:
            {content_plan}
            
            Lightweight News:
            {news_text}
            
            For each news item, analyze if it fits our Instagram content strategy and could be used for a story.
            Consider: brand alignment, audience interest, storytelling potential.
            It should be a really impactful news, that will be interesting for our audience. Other news should be ignored with fits_content = false.
            
            Respond in JSON format:
            {{
                "recommendations": [
                    {{
                        "title": "news title",
                        "fits_content": true/false,
                        "story_idea": "specific story concept if applicable",
                        "reason": "why it fits or doesn't fit"
                    }}
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            
            import json
            print(response.choices[0].message.content)
            recommendations = json.loads(response.choices[0].message.content)
            
            # Filter only news that fits content plan
            fitting_news = []
            for i, item in enumerate(lightweight_news):
                if i < len(recommendations['recommendations']):
                    rec = recommendations['recommendations'][i]
                    if rec.get('fits_content', False):
                        item['recommendation'] = rec
                        fitting_news.append(item)
            
            return fitting_news
            
        except Exception as e:
            logger.error(f"Error analyzing content fit: {e}")
            return []

    def analyze_mourning_day(self, stressful_news: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze if stressful news indicates a mourning day that requires refraining from posting"""
        if not stressful_news:
            return {
                'is_mourning_day': False,
                'reason': 'No stressful news today',
                'recommendation': 'safe_to_post',
                'details': 'No concerning events detected'
            }
        
        try:
            # Prepare news text for analysis
            news_text = "\n".join([f"- *{item['when']}* - {item['title']}: {item.get('summary', '')}" for item in stressful_news])
            
            prompt = f"""
            Analyze the following stressful news to determine if today should be treated as a mourning day:

            {news_text}

            Determine if this is a MOURNING DAY (people are in grief, national tragedy) or just REGULAR STRESSFUL NEWS (life goes on).
            Consider that it's an ongoing war, so it's not a mourning day if there are some drone attacks, rocket strikes and even some casualties.
            Few casualties are not a mourning day, unfortunately it's a part of the war and everyone is used to it.
            Mass attack is a mourning day.
            If there was a mass attack yesterday night, or today - it's a mourning day. If there was a mass attack yesterday day - it's a regular stressful news.

            MOURNING DAY indicators:
            - Mass casualties or major loss of life (only if it's a lot of people)
            - National tragedies or disasters (not just some events, but a lot of people are affected and it's a big deal, maybe died, or it's a big event that will be remembered for a long time)
            - Deaths of prominent public figures
            - Major terrorist attacks
            - Catastrophic events affecting many people

            REGULAR STRESSFUL NEWS indicators:
            - Political tensions or conflicts
            - Some drone attacks
            - Some natural disasters
            - Economic issues or market fluctuations
            - Minor incidents or accidents
            - Ongoing war developments (if not major new casualties)
            - Business or administrative issues
            - Events where life continues normally

            Respond in JSON format:
            {{
                "is_mourning_day": true/false,
                "reason": "detailed explanation of the decision",
                "recommendation": "refrain_from_posting" or "safe_to_post",
                "details": "specific guidance for content strategy",
                "key_events": ["list of most significant events that influenced the decision"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing mourning day: {e}")
            return {
                'is_mourning_day': False,
                'reason': f'Error in analysis: {e}',
                'recommendation': 'safe_to_post',
                'details': 'Defaulting to safe posting due to analysis error',
                'key_events': []
            }

async def news_monitoring_task(reply_message, reply_photo):
    """Main news monitoring task"""
    logger.info("Starting news monitoring task...")
    
    monitor = NewsMonitor()
    
    # Collect news
    news_items = monitor.collect_all_news()
    
    if not news_items:
        logger.info("No news items found for today")
        return
    
    # Categorize news
    categorized = monitor.categorize_news(news_items)
    
    # Handle stressful news
    if categorized['stressful']:
        # Analyze if this is a mourning day
        mourning_analysis = monitor.analyze_mourning_day(categorized['stressful'])
        
        stressful_count = len(categorized['stressful'])
        stressful_titles = [item['title'] for item in categorized['stressful'][:3]]  # Show max 3
        
        if mourning_analysis['is_mourning_day']:
            # Mourning day - refrain from posting
            message = f"🖤 **ДЕНЬ ЖАЛОБИ** ({stressful_count} подій)\n\n"
            for title in stressful_titles:
                message += f"• {title}\n"
            
            if stressful_count > 3:
                message += f"• ... та ще {stressful_count - 3} подій\n"
            
            message += f"\n📋 **Аналіз:** {mourning_analysis['reason']}\n\n"
            message += "🚫 **РЕКОМЕНДАЦІЯ: УТРИМАТИСЬ ВІД ПУБЛІКАЦІЙ**\n"
            message += "• Відкладіть заплановані пости на інший день\n"
            message += f"• {mourning_analysis['details']}"
            
            if mourning_analysis.get('key_events'):
                message += f"\n\n🔍 **Ключові події:**\n"
                for event in mourning_analysis['key_events'][:3]:
                    message += f"• {event}\n"
        else:
            # Regular stressful news - life goes on
            message = f"⚠️ **СТРЕСОВІ НОВИНИ** ({stressful_count} подій)\n\n"
            for title in stressful_titles:
                message += f"• {title}\n"
            
            if stressful_count > 3:
                message += f"• ... та ще {stressful_count - 3} подій\n"
            
            message += f"\n📋 **Аналіз:** {mourning_analysis['reason']}\n\n"
            message += "✅ **РЕКОМЕНДАЦІЯ: МОЖНА ПУБЛІКУВАТИ**\n"
            message += "• Життя триває, можна публікувати контент\n"
            message += f"• {mourning_analysis['details']}"

            if mourning_analysis.get('key_events'):
                message += f"\n\n🔍 **Ключові події:**\n"
                for event in mourning_analysis['key_events'][:3]:
                    message += f"• {event}\n"
        
        await reply_message(message)
    
    # Handle lightweight news that fits content plan
    fitting_news = monitor.analyze_content_fit(categorized['lightweight'])
    
    if fitting_news:
        message = f"💡 **МОЖЛИВОСТІ ДЛЯ КОНТЕНТУ** ({len(fitting_news)} ідей)\n\n"
        
        for item in fitting_news:
            rec = item.get('recommendation', {})
            message += f"📰 **{item['title']}**\n"
            message += f"💭 Ідея: {rec.get('story_idea', 'Не вказано')}\n"
            message += f"🔗 {item.get('link', '')}\n\n"
        
        await reply_message(message)
    
    logger.info(f"News monitoring completed: {len(categorized['stressful'])} stressful, {len(fitting_news)} content opportunities")
