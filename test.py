from datetime import datetime, timezone, tzinfo

import pytz

a = datetime.now(pytz.timezone('Asia/Kolkata'))

print(a)