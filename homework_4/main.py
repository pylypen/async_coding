import asyncio
import random


class Fork:
    """Клас для представлення вилки."""

    def __init__(self, number):
        self.number = number
        self.real_number = number + 1
        self.lock = asyncio.Lock()


class Philosopher:
    """Клас для представлення філософа."""

    def __init__(self, number, left_fork, right_fork):
        self.number = number
        self.real_number = number+1
        self.left_fork = left_fork
        self.right_fork = right_fork

    async def think(self):
        print(f'Філософ {self.real_number} думає.')
        await asyncio.sleep(random.uniform(1, 3))

    async def eat(self):
        async with self.left_fork.lock:
            print(f'Філософ {self.real_number} взяв ліву вилку {self.left_fork.real_number}.')

            async with self.right_fork.lock:
                print(f'Філософ {self.real_number} взяв праву вилку {self.right_fork.real_number}.')

                print(f'Філософ {self.real_number} їсть.')
                await asyncio.sleep(random.uniform(1, 3))

                print(f'Філософ {self.real_number} поклав праву вилку {self.right_fork.real_number}.')

            print(f'Філософ {self.real_number} поклав ліву вилку {self.left_fork.real_number}.')

    async def dine(self):
        while True:
            await self.think()
            await self.eat()


async def main():
    forks = [Fork(i) for i in range(5)]

    # Створюємо філософів з відповідними вилками
    philosophers = [
        Philosopher(i, forks[i], forks[(i + 1) % 5])
        for i in range(5)
    ]

    # Запускаємо всі завдання одночасно
    await asyncio.gather(*(philosopher.dine() for philosopher in philosophers))

# Запускаємо подію
if __name__ == "__main__":

    asyncio.run(main())
