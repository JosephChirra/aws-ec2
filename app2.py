# import datetime
# from typing import List, Optional
# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.responses import HTMLResponse
# from pydantic import BaseModel, Field
# from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# import uvicorn

# # ==========================================
# # DATABASE CONFIGURATION
# # ==========================================
# SQLALCHEMY_DATABASE_URL = "sqlite:///./assets.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# class AssetDB(Base):
#     __tablename__ = "assets"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True, nullable=False)
#     instance_type = Column(String, nullable=False)
#     status = Column(String, default="stopped", nullable=False)  # running, stopped, terminated
#     ip_address = Column(String, nullable=True)
#     region = Column(String, nullable=False)
#     created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # ==========================================
# # PYDANTIC SCHEMAS
# # ==========================================
# class AssetBase(BaseModel):
#     name: str = Field(..., min_length=1, max_length=100, examples=["Web-Server-Prod"])
#     instance_type: str = Field(..., examples=["t2.micro"])
#     status: str = Field(default="stopped", examples=["running"])
#     ip_address: Optional[str] = Field(default=None, examples=["54.210.12.85"])
#     region: str = Field(..., examples=["us-east-1"])

# class AssetCreate(AssetBase):
#     pass

# class AssetUpdate(BaseModel):
#     name: Optional[str] = None
#     instance_type: Optional[str] = None
#     status: Optional[str] = None
#     ip_address: Optional[str] = None
#     region: Optional[str] = None

# class AssetResponse(AssetBase):
#     id: int
#     created_at: datetime.datetime

#     class Config:
#         from_attributes = True

# # ==========================================
# # FASTAPI APP INITIALIZATION
# # ==========================================
# app = FastAPI(
#     title="AWS EC2 Cloud Asset Manager",
#     description="A complete CRUD application to manage cloud virtual instances.",
#     version="1.0.0"
# )

# # Seed initial data if DB is empty
# def seed_data():
#     db = SessionLocal()
#     if db.query(AssetDB).count() == 0:
#         initial_assets = [
#             AssetDB(name="Web-Server-Prod", instance_type="t3.medium", status="running", ip_address="54.210.12.85", region="us-east-1"),
#             AssetDB(name="Database-Replica", instance_type="r6g.large", status="stopped", ip_address="18.23.45.112", region="us-west-2"),
#             AssetDB(name="Auth-Service-Dev", instance_type="t2.micro", status="terminated", ip_address=None, region="eu-west-1")
#         ]
#         db.add_all(initial_assets)
#         db.commit()
#     db.close()

# seed_data()

# # ==========================================
# # API ENDPOINTS (CRUD)
# # ==========================================

# # CREATE
# @app.post("/api/assets", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
# def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
#     db_asset = AssetDB(
#         name=asset.name,
#         instance_type=asset.instance_type,
#         status=asset.status,
#         ip_address=asset.ip_address,
#         region=asset.region
#     )
#     db.add(db_asset)
#     db.commit()
#     db.refresh(db_asset)
#     return db_asset

# # READ ALL
# @app.get("/api/assets", response_model=List[AssetResponse])
# def read_assets(skip: int = 0, limit: int = 100, search: Optional[str] = None, db: Session = Depends(get_db)):
#     query = db.query(AssetDB)
#     if search:
#         query = query.filter(AssetDB.name.contains(search) | AssetDB.region.contains(search) | AssetDB.status.contains(search))
#     return query.offset(skip).limit(limit).all()

# # READ ONE
# @app.get("/api/assets/{asset_id}", response_model=AssetResponse)
# def read_asset(asset_id: int, db: Session = Depends(get_db)):
#     db_asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
#     if not db_asset:
#         raise HTTPException(status_code=404, detail="Asset not found")
#     return db_asset

# # UPDATE
# @app.put("/api/assets/{asset_id}", response_model=AssetResponse)
# def update_asset(asset_id: int, asset_update: AssetUpdate, db: Session = Depends(get_db)):
#     db_asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
#     if not db_asset:
#         raise HTTPException(status_code=404, detail="Asset not found")
    
#     update_data = asset_update.model_dump(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_asset, key, value)
        
#     db.commit()
#     db.refresh(db_asset)
#     return db_asset

