#!/usr/bin/env sh
set -e
# تطبيق الجداور قبل تشغيل الخادم (أول مرة وبعد كل تحديث للسكيما)
alembic upgrade head
exec "$@"
