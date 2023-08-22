from fastapi import FastAPI, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
import httpx

app = FastAPI()

# Connect to MongoDB using motor
mongo_uri = "mongodb+srv://jvDev:rLhvxX5wWVPoZw40@clusternave.2pqpbpv.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(mongo_uri)
db = client["ClusterNave"]
collection = db["elite6-data"]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get('/setDB/{id}')
async def setDB(id: int, request: Request):
    url = f'https://pokeapi.co/api/v2/pokemon/{id}'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            pokemon_data = {
                '_id': id,
                'name': response.json()['name'],
                'image': response.json()['sprites']['front_default']
            }
            try:
                # Insert the fetched data into the MongoDB collection asynchronously
                await collection.insert_one(pokemon_data)
                return {'message': 'Data inserted successfully'}
            except Exception as e:
                return {'error': 'Failed to insert data into the database'}
        else:
            return {'error': 'Failed to fetch data from the API'}

@app.get("/{id}", response_description="Get a single Pokémon")
async def show_poke(id: str):
    pokemon = await collection.find_one({"_id": id})
    if pokemon:
        return pokemon
    raise HTTPException(status_code=404, detail=f"Pokémon {id} not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