# # DELETE
# @app.delete("/api/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_asset(asset_id: int, db: Session = Depends(get_db)):
#     db_asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
#     if not db_asset:
#         raise HTTPException(status_code=404, detail="Asset not found")
#     db.delete(db_asset)
#     db.commit()
#     return None

# # HEALTH CHECK
# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "timestamp": datetime.datetime.utcnow()}

# # ==========================================
# # FRONTEND DASHBOARD
# # ==========================================
# @app.get("/", response_class=HTMLResponse)
# def get_dashboard():
#     html_content = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>Cloud Asset Control Center</title>
#         <!-- Google Fonts -->
#         <link rel="preconnect" href="https://fonts.googleapis.com">
#         <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
#         <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
#         <!-- Font Awesome -->
#         <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
#         <style>
#             :root {
#                 --bg-primary: #0b0f19;
#                 --bg-secondary: #131a2c;
#                 --text-primary: #f8fafc;
#                 --text-secondary: #94a3b8;
#                 --accent-blue: #3b82f6;
#                 --accent-blue-hover: #2563eb;
#                 --accent-green: #10b981;
#                 --accent-green-glow: rgba(16, 185, 129, 0.15);
#                 --accent-yellow: #f59e0b;
#                 --accent-yellow-glow: rgba(245, 158, 11, 0.15);
#                 --accent-red: #ef4444;
#                 --accent-red-glow: rgba(239, 68, 68, 0.15);
#                 --border-color: rgba(255, 255, 255, 0.08);
#                 --card-bg: rgba(255, 255, 255, 0.03);
#                 --glass-filter: blur(16px);
#             }

#             * {
#                 box-sizing: border-box;
#                 margin: 0;
#                 padding: 0;
#                 font-family: 'Outfit', sans-serif;
#             }

#             body {
#                 background: linear-gradient(135deg, var(--bg-primary), #111827, #0f172a);
#                 color: var(--text-primary);
#                 min-height: 100vh;
#                 display: flex;
#                 flex-direction: column;
#                 overflow-x: hidden;
#             }

#             header {
#                 backdrop-filter: var(--glass-filter);
#                 background: rgba(11, 15, 25, 0.7);
#                 border-bottom: 1px solid var(--border-color);
#                 padding: 1.25rem 2rem;
#                 position: sticky;
#                 top: 0;
#                 z-index: 100;
#                 display: flex;
#                 justify-content: space-between;
#                 align-items: center;
#             }

#             .logo-container {
#                 display: flex;
#                 align-items: center;
#                 gap: 0.75rem;
#             }

#             .logo-icon {
#                 background: linear-gradient(135deg, var(--accent-blue), #8b5cf6);
#                 width: 40px;
#                 height: 40px;
#                 border-radius: 12px;
#                 display: flex;
#                 align-items: center;
#                 justify-content: center;
#                 color: white;
#                 font-size: 1.2rem;
#                 box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
#             }

#             .logo-text h1 {
#                 font-size: 1.25rem;
#                 font-weight: 700;
#                 letter-spacing: -0.5px;
#                 background: linear-gradient(to right, #ffffff, #94a3b8);
#                 -webkit-background-clip: text;
#                 -webkit-text-fill-color: transparent;
#             }

#             .logo-text span {
#                 font-size: 0.75rem;
#                 color: var(--accent-blue);
#                 font-weight: 600;
#                 text-transform: uppercase;
#                 letter-spacing: 1px;
#             }

#             .container {
#                 max-width: 1200px;
#                 width: 100%;
#                 margin: 0 auto;
#                 padding: 2rem;
#                 flex-grow: 1;
#             }

#             /* Stats Section */
#             .stats-grid {
#                 display: grid;
#                 grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
#                 gap: 1.5rem;
#                 margin-bottom: 2rem;
#             }

#             .stat-card {
#                 background: var(--card-bg);
#                 backdrop-filter: var(--glass-filter);
#                 border: 1px solid var(--border-color);
#                 border-radius: 16px;
#                 padding: 1.5rem;
#                 display: flex;
#                 align-items: center;
#                 gap: 1.25rem;
#                 transition: transform 0.3s ease, border-color 0.3s ease;
#             }

#             .stat-card:hover {
#                 transform: translateY(-2px);
#                 border-color: rgba(255, 255, 255, 0.15);
#             }

