import asyncio
import random


class Fork:
    """A class to represent a fork."""

    def __init__(self, number):
        self.number = number
        self.real_number = number + 1
        self.lock = asyncio.Lock()


class Philosopher:
    """A philosopher class."""

    def __init__(self, number, left_fork, right_fork):
        self.number = number
        self.real_number = number+1
        self.left_fork = left_fork
        self.right_fork = right_fork

    async def think(self):
        print(f'Philosopher {self.real_number} thinks.')
        await asyncio.sleep(random.uniform(1, 3))

    async def eat(self):
        async with self.left_fork.lock:
            print(f'Philosopher {self.real_number} took the left fork {self.left_fork.real_number}.')

            async with self.right_fork.lock:
                print(f'Philosopher {self.real_number} took the right fork {self.right_fork.real_number}.')

                print(f'Philosopher {self.real_number} eats.')
                await asyncio.sleep(random.uniform(1, 3))

                print(f'Philosopher {self.real_number} put down the right fork {self.right_fork.real_number}.')

            print(f'Philosopher {self.real_number} placed the left fork {self.left_fork.real_number}.')

    async def dine(self):
        while True:
            await self.think()
            await self.eat()


async def main():
    forks = [Fork(i) for i in range(5)]

    philosophers = [
        Philosopher(i, forks[i], forks[(i + 1) % 5])
        for i in range(5)
    ]

    await asyncio.gather(*(philosopher.dine() for philosopher in philosophers))

if __name__ == "__main__":
    asyncio.run(main())
