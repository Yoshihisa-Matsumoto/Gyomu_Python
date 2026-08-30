import argparse
import asyncio
import traceback
from typing import Any

from gyomu_ai.provider.pydantic_ai.google import (
    create_default_pydantic_ai_model_registry,
)
from pydantic_ai import Agent


async def request(
    agent: Agent[Any, str],
    request_id: int,
) -> None:
    try:
        print(f"[{request_id}] start")

        result = await agent.run(
            "Reply with exactly: OK",
        )

        print(
            f"[{request_id}] success: {result.output!r}",
        )

    except BaseException as error:
        print()
        print("=" * 80)
        print(f"[{request_id}] ERROR")
        print("=" * 80)

        dump_exception(error)

        print()
        print("Traceback:")
        traceback.print_exception(error)

        print("=" * 80)
        print()


def dump_exception(error: BaseException) -> None:
    print(f"type:      {type(error)!r}")
    print(f"class:     {type(error).__name__}")
    print(f"module:    {type(error).__module__}")
    print(f"mro:       {type(error).__mro__}")
    print(f"message:   {error}")
    print(f"repr:      {error!r}")
    print(f"cause:     {error.__cause__!r}")
    print(f"context:   {error.__context__!r}")

    try:
        attributes = vars(error)
    except TypeError:
        attributes = {}

    print(f"attributes: {attributes}")

    print()
    print("Public attributes:")

    for name in dir(error):
        if name.startswith("_"):
            continue

        try:
            value = getattr(error, name)
        except Exception as attribute_error:
            value = f"<failed to read: {attribute_error!r}>"

        if callable(value):
            continue

        print(f"  {name}: {value!r}")


async def main(request_count: int) -> None:
    registry = create_default_pydantic_ai_model_registry()

    model = registry.fast(None)
    agent = Agent(model=model)

    print(f"Sending {request_count} concurrent requests...")
    print()

    results = await asyncio.gather(
        *(request(agent, request_id) for request_id in range(request_count))
    )

    _ = results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Probe Pydantic AI exceptions using concurrent Gemini requests.",
    )
    parser.add_argument(
        "-n",
        "--requests",
        type=int,
        default=50,
        help="Number of concurrent requests. Default: 50.",
    )

    args = parser.parse_args()

    asyncio.run(main(args.requests))