#             .stat-icon {
#                 width: 48px;
#                 height: 48px;
#                 border-radius: 12px;
#                 display: flex;
#                 align-items: center;
#                 justify-content: center;
#                 font-size: 1.25rem;
#             }

#             .stat-icon.total { background: rgba(59, 130, 246, 0.1); color: var(--accent-blue); }
#             .stat-icon.running { background: rgba(16, 185, 129, 0.1); color: var(--accent-green); }
#             .stat-icon.stopped { background: rgba(245, 158, 11, 0.1); color: var(--accent-yellow); }
#             .stat-icon.terminated { background: rgba(239, 68, 68, 0.1); color: var(--accent-red); }

#             .stat-info .stat-value {
#                 font-size: 1.75rem;
#                 font-weight: 700;
#                 line-height: 1.2;
#             }

#             .stat-info .stat-label {
#                 font-size: 0.875rem;
#                 color: var(--text-secondary);
#             }

#             /* Controls Section */
#             .controls-bar {
#                 display: flex;
#                 justify-content: space-between;
#                 align-items: center;
#                 flex-wrap: wrap;
#                 gap: 1rem;
#                 margin-bottom: 2rem;
#             }

#             .search-box {
#                 position: relative;
#                 flex-grow: 1;
#                 max-width: 400px;
#             }

#             .search-box input {
#                 width: 100%;
#                 padding: 0.75rem 1rem 0.75rem 2.5rem;
#                 background: rgba(255, 255, 255, 0.05);
#                 border: 1px solid var(--border-color);
#                 border-radius: 12px;
#                 color: var(--text-primary);
#                 font-size: 0.95rem;
#                 transition: all 0.3s ease;
#             }

#             .search-box input:focus {
#                 outline: none;
#                 border-color: var(--accent-blue);
#                 background: rgba(255, 255, 255, 0.08);
#                 box-shadow: 0 0 15px rgba(59, 130, 246, 0.15);
#             }

#             .search-box i {
#                 position: absolute;
#                 left: 1rem;
#                 top: 50%;
#                 transform: translateY(-50%);
#                 color: var(--text-secondary);
#             }

#             .btn {
#                 padding: 0.75rem 1.5rem;
#                 border-radius: 12px;
#                 font-weight: 600;
#                 font-size: 0.95rem;
#                 cursor: pointer;
#                 display: inline-flex;
#                 align-items: center;
#                 gap: 0.5rem;
#                 transition: all 0.3s ease;
#                 border: none;
#             }

#             .btn-primary {
#                 background: var(--accent-blue);
#                 color: white;
#             }

#             .btn-primary:hover {
#                 background: var(--accent-blue-hover);
#                 transform: translateY(-1px);
#                 box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
#             }

#             .btn-secondary {
#                 background: rgba(255, 255, 255, 0.08);
#                 color: var(--text-primary);
#                 border: 1px solid var(--border-color);
#             }

#             .btn-secondary:hover {
#                 background: rgba(255, 255, 255, 0.12);
#             }

#             /* Grid of Cards */
#             .instances-grid {
#                 display: grid;
#                 grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
#                 gap: 1.5rem;
#             }

#             .instance-card {
#                 background: var(--card-bg);
#                 backdrop-filter: var(--glass-filter);
#                 border: 1px solid var(--border-color);
#                 border-radius: 16px;
#                 padding: 1.5rem;
#                 position: relative;
#                 overflow: hidden;
#                 transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
#             }

#             .instance-card:hover {
#                 transform: translateY(-4px);
#                 border-color: rgba(255, 255, 255, 0.15);
#                 box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
#             }

#             .card-header {
#                 display: flex;
#                 justify-content: space-between;
#                 align-items: flex-start;
#                 margin-bottom: 1rem;
#             }

#             .instance-title {
#                 font-size: 1.15rem;
#                 font-weight: 600;
#                 color: var(--text-primary);
#                 overflow: hidden;
#                 text-overflow: ellipsis;
#                 white-space: nowrap;
#                 max-width: 180px;
#             }

#             .status-badge {
#                 padding: 0.25rem 0.75rem;
#                 border-radius: 9999px;
#                 font-size: 0.75rem;
#                 font-weight: 600;
#                 text-transform: uppercase;
#                 display: inline-flex;
#                 align-items: center;
#                 gap: 0.35rem;
#             }

