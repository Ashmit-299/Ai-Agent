# app/agent.py
import json
import os
import random
import time
import html
from typing import List, Dict, Optional
from pathlib import Path

class RLAgent:
    """
    Simple Q-learning agent with:
      - Discrete state key based on authenticity bucket + tag count
      - Small discrete action set
      - Methods to observe feedback (uses provided reward when available)
      - Pretraining method to ingest labeled examples to seed Q-values
    """

    def __init__(self, state_path: str = "agent_state.json"):
        self.state_path = state_path
        # Q-table: { state_key: { action: value } }
        self.q: Dict[str, Dict[str, float]] = {}
        self.epsilon = 0.2
        self.alpha = 0.3
        self.gamma = 0.9
        # Actions: keep small & interpretable
        self.actions = ["nop", "boost_tag", "add_suggested_tag"]
        # basic in-memory store of content metadata
        self.contents: Dict[str, Dict] = {}
        self.recent_rewards: List[float] = []
        # replay buffer (simple)
        self.replay: List[Dict] = []
        self.max_replay = 2000

        # load state if exists
        if os.path.exists(self.state_path):
            try:
                # Validate state path to prevent path traversal
                safe_path = Path(self.state_path).resolve()
                current_dir = Path.cwd().resolve()
                if not str(safe_path).startswith(str(current_dir)):
                    raise ValueError("State file must be within the application's working directory.")
                
                if not str(safe_path).endswith('.json'):
                    raise ValueError("State file must have .json extension")
                
                with open(safe_path, "r", encoding="utf-8") as f:
                    st = json.load(f)
                self.q = st.get("q", {})
                self.epsilon = st.get("epsilon", self.epsilon)
            except (json.JSONDecodeError, IOError, KeyError, ValueError) as e:
                print(f"Warning: Could not load agent state: {e}")
                self.q = {}
        
        # Sync with existing database content
        self.sync_with_database()

    # -------------------------
    # State and helper methods
    # -------------------------
    def _state_key(self, content_id: str) -> str:
        """Generate secure state key from content metadata"""
        # Sanitize content_id to prevent injection
        safe_content_id = html.escape(str(content_id))
        info = self.contents.get(safe_content_id, {"tags": [], "authenticity": 0.5})
        auth_bucket = max(0, min(5, int(info.get("authenticity", 0.5) * 5)))  # Clamp to 0-5
        tags_len = max(0, min(10, len(info.get("tags", []))))  # Clamp to 0-10
        return f"auth_{auth_bucket}_t{tags_len}"

    def register_content(self, content_id: str, tags: List[str], authenticity: float):
        """Record content metadata and ensure a Q entry exists for its state."""
        # Validate and sanitize inputs
        safe_content_id = html.escape(str(content_id))
        safe_tags = [html.escape(str(tag)) for tag in tags if tag]
        safe_authenticity = max(0.0, min(1.0, float(authenticity)))
        
        self.contents[safe_content_id] = {"tags": safe_tags, "authenticity": safe_authenticity}
        sk = self._state_key(safe_content_id)
        if sk not in self.q:
            self.q[sk] = {a: 0.0 for a in self.actions}
            self._persist()

    # -------------------------
    # Action / recommendation
    # -------------------------
    def recommend_tags(self, content_id: str) -> Dict:
        """Return recommended tags + the action taken (for observability)."""
        safe_content_id = html.escape(str(content_id))
        
        # Authorization: Only allow access to registered content
        if safe_content_id not in self.contents:
            raise ValueError("Content not found or access denied")
        
        sk = self._state_key(safe_content_id)
        if sk not in self.q:
            self.q[sk] = {a: 0.0 for a in self.actions}
        
        # epsilon-greedy with validation
        if random.random() < max(0.0, min(1.0, self.epsilon)):
            action = random.choice(self.actions)
        else:
            action = max(self.q[sk].items(), key=lambda x: x[1])[0]

        info = self.contents[safe_content_id]
        tags = list(info.get("tags", []))

        if action == "boost_tag" and tags:
            # Keep existing tags for boost action
            pass
        elif action == "add_suggested_tag":
            auth_score = info.get('authenticity', 0.5)
            suggested = f"ai_like_{int(auth_score * 100)}"
            if suggested not in tags:
                tags = tags + [suggested]
        
        # Store the action taken for this content
        last_action_key = f"{safe_content_id}_last_action"
        setattr(self, last_action_key, action)
        
        return {"tags": tags, "action_taken": action}

    # -------------------------
    # Learning
    # -------------------------
    def observe_feedback(self, content_id: str, event_type: str, watch_time_ms: int, reward: Optional[float] = None, user_feedback: Optional[float] = None):
        """
        Observe feedback for a content. Prefer `user_feedback` if provided (explicit user rating).
        reward param is accepted for backwards compatibility (routes computed reward earlier).
        """
        # Sanitize inputs
        safe_content_id = html.escape(str(content_id))
        safe_event_type = html.escape(str(event_type))
        safe_watch_time = max(0, min(7200000, int(watch_time_ms)))  # Clamp to reasonable range
        
        # Determine reward: user_feedback > reward > computed reward
        r = 0.0
        if user_feedback is not None:
            try: # Ensure user_feedback is a valid float and clamp it
                r = max(-2.0, min(2.0, float(user_feedback)))  # Clamp reward
            except (ValueError, TypeError):
                r = 0.0
        elif reward is not None:
            try:
                r = max(-2.0, min(2.0, float(reward)))  # Clamp reward
            except (ValueError, TypeError):
                r = 0.0
        else:
            # fallback heuristic based on event_type and watch_time
            if safe_event_type == "view":
                r = min(1.0, max(0.0, safe_watch_time / 30000.0))
            elif safe_event_type == "like":
                r = 1.0
            elif safe_event_type == "share":
                r = 2.0
            elif safe_event_type == "dislike":
                r = -1.0

        # keep recent rewards for metrics
        self.recent_rewards.append(r)
        if len(self.recent_rewards) > 1000:
            self.recent_rewards.pop(0)

        # Build a training tuple: (s,a,r,s')
        sk = self._state_key(safe_content_id)
        if sk not in self.q:
            self.q[sk] = {a: 0.0 for a in self.actions}

        # Store last action taken for this content (better than inferring)
        if safe_content_id not in self.contents:
            return  # Cannot update without registered content
        
        # Use stored last action or default to 'nop'
        last_action_key = f"{safe_content_id}_last_action"
        a = getattr(self, last_action_key, 'nop')
        
        # Next state could change based on content updates (simplified: same state)
        sk2 = sk
        max_q_next = max(self.q[sk2].values()) if self.q.get(sk2) else 0.0
        old = self.q[sk][a]
        # Q-learning update with bounds checking
        new_q_value = old + self.alpha * (r + self.gamma * max_q_next - old)
        self.q[sk][a] = max(-100.0, min(100.0, new_q_value))  # Prevent overflow

        # Add to replay buffer
        self.replay.append({"s": sk, "a": a, "r": r, "s2": sk2, "ts": time.time()})
        if len(self.replay) > self.max_replay:
            self.replay.pop(0)

        # Occasionally persist
        if random.random() < 0.05:
            self._persist()

    def batch_update_from_replay(self, batches: int = 1, batch_size: int = 64):
        """Perform extra Q updates by sampling the replay buffer."""
        if not self.replay:
            return
        for _ in range(batches):
            sample = random.sample(self.replay, min(batch_size, len(self.replay)))
            for ex in sample:
                s, a, r, s2 = ex["s"], ex["a"], ex["r"], ex["s2"]
                if s not in self.q:
                    self.q[s] = {act: 0.0 for act in self.actions}
                if s2 not in self.q:
                    self.q[s2] = {act: 0.0 for act in self.actions}
                max_q_next = max(self.q[s2].values())
                old = self.q[s][a]
                new_q_value = old + self.alpha * (r + self.gamma * max_q_next - old)
                self.q[s][a] = max(-100.0, min(100.0, new_q_value))  # Add bounds checking
        self._persist()

    # -------------------------
    # Pretraining (seed)
    # -------------------------
    def pretrain_from_examples(self, examples: List[Dict]):
        """
        Accepts a list of examples, each example is a dict:
          { "authenticity": float(0..1), "tags": [...], "reward": float }
        This will derive state keys and update Q-values so the agent is pre-seeded.
        """
        if not isinstance(examples, list):
            raise ValueError("Examples must be a list")
        
        # Authorization: Limit pretraining to prevent abuse
        if len(examples) > 1000:
            raise ValueError("Too many examples for pretraining (max 1000)")
        
        for i, ex in enumerate(examples):
            try:
                if not isinstance(ex, dict):
                    continue
                
                # Validate required fields
                required_fields = ['authenticity', 'tags', 'reward']
                for field in required_fields:
                    if field not in ex:
                        raise ValueError(f"Missing required field: {field}")
                
                auth = max(0.0, min(1.0, float(ex.get("authenticity", 0.5))))
                tags = [html.escape(str(tag)) for tag in (ex.get("tags", []) or []) if tag]
                reward = max(-2.0, min(2.0, float(ex.get("reward", 0.0))))
                
                # create synthetic content_id for state hashing
                temp_id = f"pre_{int(auth*100)}_{len(tags)}_{i}"
                self.contents[temp_id] = {"tags": tags, "authenticity": auth}
                sk = self._state_key(temp_id)
                if sk not in self.q:
                    self.q[sk] = {a: 0.0 for a in self.actions}
                
                # seed each action a bit using reward (favor add_suggested_tag if reward positive)
                if reward > 0:
                    self.q[sk]["add_suggested_tag"] += min(10.0, reward * 0.5)
                    self.q[sk]["boost_tag"] += min(10.0, reward * 0.2)
                else:
                    self.q[sk]["nop"] += min(10.0, abs(reward) * 0.1)
                    
            except (ValueError, TypeError, KeyError) as e:
                print(f"Warning: Skipping invalid example {i}: {e}")
                continue
                    
            except (ValueError, TypeError, KeyError) as e:
                print(f"Warning: Skipping invalid example {i}: {e}")
                continue
        
        # persist at end
        self._persist()

    # -------------------------
    # Persistence & metrics
    # -------------------------
    def metrics(self) -> Dict:
        """Get agent performance metrics with database sync"""
        # Sync with database to get accurate content count
        try:
            import sqlite3
            conn = sqlite3.connect('data.db')
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM content')
            db_content_count = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM feedback')
            db_feedback_count = cur.fetchone()[0]
            conn.close()
        except Exception:
            db_content_count = len(self.contents)
            db_feedback_count = len(self.replay)  # Use replay buffer size as fallback
        
        return {
            "epsilon": max(0.0, min(1.0, self.epsilon)),
            "q_states": len(self.q),
            "avg_recent_reward": round(sum(self.recent_rewards) / len(self.recent_rewards), 3) if self.recent_rewards else 0.0,
            "replay_size": len(self.replay),
            "total_contents": db_content_count,
            "registered_contents": len(self.contents),
            "total_feedback_events": db_feedback_count,
            "learning_rate": self.alpha,
            "discount_factor": self.gamma
        }

    def sync_with_database(self):
        """Sync agent with existing database content"""
        try:
            import sqlite3
            conn = sqlite3.connect('data.db')
            cur = conn.cursor()
            cur.execute('SELECT content_id, current_tags, authenticity_score FROM content')
            rows = cur.fetchall()
            conn.close()
            
            for row in rows:
                content_id, tags_json, authenticity = row
                try:
                    tags = json.loads(tags_json) if tags_json else []
                except:
                    tags = []
                
                authenticity = authenticity or 0.5
                self.register_content(content_id, tags, authenticity)
                
        except Exception as e:
            print(f"Warning: Could not sync with database: {e}")
    
    def _persist(self):
        """Safely persist agent state to file"""
        try:
            # Validate state path to prevent path traversal
            safe_path = Path(self.state_path).resolve()
            
            # Ensure path is within current directory or subdirectory
            current_dir = Path.cwd().resolve()
            if not str(safe_path).startswith(str(current_dir)):
                raise ValueError("State file must be within the application's working directory.")
            
            if not str(safe_path).endswith('.json'):
                raise ValueError("State file must have .json extension")
            
            # Create backup of existing state (Windows-safe)
            if safe_path.exists():
                backup_path = safe_path.with_suffix('.json.bak')
                try:
                    if backup_path.exists():
                        backup_path.unlink()  # Remove existing backup
                    safe_path.rename(backup_path)
                except (OSError, PermissionError):
                    # Skip backup if file operations fail
                    pass
            
            # Write new state
            with open(safe_path, "w", encoding="utf-8") as f:
                json.dump({
                    "q": self.q, 
                    "epsilon": max(0.0, min(1.0, self.epsilon))
                }, f, indent=2)
                
        except (IOError, OSError, ValueError) as e:
            print(f"Warning: Could not persist agent state: {e}")
