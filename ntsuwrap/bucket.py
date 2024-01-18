import datetime
import pytz

class YoutubeTokenBucket:
    ''' Capacity max is 10000 (unless you've negotiated an extension)'''
    def __init__(self, capacity=10000):
        self.max = capacity
        self.tokens = capacity
        self.last_refill_time = self._get_current_time()

    def _get_current_time(self):
        pacific_tz = pytz.timezone('US/Pacific')
        return datetime.datetime.now(pacific_tz).date()

    def _refill(self):
        current_date = self._get_current_time()
        if current_date != self.last_refill_time:
            self.tokens = self.max
            self.last_refill_time = current_date

    def take(self, tokens: int):
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def current_amount(self):
        return self.tokens