#             .status-badge.running {
#                 background: var(--accent-green-glow);
#                 color: var(--accent-green);
#                 border: 1px solid rgba(16, 185, 129, 0.3);
#             }

#             .status-badge.running::before {
#                 content: '';
#                 display: inline-block;
#                 width: 6px;
#                 height: 6px;
#                 border-radius: 50%;
#                 background: var(--accent-green);
#                 box-shadow: 0 0 8px var(--accent-green);
#                 animation: pulse 1.5s infinite;
#             }

#             .status-badge.stopped {
#                 background: var(--accent-yellow-glow);
#                 color: var(--accent-yellow);
#                 border: 1px solid rgba(245, 158, 11, 0.3);
#             }

#             .status-badge.terminated {
#                 background: var(--accent-red-glow);
#                 color: var(--accent-red);
#                 border: 1px solid rgba(239, 68, 68, 0.3);
#             }

#             .card-body {
#                 display: flex;
#                 flex-direction: column;
#                 gap: 0.75rem;
#                 margin-bottom: 1.5rem;
#                 font-size: 0.9rem;
#             }

#             .info-row {
#                 display: flex;
#                 justify-content: space-between;
#                 color: var(--text-secondary);
#             }

#             .info-label {
#                 font-weight: 500;
#             }

#             .info-value {
#                 color: var(--text-primary);
#                 font-family: monospace;
#             }

#             .card-actions {
#                 display: flex;
#                 gap: 0.5rem;
#                 border-top: 1px solid var(--border-color);
#                 padding-top: 1rem;
#             }

#             .action-btn {
#                 flex: 1;
#                 padding: 0.5rem;
#                 border-radius: 8px;
#                 border: 1px solid var(--border-color);
#                 background: rgba(255, 255, 255, 0.02);
#                 color: var(--text-secondary);
#                 cursor: pointer;
#                 font-size: 0.85rem;
#                 font-weight: 500;
#                 transition: all 0.2s ease;
#                 display: inline-flex;
#                 align-items: center;
#                 justify-content: center;
#                 gap: 0.35rem;
#             }

#             .action-btn:hover {
#                 background: rgba(255, 255, 255, 0.08);
#                 color: var(--text-primary);
#             }

#             .action-btn.btn-start-stop {
#                 color: var(--accent-blue);
#                 border-color: rgba(59, 130, 246, 0.2);
#             }
#             .action-btn.btn-start-stop:hover {
#                 background: rgba(59, 130, 246, 0.1);
#                 color: var(--text-primary);
#             }

#             .action-btn.btn-delete:hover {
#                 background: var(--accent-red-glow);
#                 border-color: rgba(239, 68, 68, 0.4);
#                 color: var(--accent-red);
#             }

#             /* Modal overlay */
#             .modal-overlay {
#                 position: fixed;
#                 top: 0;
#                 left: 0;
#                 right: 0;
#                 bottom: 0;
#                 background: rgba(0, 0, 0, 0.7);
#                 backdrop-filter: blur(8px);
#                 z-index: 1000;
#                 display: flex;
#                 align-items: center;
#                 justify-content: center;
#                 opacity: 0;
#                 pointer-events: none;
#                 transition: opacity 0.3s ease;
#             }

#             .modal-overlay.active {
#                 opacity: 1;
#                 pointer-events: auto;
#             }

#             .modal-content {
#                 background: var(--bg-secondary);
#                 border: 1px solid var(--border-color);
#                 border-radius: 20px;
#                 width: 90%;
#                 max-width: 480px;
#                 padding: 2rem;
#                 transform: translateY(-20px);
#                 transition: transform 0.3s ease;
#                 box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
#             }

#             .modal-overlay.active .modal-content {
#                 transform: translateY(0);
#             }

#             .modal-header {
#                 display: flex;
#                 justify-content: space-between;
#                 align-items: center;
#                 margin-bottom: 1.5rem;
#             }

#             .modal-title {
#                 font-size: 1.25rem;
#                 font-weight: 700;
#             }

#             .close-modal-btn {
#                 background: none;
#                 border: none;
#                 color: var(--text-secondary);
#                 cursor: pointer;
#                 font-size: 1.25rem;
#                 transition: color 0.2s ease;
#             }

