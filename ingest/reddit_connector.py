import os
import asyncio
import asyncpg
import praw
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import json
import logging
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RedditMention:
    source: str = "reddit"
    source_id: str = ""
    author: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    created_at: datetime = None
    metrics: Dict[str, Any] = None
    lang: str = "en"
    entities: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}
        if self.entities is None:
            self.entities = {}

class RedditConnector:
    """Reddit connector for ingesting posts and comments from crypto/meme subreddits"""
    
    def __init__(self):
        # Only initialize Reddit client if credentials are available
        if os.getenv("REDDIT_CLIENT_ID"):
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT", "NarrativeScanner/1.0")
            )
        else:
            self.reddit = None
        self.db_url = os.getenv("DATABASE_URL")
        
        # Target subreddits for crypto and meme content
        self.subreddits = [
            "solana",
            "SolanaMemeCoin", 
            "CryptoMoonShots",
            "CryptoCurrency",
            "altcoin",
            "SatoshiStreetBets",
            "memecoins",
            "dogecoin",
            "SafeMoon",
            "shitcoin"
        ]
        
    async def connect_db(self):
        """Establish database connection"""
        return await asyncpg.connect(self.db_url)
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from Reddit text"""
        entities = {
            "hashtags": [],
            "tickers": [],
            "urls": [],
            "mentions": []
        }
        
        if not text:
            return entities
            
        words = text.split()
        for word in words:
            # Extract ticker symbols (e.g., $SOL, $WIF)
            if word.startswith("$") and len(word) > 1:
                ticker = word[1:].upper().strip(".,!?")
                if ticker.isalpha() and len(ticker) <= 10:
                    entities["tickers"].append(ticker)
            
            # Extract URLs
            if word.startswith(("http://", "https://")):
                entities["urls"].append(word)
            
            # Extract user mentions
            if word.startswith("u/") and len(word) > 2:
                entities["mentions"].append(word[2:])
                
        return entities
    
    def process_submission(self, submission) -> RedditMention:
        """Process a Reddit submission into our format"""
        # Combine title and selftext for full content
        text = submission.title
        if hasattr(submission, 'selftext') and submission.selftext:
            text += " " + submission.selftext
            
        mention = RedditMention(
            source_id=f"submission_{submission.id}",
            author=str(submission.author) if submission.author else None,
            text=text,
            url=f"https://reddit.com{submission.permalink}",
            created_at=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
            metrics={
                "score": submission.score,
                "upvote_ratio": getattr(submission, 'upvote_ratio', None),
                "num_comments": submission.num_comments,
                "gilded": getattr(submission, 'gilded', 0),
                "subreddit": str(submission.subreddit)
            },
            entities=self.extract_entities(text)
        )
        
        return mention
    
    def process_comment(self, comment) -> RedditMention:
        """Process a Reddit comment into our format"""
        mention = RedditMention(
            source_id=f"comment_{comment.id}",
            author=str(comment.author) if comment.author else None,
            text=comment.body,
            url=f"https://reddit.com{comment.permalink}",
            created_at=datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
            metrics={
                "score": comment.score,
                "gilded": getattr(comment, 'gilded', 0),
                "is_submitter": getattr(comment, 'is_submitter', False),
                "subreddit": str(comment.subreddit)
            },
            entities=self.extract_entities(comment.body)
        )
        
        return mention
    
    async def save_mention(self, conn, mention: RedditMention):
        """Save mention to database with conflict handling"""
        try:
            await conn.execute("""
                INSERT INTO mention (source, source_id, author, text, url, created_at, metrics, lang, entities)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (source, source_id) DO NOTHING
            """, 
            mention.source,
            mention.source_id, 
            mention.author,
            mention.text,
            mention.url,
            mention.created_at,
            json.dumps(mention.metrics),
            mention.lang,
            json.dumps(mention.entities)
            )
            logger.debug(f"Saved mention: {mention.source_id}")
        except Exception as e:
            logger.error(f"Error saving mention {mention.source_id}: {e}")
    
    async def ingest_subreddit_posts(self, subreddit_name: str, limit: int = 100):
        """Ingest recent posts from a specific subreddit"""
        logger.info(f"Ingesting posts from r/{subreddit_name}")
        
        conn = await self.connect_db()
        mentions_saved = 0
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get hot posts
            for submission in subreddit.hot(limit=limit):
                mention = self.process_submission(submission)
                await self.save_mention(conn, mention)
                mentions_saved += 1
                
                # Also get top comments from this submission
                submission.comments.replace_more(limit=0)  # Remove "more comments"
                for comment in submission.comments.list()[:10]:  # Top 10 comments
                    if hasattr(comment, 'body') and comment.body not in ['[deleted]', '[removed]']:
                        comment_mention = self.process_comment(comment)
                        await self.save_mention(conn, comment_mention)
                        mentions_saved += 1
                        
        except Exception as e:
            logger.error(f"Error ingesting r/{subreddit_name}: {e}")
        finally:
            await conn.close()
            
        logger.info(f"Saved {mentions_saved} mentions from r/{subreddit_name}")
        return mentions_saved
    
    async def ingest_all_subreddits(self, limit_per_subreddit: int = 50):
        """Ingest posts from all configured subreddits"""
        logger.info("Starting Reddit ingestion for all subreddits")
        total_mentions = 0
        
        for subreddit_name in self.subreddits:
            try:
                count = await self.ingest_subreddit_posts(subreddit_name, limit_per_subreddit)
                total_mentions += count
                # Small delay to be respectful to Reddit's API
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Failed to ingest r/{subreddit_name}: {e}")
                continue
                
        logger.info(f"Reddit ingestion complete. Total mentions: {total_mentions}")
        return total_mentions

async def main():
    """Main function for testing the Reddit connector"""
    connector = RedditConnector()
    await connector.ingest_all_subreddits(limit_per_subreddit=25)

if __name__ == "__main__":
    asyncio.run(main())