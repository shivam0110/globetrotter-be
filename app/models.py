from prisma import Prisma

# Initialize Prisma client
prisma = Prisma()
prisma.connect()

# Make sure to disconnect when the application shuts down
import atexit
atexit.register(prisma.disconnect)