#             .close-modal-btn:hover {
#                 color: var(--text-primary);
#             }

#             /* Form Elements */
#             .form-group {
#                 margin-bottom: 1.25rem;
#             }

#             .form-label {
#                 display: block;
#                 font-size: 0.875rem;
#                 font-weight: 600;
#                 color: var(--text-secondary);
#                 margin-bottom: 0.5rem;
#             }

#             .form-input {
#                 width: 100%;
#                 padding: 0.75rem 1rem;
#                 background: rgba(255, 255, 255, 0.05);
#                 border: 1px solid var(--border-color);
#                 border-radius: 10px;
#                 color: var(--text-primary);
#                 font-size: 0.95rem;
#                 transition: all 0.3s ease;
#             }

#             .form-input:focus {
#                 outline: none;
#                 border-color: var(--accent-blue);
#                 background: rgba(255, 255, 255, 0.08);
#             }

#             .form-select {
#                 appearance: none;
#                 background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
#                 background-repeat: no-repeat;
#                 background-position: right 1rem center;
#                 background-size: 1em;
#             }

#             .modal-footer {
#                 display: flex;
#                 justify-content: flex-end;
#                 gap: 0.75rem;
#                 margin-top: 2rem;
#             }

#             /* Toast Notification */
#             .toast-container {
#                 position: fixed;
#                 bottom: 2rem;
#                 right: 2rem;
#                 z-index: 2000;
#                 display: flex;
#                 flex-direction: column;
#                 gap: 0.75rem;
#             }

#             .toast {
#                 background: rgba(19, 26, 44, 0.9);
#                 backdrop-filter: var(--glass-filter);
#                 border: 1px solid var(--border-color);
#                 border-radius: 12px;
#                 padding: 1rem 1.5rem;
#                 color: var(--text-primary);
#                 display: flex;
#                 align-items: center;
#                 gap: 0.75rem;
#                 min-width: 280px;
#                 box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
#                 transform: translateX(120%);
#                 transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
#             }

#             .toast.active {
#                 transform: translateX(0);
#             }

#             .toast-icon.success { color: var(--accent-green); }
#             .toast-icon.error { color: var(--accent-red); }

#             /* Empty state */
#             .empty-state {
#                 grid-column: 1 / -1;
#                 text-align: center;
#                 padding: 4rem 2rem;
#                 background: var(--card-bg);
#                 border: 1px dashed var(--border-color);
#                 border-radius: 20px;
#                 color: var(--text-secondary);
#             }

#             .empty-state i {
#                 font-size: 3rem;
#                 margin-bottom: 1rem;
#                 color: rgba(255, 255, 255, 0.1);
#             }

#             .empty-state h3 {
#                 color: var(--text-primary);
#                 margin-bottom: 0.5rem;
#             }

#             @keyframes pulse {
#                 0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
#                 70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
#                 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
#             }

#             footer {
#                 text-align: center;
#                 padding: 2rem;
#                 color: var(--text-secondary);
#                 font-size: 0.85rem;
#                 border-top: 1px solid var(--border-color);
#                 margin-top: auto;
#             }

#             footer a {
#                 color: var(--accent-blue);
#                 text-decoration: none;
#             }
#         </style>
#     </head>
#     <body>
#         <header>
#             <div class="logo-container">
#                 <div class="logo-icon">
#                     <i class="fa-solid fa-server"></i>
#                 </div>
#                 <div class="logo-text">
#                     <h1>Cloud Assets</h1>
#                     <span>EC2 Manager</span>
#                 </div>
#             </div>
#             <div>
#                 <button class="btn btn-primary" onclick="openCreateModal()">
#                     <i class="fa-solid fa-plus"></i> Launch Instance
#                 </button>
#             </div>
#         </header>

