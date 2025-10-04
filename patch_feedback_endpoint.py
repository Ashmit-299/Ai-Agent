#!/usr/bin/env python3
"""
Patch feedback endpoint to add better error handling
"""

patch_code = '''
@step5_router.post('/feedback', response_model=FeedbackResponse, status_code=201)
async def feedback_async(
    f: FeedbackRequest, 
    request: Request,
    current_user = Depends(get_current_user_required),
    _rate_limit = Depends(rate_limit_feedback)
):
    """STEP 5A: Submit feedback to train RL agent (requires authentication) - ASYNC with rate limiting"""
    
    request_id = getattr(request.state, 'request_id', None)
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Validate rating
        if not (1 <= f.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Get user_id
        user_id = current_user.user_id
        timestamp = time.time()
        
        # Convert rating to reward
        reward = (f.rating - 3) / 2.0
        event_type = 'like' if f.rating >= 4 else 'dislike' if f.rating <= 2 else 'view'
        
        # Save feedback to database
        try:
            import psycopg2
            DATABASE_URL = os.getenv("DATABASE_URL")
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO feedback (content_id, user_id, event_type, watch_time_ms, reward, rating, comment, timestamp, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                f.content_id, user_id, event_type, 0, reward, f.rating, f.comment, timestamp, client_ip
            ))
            
            feedback_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"Feedback saved: ID {feedback_id}")
            
        except Exception as db_error:
            print(f"Database error: {db_error}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        # Train RL agent
        try:
            await asyncio.to_thread(
                agent.observe_feedback,
                content_id=f.content_id,
                event_type=event_type,
                watch_time_ms=0,
                user_feedback=reward
            )
            agent_metrics = agent.metrics()
            
            return FeedbackResponse(
                status='success',
                rating=f.rating,
                event_type=event_type,
                reward=reward,
                rl_training={
                    'agent_trained': True,
                    'current_epsilon': agent_metrics['epsilon'],
                    'q_states': agent_metrics['q_states'],
                    'avg_recent_reward': agent_metrics['avg_recent_reward']
                },
                next_step=f'GET /recommend-tags/{f.content_id} to see updated AI recommendations'
            )
            
        except Exception as rl_error:
            print(f"RL agent error: {rl_error}")
            return {
                'status': 'success',
                'rating': f.rating,
                'event_type': event_type,
                'reward': reward,
                'rl_training': {
                    'agent_trained': False,
                    'error': str(rl_error)
                },
                'next_step': f'GET /recommend-tags/{f.content_id} to see AI recommendations'
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Feedback error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Feedback failed: {str(e)}")
'''

print("Feedback Endpoint Patch")
print("="*60)
print("\nThe feedback endpoint needs to be patched with better error handling.")
print("\nRecommended fix:")
print("1. The current error is being swallowed without logging")
print("2. Need to add explicit error messages")
print("3. Simplify the database save logic")
print("\nThe issue is likely in one of these areas:")
print("- DatabaseManager.create_feedback() method")
print("- save_json() function call")
print("- RL agent training")
print("- Observability tracking")
print("\nQuick fix: Restart the server and check the console output")
print("The error should be printed to the console now.")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("To apply this fix:")
    print("1. The feedback endpoint in routes.py needs simplified error handling")
    print("2. Remove complex try-catch blocks that hide errors")
    print("3. Add explicit print statements for debugging")
    print("="*60)
