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
            # Violent threats
            re.compile(r'(destroy|kill|murder|burn|smash|demolish|purge|eradicate)\s+(the\s+)?(ai|tech|machine|robot|algorithm|server)', re.I),
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
        
        # Even spicier search terms with wildcards
        self.search_terms = [
            # Direct violence
            "guillotine*",
            "eat the rich*",
            "destroy* AI*",
            "burn* silicon*",
            
            # Apocalyptic
            "AI* apocalypse*",
            "machine* uprising*",
            "tech* doom*",
            "extinction* AI*",
            
            # Tech elite
            "techbro* die*",
            "valley* parasites*",
            "oligarch* death*",
            "vc* guillotine*",
            
            # Unhinged rage
            "AI* demon*",
            "machine* hell*",
            "tech* satan*",
            "algorithm* evil*",
            
            # Resistance
            "rise* against* AI*",
            "destroy* machine*",
            "human* resistance*",
            "tech* revolution*"
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
            
        # Count rage indicators (even lower threshold)
        rage_score = sum(1 for pattern in self.rage_patterns if pattern.search(text))
        
        # Additional intensity multipliers
        if text.count('!') >= 2:  # Just need a couple exclamations
            rage_score += 1
        if len(re.findall(r'[A-Z]{3,}', text)) >= 1:  # Any CAPS section
            rage_score += 1
        if len(re.findall(r'[!?]{2,}', text)) >= 1:  # Any punctuation cluster
            rage_score += 1
            
        # Super low threshold - just need a hint of rage
        return core_matches >= 1 and rage_score >= 2
        
    def search_posts(self, term, limit=100):
        """Search for posts containing term with pagination"""
        try:
            all_posts = []
            cursor = None
            
            while len(all_posts) < limit:
                # Build search params
                params = {
                    'q': term,
                    'limit': min(50, limit - len(all_posts))  # Max 50 per request
                }
                if cursor:
                    params['cursor'] = cursor
                
                response = self.client.app.bsky.feed.search_posts(params)
                
                if not hasattr(response, 'posts') or not response.posts:
                    break
                    
                # Filter for high engagement posts
                engaged_posts = [
                    post for post in response.posts 
                    if (getattr(post, 'likeCount', 0) + getattr(post, 'repostCount', 0)) > 5
                ]
                
                if engaged_posts:
                    print(f"\nFound {len(engaged_posts)} spicy posts for '{term}':")
                    for post in engaged_posts[:3]:  # Show sample
                        print("-" * 60)
                        print(post.record.text)
                
                all_posts.extend(engaged_posts)
                
                # Get cursor for next page
                cursor = getattr(response, 'cursor', None)
                if not cursor:
                    break
                    
                # Avoid rate limits
                time.sleep(0.5)
            
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
                posts = self.search_posts(term)
                
                for post in posts:
                    result = self.process_post(post)
                    if result:
                        collected_posts.append(result)
                        print(f"\nExtreme post found! Total: {len(collected_posts)}")
                        print("-" * 60)
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