#         <div class="container">
#             <!-- Stats -->
#             <div class="stats-grid">
#                 <div class="stat-card">
#                     <div class="stat-icon total"><i class="fa-solid fa-layer-group"></i></div>
#                     <div class="stat-info">
#                         <div class="stat-value" id="stat-total">0</div>
#                         <div class="stat-label">Total Nodes</div>
#                     </div>
#                 </div>
#                 <div class="stat-card">
#                     <div class="stat-icon running"><i class="fa-solid fa-circle-play"></i></div>
#                     <div class="stat-info">
#                         <div class="stat-value" id="stat-running">0</div>
#                         <div class="stat-label">Running</div>
#                     </div>
#                 </div>
#                 <div class="stat-card">
#                     <div class="stat-icon stopped"><i class="fa-solid fa-circle-stop"></i></div>
#                     <div class="stat-info">
#                         <div class="stat-value" id="stat-stopped">0</div>
#                         <div class="stat-label">Stopped</div>
#                     </div>
#                 </div>
#                 <div class="stat-card">
#                     <div class="stat-icon terminated"><i class="fa-solid fa-ban"></i></div>
#                     <div class="stat-info">
#                         <div class="stat-value" id="stat-terminated">0</div>
#                         <div class="stat-label">Terminated</div>
#                     </div>
#                 </div>
#             </div>

#             <!-- Controls -->
#             <div class="controls-bar">
#                 <div class="search-box">
#                     <i class="fa-solid fa-magnifying-glass"></i>
#                     <input type="text" id="search-input" placeholder="Search by name, status, or region..." oninput="handleSearch()">
#                 </div>
#             </div>

#             <!-- Main Grid -->
#             <div class="instances-grid" id="instances-container">
#                 <!-- Loaded dynamically -->
#             </div>
#         </div>

#         <!-- Create/Edit Modal -->
#         <div class="modal-overlay" id="asset-modal">
#             <div class="modal-content">
#                 <div class="modal-header">
#                     <h2 class="modal-title" id="modal-title">Launch Instance</h2>
#                     <button class="close-modal-btn" onclick="closeModal()"><i class="fa-solid fa-xmark"></i></button>
#                 </div>
#                 <form id="asset-form" onsubmit="saveAsset(event)">
#                     <input type="hidden" id="asset-id">
#                     <div class="form-group">
#                         <label class="form-label" for="asset-name">Instance Name</label>
#                         <input type="text" id="asset-name" class="form-input" required placeholder="e.g., Web-Prod-01">
#                     </div>
#                     <div class="form-group">
#                         <label class="form-label" for="asset-type">Instance Type</label>
#                         <select id="asset-type" class="form-input form-select" required>
#                             <option value="t2.micro">t2.micro (1 vCPU, 1 GiB)</option>
#                             <option value="t3.small">t3.small (2 vCPU, 2 GiB)</option>
#                             <option value="t3.medium">t3.medium (2 vCPU, 4 GiB)</option>
#                             <option value="m5.large">m5.large (2 vCPU, 8 GiB)</option>
#                             <option value="r6g.large">r6g.large (2 vCPU, 16 GiB)</option>
#                         </select>
#                     </div>
#                     <div class="form-group">
#                         <label class="form-label" for="asset-region">AWS Region</label>
#                         <select id="asset-region" class="form-input form-select" required>
#                             <option value="us-east-1">us-east-1 (N. Virginia)</option>
#                             <option value="us-west-2">us-west-2 (Oregon)</option>
#                             <option value="eu-west-1">eu-west-1 (Ireland)</option>
#                             <option value="ap-south-1">ap-south-1 (Mumbai)</option>
#                             <option value="ap-northeast-1">ap-northeast-1 (Tokyo)</option>
#                         </select>
#                     </div>
#                     <div class="form-group">
#                         <label class="form-label" for="asset-ip">IP Address (Optional)</label>
#                         <input type="text" id="asset-ip" class="form-input" placeholder="e.g., 54.210.12.85">
#                     </div>
#                     <div class="form-group">
#                         <label class="form-label" for="asset-status">Initial Status</label>
#                         <select id="asset-status" class="form-input form-select" required>
#                             <option value="stopped">Stopped</option>
#                             <option value="running">Running</option>
#                             <option value="terminated">Terminated</option>
#                         </select>
#                     </div>
#                     <div class="modal-footer">
#                         <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
#                         <button type="submit" class="btn btn-primary">Save Changes</button>
#                     </div>
#                 </form>
#             </div>
#         </div>

#         <!-- Toast Notifications -->
#         <div class="toast-container" id="toast-container"></div>

