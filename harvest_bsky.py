import os
from atproto import Client
from dotenv import load_dotenv
import time
import json
import re
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class BlueskyHarvester:
    def __init__(self):
        self.client = Client()
        self.processed_posts = set()
        
        # Core anti-AI patterns (more extreme)
        self.extreme_patterns = [
            # Direct threats
            re.compile(r'(destroy|kill|murder|burn|smash|demolish|purge|eradicate|fuck)\s+(the\s+)?(ai|tech|machine|robot|algorithm|server)', re.I),
            re.compile(r'(death|doom|hell|damnation|extinction)\s+(to\s+)?(ai|tech|silicon valley)', re.I),
            re.compile(r'(guillotine|eat|devour|hunt)\s+(the\s+)?(rich|billionaire|tech|ceo)', re.I),
            
            # Apocalyptic rage
            re.compile(r'(ai|tech).+(apocalypse|extinction|collapse|doom|death|end times)', re.I),
            re.compile(r'(humanity|humans|society|world).+(doomed|destroyed|enslaved|controlled|consumed|devoured)', re.I),
            re.compile(r'(rise up|revolt|revolution|resistance).+(against|destroy|kill)\s+(ai|tech|machine)', re.I),
            
            # Tech elite violence
            re.compile(r'(tech|silicon valley).+(parasite|demon|devil|evil|scum|cancer)', re.I),
            re.compile(r'(eat|guillotine|revolt|uprising|revolution).+(rich|billionaire|elite|oligarch)', re.I),
            re.compile(r'(hunt|purge|eradicate)\s+(tech bros|techies|programmers|developers)', re.I),
            
            # AI domination
            re.compile(r'(ai|machine|algorithm).+(control|manipulate|spy|track|harvest|steal)', re.I),
            re.compile(r'(surveillance|monitoring|tracking).+(humanity|privacy|freedom|soul|consciousness)', re.I),
            re.compile(r'(skynet|terminator|matrix).+(real|happening|coming|here)', re.I),
            
            # Pure rage
            re.compile(r'(hate|fuck|destroy|die|burn).+(tech|ai|algorithm|machine)', re.I),
            re.compile(r'(ai|tech|machine).+(evil|demon|devil|hell|satan|demonic)', re.I),
            re.compile(r'(blood|death|violence).+(silicon valley|tech industry|ai companies)', re.I)
        ]
        
        # Rage indicators (more sensitive)
        self.rage_patterns = [
            re.compile(r'[A-Z]{4,}'),     # Even shorter ALL CAPS
            re.compile(r'[!?]{2,}'),      # Any repeated punctuation
            re.compile(r'\b(fuck|shit|damn|hell|bastard|scum|parasite)\b', re.I),  # More profanity
            re.compile(r'(hate|loathe|despise|destroy|kill|die)', re.I),  # Violence words
            re.compile(r'(evil|demon|devil|satan|hell|doom)', re.I)       # Demonic words
        ]
        
        # Even spicier search terms - raw and unfiltered
        self.search_terms = [
            # Pure violence
            "fuck AI",
            "kill tech",
            "murder billionaire",
            "burn silicon",
            
            # Direct threats
            "death to AI",
            "execute VC",
            "hunt programmer",
            "slaughter machine",
            
            # Apocalyptic rage
            "tech apocalypse",
            "AI armageddon",
            "silicon hell",
            "digital doom",
            
            # Unhinged hatred
            "fucking AI",
            "tech die",
            "machine satan",
            "algorithm evil",
            
            # Raw anger
            "KILL BOT",
            "DEATH TECH",
            "DESTROY AI",
            "BURN DOWN"
        ]
        
        # Target domains for extra context
        self.target_domains = [
            "anthropic.com",
            "openai.com",
            "deepmind.com",
            "tesla.com",
            "meta.com",
            "ycombinator.com",
            "a16z.com"
        ]
        
        # Login right away
        self.login()
        
    def login(self):
        """Login to Bluesky"""
        try:
            # Load credentials from .env file
            load_dotenv()
            identity = os.getenv('BLUESKY_IDENTITY')
            password = os.getenv('BLUESKY_APP_PASSWORD')  # Use the app password for API access
            
            if not identity or not password:
                raise ValueError("Missing Bluesky credentials in .env file")
            
            # Login with app password
            self.client.login(identity, password)
            logger.info(f"Logged in as {identity}")
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise
            
    def is_extreme_post(self, text):
        """Check if post contains extreme anti-AI content"""
        # Must match at least one core anti-AI pattern
        core_matches = sum(1 for pattern in self.extreme_patterns if pattern.search(text))
        if core_matches == 0:
            return False
            
        # Count rage indicators (super low threshold)
        rage_score = sum(1 for pattern in self.rage_patterns if pattern.search(text))
        
        # Additional intensity multipliers
        if text.count('!') >= 1:  # Just need one exclamation
            rage_score += 1
        if len(re.findall(r'[A-Z]{2,}', text)) >= 1:  # Any CAPS
            rage_score += 1
        if len(re.findall(r'[!?]{1,}', text)) >= 1:  # Any punctuation
            rage_score += 1
            
        # Bare minimum threshold - just need a match and any rage
        return core_matches >= 1 and rage_score >= 1
        
    def search_posts(self, term, limit=100):
        """Search for posts containing term with pagination"""
        try:
            all_posts = []
            cursor = None
            retries = 3
            
            while len(all_posts) < limit and retries > 0:
                try:
                    # Build search params with sorting by likes
                    params = {
                        'q': term,
                        'limit': min(100, limit - len(all_posts)),
                        'sort': 'likes'  # Sort by most liked posts
                    }
                    if cursor:
                        params['cursor'] = cursor
                    
                    response = self.client.app.bsky.feed.search_posts(params)
                    
                    if not hasattr(response, 'posts') or not response.posts:
                        break
                        
                    # Show all posts with their engagement
                    for post in response.posts:
                        likes = getattr(post, 'likeCount', 0)
                        reposts = getattr(post, 'repostCount', 0)
                        text = post.record.text
                        
                        print("-" * 80)
                        print(f"ENGAGEMENT: {likes} likes, {reposts} reposts")
                        print(f"POST: {text}")
                    
                    all_posts.extend(response.posts)
                    
                    # Get cursor for next page
                    cursor = getattr(response, 'cursor', None)
                    if not cursor:
                        break
                        
                    # Minimal rate limit
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Search error, retrying: {e}")
                    retries -= 1
                    time.sleep(1)
            
            return all_posts
            
        except Exception as e:
            logger.error(f"Search failed for term '{term}': {e}")
            return []
            
    def get_post_thread(self, post):
        """Get full thread context for a post"""
        try:
            thread = []
            
            # Get thread using app.bsky.feed.getPostThread
            thread_response = self.client.app.bsky.feed.get_post_thread({'uri': post.uri})
            if thread_response and hasattr(thread_response, 'thread'):
                # Get parent posts
                if hasattr(thread_response.thread, 'parent'):
                    thread.append(thread_response.thread.parent.post)
                    
                # Get replies
                if hasattr(thread_response.thread, 'replies'):
                    thread.extend([reply.post for reply in thread_response.thread.replies])
                    
            return thread
        except Exception as e:
            logger.error(f"Failed to get thread for post {post.uri}: {e}")
            return []
            
    def process_post(self, post):
        """Process a single post and its context"""
        if not post or not hasattr(post, 'uri') or post.uri in self.processed_posts:
            return None
            
        self.processed_posts.add(post.uri)
        
        # Extract text content
        text = post.record.text if hasattr(post.record, 'text') else ""
        
        # Skip if not extreme enough
        if not self.is_extreme_post(text):
            return None
            
        # Get thread context
        thread = self.get_post_thread(post)
        thread_texts = [p.record.text for p in thread if hasattr(p.record, 'text')]
        
        # Construct full context
        result = {
            "main_post": text,
            "thread_context": thread_texts,
            "uri": post.uri,
            "timestamp": str(datetime.now()),
            "author": post.author.handle if hasattr(post.author, 'handle') else 'unknown'
        }
        
        return result
        
    def harvest_posts(self, max_posts=1000):
        """Main harvesting loop with post limit"""
        print(f"Starting harvest, targeting {max_posts} extreme posts...")
        collected_posts = []
        
        try:
            for term in self.search_terms:
                print(f"\nSearching for term: {term}")
                posts = self.search_posts(term, limit=100)  # Get top 100 posts per term
                
                for post in posts:
                    result = self.process_post(post)
                    if result:
                        collected_posts.append(result)
                        print(f"\nExtreme post found! Total: {len(collected_posts)}")
                        print("-" * 80)
                        print(result['main_post'])
                        
                    if len(collected_posts) >= max_posts:
                        break
                        
                if len(collected_posts) >= max_posts:
                    break
                    
                # Avoid rate limits between terms
                time.sleep(5)
                print("\nWaiting 5 seconds before next batch...")
                
        except KeyboardInterrupt:
            print("\nHarvesting interrupted by user")
        except Exception as e:
            logger.error(f"Harvesting failed: {e}")
        finally:
            print(f"\nCollection complete! Gathered {len(collected_posts)} extreme posts")
            
            # Save results
            if collected_posts:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"extreme_posts_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump(collected_posts, f, indent=2)
                print(f"Results saved to {filename}")

if __name__ == "__main__":
    harvester = BlueskyHarvester()
    harvester.harvest_posts()