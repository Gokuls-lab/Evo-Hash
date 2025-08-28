import os
import uuid
import pickle
import neat
import hashlib
from fastapi import FastAPI, Request, Form, Depends, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine, User, Base

# --- 1. Global Setup ---
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
NEAT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config-feedforward.txt')
MODELS_DIR = 'models'

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# --- 2. Real NEAT Model Management ---

def create_and_save_neat_model(user_id: str):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         NEAT_CONFIG_PATH)
    genome = neat.DefaultGenome(user_id)
    genome.configure_new(config.genome_config)
    model_path = os.path.join(MODELS_DIR, f"{user_id}.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(genome, f)

def transform_with_neat(user_id: str, input_string: str) -> str:
    model_path = os.path.join(MODELS_DIR, f"{user_id}.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model for user {user_id} not found.")
    with open(model_path, 'rb') as f:
        genome = pickle.load(f)
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         NEAT_CONFIG_PATH)
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    input_bytes = input_string.encode('utf-8')
    inputs = [(byte / 128.0) - 1.0 for byte in input_bytes]
    inputs += [0.0] * (256 - len(inputs))
    inputs = inputs[:256]
    outputs = net.activate(inputs)

    # Convert the list of floats to a single string and hash it
    output_string = ''.join(map(str, outputs))
    return hashlib.sha256(output_string.encode('utf-8')).hexdigest()

# --- 3. Database & Auth Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_admin_user(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("admin_session")
    if not session_token:
        raise HTTPException(status_code=307, detail="Not authenticated", headers={"Location": "/admin/login"})
    user = db.query(User).filter(User.id == session_token, User.is_admin == True).first()
    if not user:
        raise HTTPException(status_code=307, detail="Not authorized", headers={"Location": "/admin/login"})
    return user

# --- 4. FastAPI Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_user_endpoint(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

    transformed_input = transform_with_neat(user.id, password)
    if user.neat_hash == transformed_input:
        return templates.TemplateResponse("login.html", {"request": request, "success": "Login successful!"})
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user_endpoint(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})

    user_id = str(uuid.uuid4())
    create_and_save_neat_model(user_id)
    neat_hash = transform_with_neat(user_id, password)

    is_admin = False
    if username.lower() == 'admin' and db.query(User).count() == 0:
        is_admin = True

    new_user = User(id=user_id, username=username, neat_hash=neat_hash, neat_model_id=user_id, is_admin=is_admin)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)

# --- 5. Admin Panel Endpoints ---

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_form(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/login")
async def admin_login_endpoint(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    user = db.query(User).filter(User.username == username, User.is_admin == True).first()
    if not user:
        return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Invalid credentials or not an admin"})

    transformed_input = transform_with_neat(user.id, password)
    if user.neat_hash == transformed_input:
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_session", value=user.id, httponly=True)
        return response
    else:
        return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Invalid credentials or not an admin"})

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "users": users})