#         <footer>
#             <p>AWS EC2 Asset Dashboard. Powered by FastAPI & SQLite. Version 2.2.0</p>
#         </footer>

#         <script>
#             let allAssets = [];

#             // Fetch and render assets
#             async function fetchAssets(search = '') {
#                 try {
#                     const url = search ? `/api/assets?search=${encodeURIComponent(search)}` : '/api/assets';
#                     const response = await fetch(url);
#                     if (!response.ok) throw new Error('Failed to load assets');
#                     allAssets = await response.json();
#                     renderAssets(allAssets);
#                     updateStats(allAssets);
#                 } catch (error) {
#                     showToast(error.message, 'error');
#                 }
#             }

#             function renderAssets(assets) {
#                 const container = document.getElementById('instances-container');
#                 container.innerHTML = '';

#                 if (assets.length === 0) {
#                     container.innerHTML = `
#                         <div class="empty-state">
#                             <i class="fa-solid fa-server"></i>
#                             <h3>No instances found</h3>
#                             <p>Try refining your search or launch a new cloud instance.</p>
#                         </div>
#                     `;
#                     return;
#                 }

#                 assets.forEach(asset => {
#                     const card = document.createElement('div');
#                     card.className = 'instance-card';
                    
#                     const isRunning = asset.status === 'running';
#                     const isTerminated = asset.status === 'terminated';
#                     const toggleLabel = isRunning ? 'Stop' : 'Start';
#                     const toggleIcon = isRunning ? 'fa-circle-stop' : 'fa-circle-play';

#                     card.innerHTML = `
#                         <div class="card-header">
#                             <div class="instance-title" title="${asset.name}">${asset.name}</div>
#                             <span class="status-badge ${asset.status}">
#                                 ${asset.status}
#                             </span>
#                         </div>
#                         <div class="card-body">
#                             <div class="info-row">
#                                 <span class="info-label">Type</span>
#                                 <span class="info-value">${asset.instance_type}</span>
#                             </div>
#                             <div class="info-row">
#                                 <span class="info-label">Region</span>
#                                 <span class="info-value">${asset.region}</span>
#                             </div>
#                             <div class="info-row">
#                                 <span class="info-label">IP Address</span>
#                                 <span class="info-value">${asset.ip_address || '—'}</span>
#                             </div>
#                         </div>
#                         <div class="card-actions">
#                             <button class="action-btn btn-start-stop" onclick="toggleStatus(${asset.id}, '${asset.status}')" ${isTerminated ? 'disabled' : ''}>
#                                 <i class="fa-solid ${toggleIcon}"></i> ${toggleLabel}
#                             </button>
#                             <button class="action-btn" onclick="openEditModal(${asset.id})">
#                                 <i class="fa-solid fa-pen-to-square"></i> Edit
#                             </button>
#                             <button class="action-btn btn-delete" onclick="deleteAsset(${asset.id})">
#                                 <i class="fa-solid fa-trash-can"></i> Terminate
#                             </button>
#                         </div>
#                     `;
#                     container.appendChild(card);
#                 });
#             }

#             function updateStats(assets) {
#                 const total = assets.length;
#                 const running = assets.filter(a => a.status === 'running').length;
#                 const stopped = assets.filter(a => a.status === 'stopped').length;
#                 const terminated = assets.filter(a => a.status === 'terminated').length;

#                 document.getElementById('stat-total').innerText = total;
#                 document.getElementById('stat-running').innerText = running;
#                 document.getElementById('stat-stopped').innerText = stopped;
#                 document.getElementById('stat-terminated').innerText = terminated;
#             }

#             let searchTimeout;
#             function handleSearch() {
#                 clearTimeout(searchTimeout);
#                 searchTimeout = setTimeout(() => {
#                     const query = document.getElementById('search-input').value;
#                     fetchAssets(query);
#                 }, 200);
#             }

#             // Save Asset (Create / Update)
#             async function saveAsset(event) {
#                 event.preventDefault();
#                 const id = document.getElementById('asset-id').value;
#                 const assetData = {
#                     name: document.getElementById('asset-name').value,
#                     instance_type: document.getElementById('asset-type').value,
#                     region: document.getElementById('asset-region').value,
#                     ip_address: document.getElementById('asset-ip').value || null,
#                     status: document.getElementById('asset-status').value
#                 };

