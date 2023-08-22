from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
import httpx

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# Connect to MongoDB using motor
mongo_uri = "mongodb+srv://jvDev:rLhvxX5wWVPoZw40@clusternave.2pqpbpv.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(mongo_uri)
db = client["ClusterNave"]
collection = db["elite6-data"]

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, 'data': None})

@app.get('/setDB/{id}')
async def setDB(id: int, request: Request):
    print(id)
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
                return templates.TemplateResponse("index.html", {"request": request, 'data': pokemon_data})
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

# route to get the pokemon id from the index.html form
@app.post("/pokemon")
async def get_pokemon(request: Request):
    form_data = await request.form()
    pokemon_id = form_data["pokemon_id"]
    return RedirectResponse(url=str("/setDB/" + pokemon_id))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
