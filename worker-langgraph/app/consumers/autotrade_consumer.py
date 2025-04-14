from app.utils.message_queue import create_kafka_consumer, poll_kafka_msg, commit_kafka
from app.handlers.handle_autotrade_job import handle_autotrade_job
import asyncio


async def run_autotrade_consumer():
    print("🚀 Starting AutoTrader consumer", flush=True)

    consumer = create_kafka_consumer("autotrade.jobs", "autotrade-consumer")

    if consumer:
        print("✅ Kafka consumer initialized for 'autotrade.jobs'", flush=True)
    else:
        print("❌ Kafka consumer failed to initialize", flush=True)
        return

    while True:
        try:
            data, msg = await poll_kafka_msg(consumer)

            if not data:
                await asyncio.sleep(1)
                continue

            print(
                f"📥 Received AutoTrader job: {data.get('job_id') or data.get('ticker')}",
                flush=True,
            )

            await handle_autotrade_job(data)

            if msg:
                print("✅ Committing Kafka offset", flush=True)
                commit_kafka(consumer, msg)

        except Exception as e:
            print(f"❌ Error in AutoTrader consumer loop: {e}", flush=True)
            await asyncio.sleep(1)