#                 try {
#                     let response;
#                     if (id) {
#                         // Update
#                         response = await fetch(`/api/assets/${id}`, {
#                             method: 'PUT',
#                             headers: { 'Content-Type': 'application/json' },
#                             body: JSON.stringify(assetData)
#                         });
#                     } else {
#                         // Create
#                         response = await fetch('/api/assets', {
#                             method: 'POST',
#                             headers: { 'Content-Type': 'application/json' },
#                             body: JSON.stringify(assetData)
#                         });
#                     }

#                     if (!response.ok) {
#                         const errorDetail = await response.json();
#                         throw new Error(errorDetail.detail || 'Failed to save asset');
#                     }

#                     showToast(id ? 'Instance updated successfully!' : 'New instance launched successfully!', 'success');
#                     closeModal();
#                     fetchAssets();
#                 } catch (error) {
#                     showToast(error.message, 'error');
#                 }
#             }

#             // Quick Toggle Status (Start/Stop)
#             async function toggleStatus(id, currentStatus) {
#                 const nextStatus = currentStatus === 'running' ? 'stopped' : 'running';
#                 try {
#                     const response = await fetch(`/api/assets/${id}`, {
#                         method: 'PUT',
#                         headers: { 'Content-Type': 'application/json' },
#                         body: JSON.stringify({ status: nextStatus })
#                     });
#                     if (!response.ok) throw new Error('Failed to change status');
#                     showToast(`Instance state changed to ${nextStatus}`, 'success');
#                     fetchAssets();
#                 } catch (error) {
#                     showToast(error.message, 'error');
#                 }
#             }

#             // Delete / Terminate Instance
#             async function deleteAsset(id) {
#                 if (!confirm('Are you sure you want to terminate this instance?')) return;
#                 try {
#                     const response = await fetch(`/api/assets/${id}`, {
#                         method: 'DELETE'
#                     });
#                     if (!response.ok) throw new Error('Failed to delete instance');
#                     showToast('Instance terminated successfully', 'success');
#                     fetchAssets();
#                 } catch (error) {
#                     showToast(error.message, 'error');
#                 }
#             }

#             // Modal Handlers
#             function openCreateModal() {
#                 document.getElementById('modal-title').innerText = 'Launch New Instance';
#                 document.getElementById('asset-id').value = '';
#                 document.getElementById('asset-form').reset();
#                 document.getElementById('asset-status').value = 'stopped';
#                 document.getElementById('asset-modal').classList.add('active');
#             }

#             function openEditModal(id) {
#                 const asset = allAssets.find(a => a.id === id);
#                 if (!asset) return;

#                 document.getElementById('modal-title').innerText = `Configure ${asset.name}`;
#                 document.getElementById('asset-id').value = asset.id;
#                 document.getElementById('asset-name').value = asset.name;
#                 document.getElementById('asset-type').value = asset.instance_type;
#                 document.getElementById('asset-region').value = asset.region;
#                 document.getElementById('asset-ip').value = asset.ip_address || '';
#                 document.getElementById('asset-status').value = asset.status;

#                 document.getElementById('asset-modal').classList.add('active');
#             }

#             function closeModal() {
#                 document.getElementById('asset-modal').classList.remove('active');
#             }

#             // Toast feedback
#             function showToast(message, type = 'success') {
#                 const container = document.getElementById('toast-container');
#                 const toast = document.createElement('div');
#                 toast.className = 'toast';
                
#                 const icon = type === 'success' 
#                     ? '<i class="fa-solid fa-circle-check toast-icon success"></i>' 
#                     : '<i class="fa-solid fa-circle-exclamation toast-icon error"></i>';

#                 toast.innerHTML = `
#                     ${icon}
#                     <span>${message}</span>
#                 `;
#                 container.appendChild(toast);
                
#                 // Trigger reflow for slide transition
#                 toast.offsetHeight;
#                 toast.classList.add('active');

#                 setTimeout(() => {
#                     toast.classList.remove('active');
#                     setTimeout(() => toast.remove(), 300);
#                 }, 4000);
#             }

#             // Initial load
#             fetchAssets();
#         </script>
#     </body>
#     </html>
#     """
#     return HTMLResponse(content=html_content)

# if __name__ == "__main__":
#     uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
