import time

def robust_invoke(chain, input_data):
    """
    Bulletproof retry logic to handle Gemini's strict 20 RPM free tier limits.
    If a 429 RESOURCE_EXHAUSTED error is encountered, it will pause for 60 seconds
    to let the quota fully reset before trying again.
    """
    for attempt in range(15):
        try:
            return chain.invoke(input_data)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota exceeded" in error_str:
                print(f"\n[Rate Limit Hit] Waiting 60 seconds for quota to reset (Attempt {attempt+1}/15)...")
                time.sleep(60)
            else:
                raise e
    raise Exception("Max retries exceeded for LLM invocation")
